#!/usr/bin/env python3
from __future__ import annotations
from typing import Dict, Any, List
from .base import BaseRunner
try:
    import paramiko  # type: ignore
    import requests  # type: ignore
except Exception:
    paramiko = None  # type: ignore
    requests = None  # type: ignore
DETECT_PKG = "bash -lc 'command -v apt >/dev/null && echo apt || command -v dnf >/dev/null && echo dnf || command -v pacman >/dev/null && echo pacman || echo unknown'"
APT_UPGR = "bash -lc 'apt -qq list --upgradable 2>/dev/null | cut -d/ -f1 | sed \"s/\\[upgradable.*//\"'"
DNF_UPGR = "bash -lc 'dnf -q check-update --refresh 2>/dev/null | awk "NR>2 && $1 !~ /^Obsoleting/ && $1 !~ /^Last/ {print $1}"'"
PACMAN_UPGR = "bash -lc 'checkupdates 2>/dev/null | cut -d" " -f1'"
class Runner(BaseRunner):
    def _ssh(self, addr: str, username: str, key_path: str):
        if not paramiko: return None
        c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(addr, username=username, key_filename=key_path, look_for_keys=True, timeout=8)
        return c
    def _pkg_mgr(self, c) -> str:
        try:
            _, out, _ = c.exec_command(DETECT_PKG, timeout=10)
            return out.read().decode().strip() or "unknown"
        except Exception:
            return "unknown"
    def _list_upgrades(self, c, mgr: str) -> List[str]:
        cmd = {'apt': APT_UPGR, 'dnf': DNF_UPGR, 'pacman': PACMAN_UPGR}.get(mgr, "echo")
        pkgs: List[str] = []
        try:
            _, out, _ = c.exec_command(cmd, timeout=20)
            for line in out.read().decode().splitlines():
                t = line.strip()
                if t: pkgs.append(t)
        except Exception as e:
            self.logger.warning(f"Upgrade check failed ({mgr}): {e}")
        return pkgs
    def _osv_lookup(self, pkg: str, mgr: str) -> str:
        if not requests: return "(no OSV)"
        eco = {'apt': 'Debian', 'dnf': 'RPM', 'pacman': 'Alpine'}.get(mgr, 'Debian')
        try:
            r = requests.post("https://api.osv.dev/v1/query", json={"package": {"name": pkg, "ecosystem": eco}}, timeout=10)
            vulns = r.json().get("vulns", [])
            if not vulns: return "no known CVEs"
            ids = ", ".join(v.get("id","?") for v in vulns[:5])
            more = max(0, len(vulns)-5)
            return f"CVEs: {ids}" + (f" (+{more} more)" if more else "")
        except Exception as e:
            self.logger.warning(f"OSV lookup failed for {pkg}: {e}")
            return "(OSV error)"
    def run(self) -> int:
        hosts: List[Dict[str, Any]] = self.globals.get('hosts', []) or []
        username: str = self.globals.get('ssh', {}).get('username', 'cbwinslow')
        key_path: str = self.globals.get('ssh', {}).get('key_path', '~/.ssh/id_ed25519')
        lines: List[str] = ["# CVE Alerts\n"]
        if not hosts: lines.append("(no hosts configured)\n")
        for h in hosts:
            if not paramiko:
                mgr = 'apt'; pkgs = ["openssl","curl","libxml2"]
            else:
                try:
                    c = self._ssh(h['address'], username, key_path)
                    mgr = self._pkg_mgr(c)
                    pkgs = self._list_upgrades(c, mgr)
                    c.close()
                except Exception as e:
                    self.logger.warning(f"SSH error for {h['name']}: {e}")
                    mgr = 'unknown'; pkgs = []
            if not pkgs:
                lines.append(f"- {h['name']}: no upgrades found (mgr={mgr})\n"); continue
            lines.append(f"- {h['name']}: {len(pkgs)} upgradable packages (mgr={mgr})\n")
            for p in pkgs[:10]:
                lines.append(f"  - {p}: {self._osv_lookup(p, mgr)}\n")
        md = "".join(lines)
        out = next((o for o in self.agent['outputs'] if o['type']=='markdown'), None)
        if out: self.emit_markdown(out['path'], md)
        return 0

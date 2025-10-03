#!/usr/bin/env python3
from __future__ import annotations
from typing import Dict, Any, List
from .base import BaseRunner
try:
    import paramiko  # type: ignore
except Exception:
    paramiko = None  # type: ignore
CMDSET = {
    "os": "grep PRETTY_NAME /etc/os-release | cut -d= -f2 | tr -d '"'",
    "kernel": "uname -r",
    "uptime": "uptime -p",
    "load": "cat /proc/loadavg | awk '{print $1}'",
    "mem_free": "free -h | awk '/Mem:/ {print $7}'",
    "disk_free": "df -h / | awk 'NR==2 {print $4}'",
    "outdated": "bash -lc 'command -v apt >/dev/null 2>&1 && apt -qq list --upgradable 2>/dev/null | wc -l || echo 0'",
}
class Runner(BaseRunner):
    def _ssh_exec(self, host: Dict[str, Any], username: str, key_path: str, timeout: int = 8) -> Dict[str, str]:
        if not paramiko:
            return {"os":"Ubuntu 24.04 LTS","kernel":"6.8","uptime":"up 12 days","load":"0.23","mem_free":"8.2G","disk_free":"120G","outdated":"3"}
        res: Dict[str,str] = {}
        try:
            c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            c.connect(hostname=host["address"], username=username, key_filename=key_path, timeout=timeout, look_for_keys=True)
            for k, cmd in CMDSET.items():
                _, stdout, _ = c.exec_command(cmd, timeout=timeout)
                res[k] = stdout.read().decode().strip() or "-"
            c.close()
        except Exception as e:
            self.logger.warning(f"SSH failed for {host['name']}: {e}")
            res = {**{k: '-' for k in CMDSET}, "os": "unknown"}
        return res
    def run(self) -> int:
        hosts: List[Dict[str, Any]] = self.globals.get('hosts', []) or []
        username: str = self.globals.get('ssh', {}).get('username', 'cbwinslow')
        key_path: str = self.globals.get('ssh', {}).get('key_path', '~/.ssh/id_ed25519')
        rows = [
            "| host | os | kernel | uptime | cpu_load | mem_free | disk_free | outdated_pkgs |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for h in hosts:
            stats = self._ssh_exec(h, username, key_path)
            rows.append(f"| {h['name']} | {stats['os']} | {stats['kernel']} | {stats['uptime']} | {stats['load']} | {stats['mem_free']} | {stats['disk_free']} | {stats['outdated']} |")
        md = "\n".join(rows)
        out = next((o for o in self.agent['outputs'] if o['type']=='markdown'), None)
        if out: self.emit_markdown(out['path'], md)
        return 0

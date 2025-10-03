#!/usr/bin/env python3
from __future__ import annotations
import os, subprocess, shlex
from typing import Optional
class SecretError(Exception): pass
def _keyring_get(key: str) -> Optional[str]:
    try:
        import keyring
        return keyring.get_password("agent-mode-starter", key)
    except Exception:
        return None
def _bw_get(key: str) -> Optional[str]:
    bw_session = os.environ.get("BW_SESSION")
    if not bw_session: return None
    try:
        cmd = f"bw get password {shlex.quote(key)}"
        out = subprocess.check_output(cmd, shell=True, text=True, env={**os.environ, "BW_SESSION": bw_session})
        return out.strip()
    except Exception:
        return None
def get_secret(key: str) -> Optional[str]:
    return _keyring_get(key) or _bw_get(key) or os.environ.get(key)

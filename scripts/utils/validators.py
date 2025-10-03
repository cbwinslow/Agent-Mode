#!/usr/bin/env python3
from __future__ import annotations
import os, yaml
from typing import Any, Dict
REQUIRED_AGENT_FIELDS = {"id","version","prompt","outputs","automation"}
class ConfigError(Exception): pass
def load_yaml(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise ConfigError(f"Missing config: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}
def validate_agent_cfg(cfg: Dict[str, Any]) -> None:
    missing = REQUIRED_AGENT_FIELDS - set(cfg.keys())
    if missing: raise ConfigError(f"Agent config missing fields: {sorted(missing)}")
    if not isinstance(cfg.get("outputs"), list) or not cfg["outputs"]:
        raise ConfigError("'outputs' must be a non-empty list")
    if "rrule" not in (cfg.get("automation") or {}):
        raise ConfigError("automation.rrule required (iCal RRULE)")

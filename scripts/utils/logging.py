#!/usr/bin/env python3
from __future__ import annotations
import json, logging, os, re, sys
from datetime import datetime
REDACT_RE = re.compile(r"(api_key|token|password|secret)=([^\s]+)", re.I)
class RedactingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        return REDACT_RE.sub(r"\1=***", msg)
def get_logger(name: str, log_dir: str, level: str = "INFO", json_mode: bool = False) -> logging.Logger:
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger(name); logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    if logger.handlers: return logger
    ts = datetime.now().strftime("%Y%m%d")
    log_path = os.path.join(log_dir, f"{name}-{ts}.log")
    fh = logging.FileHandler(log_path); ch = logging.StreamHandler(sys.stdout)
    if json_mode:
        fmt = logging.Formatter('%(message)s')
        def _json_filter(record: logging.LogRecord):
            record.msg = json.dumps({"ts": datetime.utcnow().isoformat(),"lvl": record.levelname,"name": name,"msg": record.getMessage()})
            return record
        fh.addFilter(_json_filter); ch.addFilter(_json_filter)
    else:
        fmt = RedactingFormatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s')
    fh.setFormatter(fmt); ch.setFormatter(fmt)
    logger.addHandler(fh); logger.addHandler(ch); return logger

#!/usr/bin/env python3
from __future__ import annotations
from typing import Dict, Any
from ..utils.logging import get_logger
from ..utils.io import write_text, write_csv
class BaseRunner:
    def __init__(self, agent_cfg: Dict[str, Any], globals_cfg: Dict[str, Any], dry_run: bool = False):
        self.agent = agent_cfg; self.globals = globals_cfg; self.dry = dry_run
        self.logger = get_logger(agent_cfg['id'], globals_cfg['log_dir'])
    def emit_markdown(self, rel_path: str, content: str) -> None:
        write_text(f"{self.globals['output_dir']}/{rel_path}", content)
        self.logger.info(f"Wrote markdown: {rel_path}")
    def emit_csv(self, rel_path: str, rows):
        write_csv(f"{self.globals['output_dir']}/{rel_path}", rows)
        self.logger.info(f"Wrote csv: {rel_path}")
    def run(self) -> int: raise NotImplementedError

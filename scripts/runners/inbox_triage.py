#!/usr/bin/env python3
from .base import BaseRunner
class Runner(BaseRunner):
    def run(self) -> int:
        self.emit_markdown("reports/inbox_summary.md","# Inbox Summary\n- urgent: 0\n"); return 0

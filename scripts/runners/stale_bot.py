#!/usr/bin/env python3
from .base import BaseRunner
class Runner(BaseRunner):
    def run(self) -> int:
        self.emit_markdown("reports/stale_repos.md","# Stale Repos\n- (none yet)\n"); return 0

#!/usr/bin/env python3
from .base import BaseRunner
class Runner(BaseRunner):
    def run(self) -> int:
        self.emit_markdown("docs/CHANGELOG_draft.md","# Weekly Changelog\n- Example entries\n"); return 0

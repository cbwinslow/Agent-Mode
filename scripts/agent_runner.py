#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib, os, sys
from typing import Any, Dict
from scripts.utils.logging import get_logger
from scripts.utils.validators import load_yaml, validate_agent_cfg, ConfigError
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
RUNNER_MAP = {
    "infra-auditor": "scripts.runners.infra_auditor",
    "port-mapper": "scripts.runners.port_mapper",
    "security-scout": "scripts.runners.security_scout",
    "code-curator": "scripts.runners.code_curator",
    "stale-bot": "scripts.runners.stale_bot",
    "task-syncer": "scripts.runners.task_syncer",
    "ai-researcher": "scripts.runners.ai_researcher",
    "inbox-triage": "scripts.runners.inbox_triage",
}
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", required=True)
    ap.add_argument("--output", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--json-logs", action="store_true")
    ap.add_argument("--since", default=None)
    ap.add_argument("--until", default=None)
    args = ap.parse_args()
    globals_cfg = load_yaml(os.path.join(ROOT, "configs", "globals.yaml"))
    if args.output: globals_cfg["output_dir"] = args.output
    logger = get_logger("agent_runner", globals_cfg["log_dir"], level="DEBUG" if args.verbose else "INFO", json_mode=args.json_logs)
    agent_path = os.path.join(ROOT, "configs", "agents", f"{args.agent}.yaml")
    try:
        agent_cfg = load_yaml(agent_path); validate_agent_cfg(agent_cfg)
    except ConfigError as e:
        logger.error(f"Config error: {e}"); return 2
    mod_name = RUNNER_MAP.get(args.agent)
    if not mod_name:
        logger.error(f"No runner module for agent {args.agent}"); return 3
    try:
        mod = importlib.import_module(mod_name)
        runner = mod.Runner(agent_cfg, globals_cfg, dry_run=args.dry_run)
        return runner.run()
    except Exception as e:
        logger.exception(f"Runner failed: {e}"); return 1
if __name__ == "__main__":
    sys.exit(main())

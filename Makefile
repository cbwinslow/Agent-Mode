.PHONY: validate dryrun run install scan serve

install:
	pip install uv || python -m pip install uv
	uv venv
	uv pip install -e .

validate:
	python -m py_compile $(shell git ls-files '*.py') || true
	python - <<'PY'
import yaml, glob
for p in glob.glob('configs/agents/*.yaml'):
    with open(p) as f:
        yaml.safe_load(f)
print('YAML OK')
PY

dryrun:
	python -m scripts.agent_runner --agent infra-auditor --dry-run --verbose || true
	python -m scripts.agent_runner --agent port-mapper --dry-run || true
	python -m scripts.agent_runner --agent security-scout --dry-run || true

run:
	python -m scripts.agent_runner --agent $(AGENT) --verbose

scan:
	python -m scripts.agent_runner --agent port-mapper --verbose

serve:
	uvicorn scripts.server:app --host 0.0.0.0 --port 8787

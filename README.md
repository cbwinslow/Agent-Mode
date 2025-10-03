# Agent Mode Starter Library (CBW) — v0.2.0

New in this release:
- OS autodetect (apt/dnf/pacman) in `security-scout` with OSV CVE hints
- Secure secrets: OS keyring first, Bitwarden CLI fallback, then env
- FastAPI dashboard: browse reports/logs and trigger runs

## Quickstart
pyenv install -s 3.10.14 && pyenv local 3.10.14
make install
make validate
make dryrun
# Optional dashboard
make serve   # http://localhost:8787

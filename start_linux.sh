#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
fi
if [[ ! -f .env ]]; then
  cp .env.example .env
fi
.venv/bin/python -m pip install -r backend/requirements.txt
export PYTHONPATH=backend
.venv/bin/python scripts/backup_safety.py before-local-migration --directory backups
.venv/bin/python -m alembic -c backend/alembic.ini upgrade head
echo 'OSMANX OMNICHAT: open http://127.0.0.1:8000 and select Demo Mode'
exec .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

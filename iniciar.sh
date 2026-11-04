#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -f frontend/dist/index.html ]; then
  if ! command -v npm >/dev/null 2>&1; then
    printf '%s\n' 'Instale Node 22 ou superior para compilar a interface na primeira execução.'
    exit 1
  fi
  npm --prefix frontend ci
  npm run build
fi
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install -r requirements-verificado.txt
printf '%s\n' 'Abra http://localhost:8000. Para encerrar: Ctrl+C.'
exec .venv/bin/python -m uvicorn api.main:app --host 127.0.0.1 --port 8000

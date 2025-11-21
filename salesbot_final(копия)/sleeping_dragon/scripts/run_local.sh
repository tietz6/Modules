#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1
export UVICORN_WORKERS=${UVICORN_WORKERS:-1}
export PORT=${PORT:-8080}
echo "[run_local] starting uvicorn on :$PORT"
python -m uvicorn startup:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 30

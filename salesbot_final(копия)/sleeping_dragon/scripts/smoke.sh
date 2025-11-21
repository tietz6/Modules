#!/usr/bin/env bash
set -e
BASE=${1:-http://127.0.0.1:8080}
echo "[smoke] ping"
curl -sSf $BASE/api/public/v1/ping >/dev/null
echo "[smoke] health"
curl -sSf $BASE/api/public/v1/health >/dev/null
echo "[smoke] routes summary"
curl -sSf $BASE/api/public/v1/routes_summary >/dev/null || true
echo "[smoke] mini brand"
curl -sSf $BASE/mini/brand/health >/dev/null
echo "[smoke] voice llm"
curl -sSf -H "Content-Type: application/json" -d '{"messages":[{"role":"user","content":"Привет!"}]}' $BASE/voice/v1/llm/chat >/dev/null || true
echo "[smoke] sleeping dragon"
curl -sSf $BASE/sleeping_dragon/v4/health >/dev/null || true
echo "[ok] all checks passed (or optional routes skipped)"

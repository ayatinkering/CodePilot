#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
if [[ ! -x .venv/bin/codepilot || ! -f frontend/dist/index.html ]]; then
  echo 'First run: uv sync --locked && npm ci --prefix frontend && npm run build --prefix frontend' >&2
  exit 1
fi
.venv/bin/python - <<'PY'
from codepilot.config import Settings
from codepilot.retrieval import REVISION
import subprocess
s=Settings()
assert (s.data_dir/'models'/REVISION/'model_optimized.onnx').is_file(), 'Run: .venv/bin/codepilot prepare-model'
assert s.runner_image.startswith('sha256:'), 'Set CODEPILOT_RUNNER_IMAGE in .env; see README'
subprocess.run(['docker','image','inspect',s.runner_image],check=True,stdout=subprocess.DEVNULL)
PY
.venv/bin/codepilot prepare-demo >/dev/null
.venv/bin/codepilot worker &
worker_pid=$!
.venv/bin/codepilot serve &
server_pid=$!
cleanup() { kill "$worker_pid" "$server_pid" 2>/dev/null || true; wait "$worker_pid" "$server_pid" 2>/dev/null || true; }
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
echo 'CodePilot: http://127.0.0.1:8000 — Ctrl-C stops this worker and server.'
wait -n "$worker_pid" "$server_pid"

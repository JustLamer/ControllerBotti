#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ -x ".venv/bin/python" ]]; then
  .venv/bin/python main.py "$@"
else
  python3 main.py "$@"
fi

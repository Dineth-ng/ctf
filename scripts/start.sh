#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/build_lab.py
docker compose up -d --build --wait ctfd stage1-web stage4-web
python3 scripts/health_check.py

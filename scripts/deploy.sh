#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker info >/dev/null
docker compose version >/dev/null
./scripts/preflight.sh
python3 scripts/init_env.py
docker compose up -d --build --wait --wait-timeout 240
python3 scripts/setup_ctfd.py
printf '\nCTFd: http://localhost:8000 | Admin: http://localhost:8000/admin\nCredentials: .local/admin-credentials.txt\nOSINT: http://localhost | Portal: http://localhost:8080 | SSH: localhost:2222\n'

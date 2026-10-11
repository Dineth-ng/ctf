#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose stop
echo 'Stopped containers; database volumes and CTFd scores were kept.'

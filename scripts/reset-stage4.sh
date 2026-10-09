#!/usr/bin/env bash
# Reseed only the Stage 4 challenge database and remove active web sessions.
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose exec -T stage4-db sh -c \
  'MYSQL_PWD="$MYSQL_PASSWORD" exec mysql -u "$MYSQL_USER" "$MYSQL_DATABASE"' \
  < challenges/stage4-web/database/init.sql
docker compose up -d --no-deps --force-recreate --wait stage4-web
printf 'Stage 4 database and web sessions reset.\n'

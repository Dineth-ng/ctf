#!/usr/bin/env bash
# Reset challenge state only. CTFd users, uploads, and scores remain intact.
set -euo pipefail
cd "$(dirname "$0")/.."
case "${1:-challenges}" in
  challenges)
    docker compose exec -T stage4_db sh -c 'exec mariadb -u root -p"$MARIADB_ROOT_PASSWORD" -e "DROP DATABASE IF EXISTS portal_db;"'
    docker compose exec -T stage4_db sh -c 'exec mariadb -u root -p"$MARIADB_ROOT_PASSWORD"' < stage4_web/db/init.sql
    docker compose up -d --force-recreate --wait --wait-timeout 120 stage1_2_web stage4_web stage6_vault
    docker compose restart gateway
    printf 'Challenge database and containers restored. CTFd accounts and scores preserved.\n'
    ;;
  *) printf 'Usage: %s [challenges]\n' "$0" >&2; exit 2 ;;
esac

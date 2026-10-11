#!/usr/bin/env bash
# Report conflicting Docker containers before the gateway tries to bind host ports.
set -euo pipefail
ports=(80 8000 8080 2222)
blocked=0
for port in "${ports[@]}"; do
  while IFS= read -r container; do
    [[ -z "$container" ]] && continue
    # The current gateway already owns these ports on repeat deployments.
    [[ "$container" == 'nighthawk-member1-gateway-1' ]] && continue
    printf 'Port %s is already published by Docker container: %s\n' "$port" "$container" >&2
    blocked=1
  done < <(docker ps --filter "publish=${port}" --format '{{.Names}}')
done
if (( blocked )); then
  printf '\nStop only the old lab containers listed above, then run ./scripts/deploy.sh again. This project needs ports 80, 8000, 8080, and 2222.\n' >&2
  exit 1
fi
printf 'No conflicting Docker containers found for gateway ports 80, 8000, 8080, and 2222.\n'

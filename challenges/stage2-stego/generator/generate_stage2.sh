#!/bin/bash

set -e

if [ -z "$1" ]; then
    echo "Usage:"
    echo "./solve_stage2.sh <stego-image> [password]"
    exit 1
fi

IMAGE="$1"
PASSWORD="${2:-NC-RD-7741}"

TEMP_DIR=$(mktemp -d)
OUTPUT="$TEMP_DIR/hidden-note.txt"

echo "[+] Analysing:"
echo "$IMAGE"

steghide extract \
    -sf "$IMAGE" \
    -p "$PASSWORD" \
    -xf "$OUTPUT"

echo
echo "[+] Hidden content:"
cat "$OUTPUT"

echo
echo "[+] Searching for NightHawk flag..."

grep -o 'NH{[^}]*}' "$OUTPUT" || true

rm -rf "$TEMP_DIR"
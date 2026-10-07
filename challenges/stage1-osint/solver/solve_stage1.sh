#!/bin/bash

set -e

if [ -z "$1" ]; then

    echo "Usage:"
    echo "./solve_stage1.sh <image>"

    exit 1

fi


IMAGE="$1"


if [ ! -f "$IMAGE" ]; then

    echo "[-] File not found:"
    echo "$IMAGE"

    exit 1

fi


echo "[+] Analysing:"
echo "$IMAGE"


FLAG=$(exiftool "$IMAGE" | grep -o 'NH{[^}]*}' | head -n 1)


if [ -z "$FLAG" ]; then

    echo "[-] No NightHawk flag found."

    exit 1
fi


echo "[+] Flag discovered:"
echo "$FLAG"

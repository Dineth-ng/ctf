#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

IMAGE="$SCRIPT_DIR/../website/assets/images/conference-2026.jpg"

FLAG="NH{metadata_exposure_confirmed}"

ARCHIVE_REF="NC-RD-7741"

PROJECT="PROMETHEUS"


echo "=========================================="
echo " Operation NightHawk"
echo " Stage 1 - The Digital Footprint"
echo "=========================================="


if [ ! -f "$IMAGE" ]; then

    echo "[-] Challenge image not found:"
    echo "$IMAGE"

    exit 1

fi


echo "[+] Cleaning previous challenge metadata"


exiftool \
-overwrite_original \
-Artist= \
-Description= \
-Comment= \
"$IMAGE" \
> /dev/null


echo "[+] Writing NexaCore metadata"


exiftool \
-overwrite_original \
-Artist="NexaCore Communications Team" \
-Copyright="NexaCore Dynamics 2026" \
-Description="CyberTech Asia 2026 Research Division Photo" \
-Comment="ArchiveRef=$ARCHIVE_REF | InternalProject=$PROJECT | $FLAG" \
"$IMAGE" \
> /dev/null


echo "[+] Verifying metadata"


exiftool "$IMAGE" | \
grep -E "Artist|Description|Comment"


echo
echo "[+] Stage 1 generated successfully."
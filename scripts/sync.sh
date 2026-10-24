#!/usr/bin/env bash
# Copies the shared module (common/) into every Fase Groove product as
# ThirdParty/fasegroove-common/, replacing the previous copy (files removed here go there too).
# Usage: scripts/sync.sh [product repo ...]   (default: the sibling repos of this one)
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
products=("$@")
if [ ${#products[@]} -eq 0 ]; then
    for name in fasegroovepiano fasegroovedrums fasegrooveguitar fasegroovearranger; do
        [ -d "$here/../$name" ] && products+=("$here/../$name")
    done
fi
for repo in "${products[@]}"; do
    dest="$repo/ThirdParty/fasegroove-common"
    rm -rf "$dest"
    mkdir -p "$dest"
    cp -R "$here/common/." "$dest/"
    echo "synced $(basename "$(cd "$repo" && pwd)")"
done

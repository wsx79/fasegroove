#!/usr/bin/env bash
# Copies the shared module (common/) into every Fase Groove product as
# ThirdParty/fasegroove-common/, replacing the previous copy (files removed here go there too).
# Usage: scripts/sync.sh [product repo ...]   (default: the sibling repos of this one)
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
products=("$@")
if [ ${#products[@]} -eq 0 ]; then
    for name in fasegroovepiano fasegroovedrums fasegrooveguitar fasegroovearranger fasegroovelead; do
        [ -d "$here/../$name" ] && products+=("$here/../$name")
    done
fi
# A lock identifies committed sources, never an uncommitted working copy.
if [ -n "$(git -C "$here" status --porcelain --untracked-files=all -- common)" ]; then
    echo "Commit common/ before syncing a pinned module." >&2
    exit 1
fi
for repo in "${products[@]}"; do
    dest="$repo/ThirdParty/fasegroove-common"
    rm -rf "$dest"
    mkdir -p "$dest"
    cp -R "$here/common/." "$dest/"
    python3 "$here/common/VerifyModule.py" --module "$dest" --canonical "$here" --write-lock
    echo "synced $(basename "$(cd "$repo" && pwd)")"
done

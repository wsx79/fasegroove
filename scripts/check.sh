#!/usr/bin/env bash
# Reports every product whose ThirdParty/fasegroove-common/ differs from common/.
# Exit status 1 when one is out of sync (run scripts/sync.sh to fix it).
set -uo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
products=("$@")
if [ ${#products[@]} -eq 0 ]; then
    for name in fasegroovepiano fasegroovedrums fasegrooveguitar fasegroovearranger fasegroovelead; do
        [ -d "$here/../$name" ] && products+=("$here/../$name")
    done
fi
status=0
for repo in "${products[@]}"; do
    name="$(basename "$(cd "$repo" && pwd)")"
    dest="$repo/ThirdParty/fasegroove-common"
    if [ ! -d "$dest" ]; then
        echo "MISSING  $name"; status=1; continue
    fi
    if out="$(diff -rq "$here/common" "$dest")"; then
        if python3 "$here/common/VerifyModule.py" --module "$dest"; then
            echo "in sync  $name"
        else
            status=1
        fi
    else
        echo "DIFFERS  $name"; echo "$out" | sed 's/^/    /'; status=1
    fi
done
exit $status

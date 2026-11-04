#!/bin/bash
# Zabalí mod do ~/.factorio/mods/cozy-farm_<verze>.zip (verze z info.json) a smaže starší verze.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VER=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['version'])" "$ROOT/cozy-farm/info.json")
OUT="${1:-$HOME/.factorio/mods}"
TMP=$(mktemp -d)
cp -r "$ROOT/cozy-farm" "$TMP/cozy-farm_$VER"
find "$OUT" -maxdepth 1 -name 'cozy-farm_*.zip' ! -name "cozy-farm_$VER.zip" -delete
rm -f "$OUT/cozy-farm_$VER.zip"
(cd "$TMP" && zip -qr "$OUT/cozy-farm_$VER.zip" "cozy-farm_$VER")
rm -rf "$TMP"
echo "$OUT/cozy-farm_$VER.zip"

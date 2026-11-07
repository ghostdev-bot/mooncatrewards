#!/bin/bash
# Rebuild data (incremental, ~2-5 Helius credits per run unless new txs) and redeploy to surge.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .cache
python3 scripts/build.py 2>>.cache/refresh.log
SURGE_LOGIN="$(jq -r .email /home/box/secrets/surge.json)" SURGE_TOKEN="$(jq -r .token /home/box/secrets/surge.json)" npx --yes surge@0.53.0 site mooncatrewards.surge.sh >/dev/null
echo "refreshed + deployed $(date -u +%FT%TZ)"

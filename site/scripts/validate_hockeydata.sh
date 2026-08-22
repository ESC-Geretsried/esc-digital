#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PAGE="$ROOT/site/public/river-rats/index.html"
CFG="$ROOT/content/river-rats/hockeydata.json"

test -f "$PAGE"
test -f "$CFG"
grep -q 'hockeydata.los.GameSlider' "$PAGE"
grep -q 'hockeydata.los.Schedule' "$PAGE"
grep -q 'hockeydata.los.Standings' "$PAGE"
grep -q 'bevbyl_sen_vr' "$PAGE"
grep -q '"team_id": 13305' "$CFG"
grep -q '"division_id": 21620' "$CFG"
if grep -q '__HOCKEYDATA_API_KEY__' "$PAGE"; then
  echo 'ERROR: HockeyData API key placeholder leaked into output' >&2
  exit 2
fi
if grep -q 'HOCKEYDATA_API_KEY' "$CFG"; then
  echo 'ERROR: secret reference must not be stored in tenant content config' >&2
  exit 2
fi
echo 'HockeyData integration structure validated'

#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PAGE="$ROOT/site/public/river-rats/index.html"
CFG="$ROOT/content/river-rats/hockeydata.json"

require_file(){ test -f "$1" || { echo "ERROR: missing $1" >&2; exit 2; }; }
require_fixed(){ grep -Fq "$2" "$1" || { echo "ERROR: expected '$2' missing from $1" >&2; exit 2; }; }

require_file "$PAGE"
require_file "$CFG"
require_fixed "$PAGE" 'hockeydata.los.GameSlider'
require_fixed "$PAGE" 'hockeydata.los.Schedule'
require_fixed "$PAGE" 'hockeydata.los.Standings'
require_fixed "$PAGE" 'bevbyl_sen_vr'
require_fixed "$CFG" '"team_id": 13305'
require_fixed "$CFG" '"division_id": 21620'
if grep -Fq '__HOCKEYDATA_API_KEY__' "$PAGE"; then
  echo 'ERROR: HockeyData API key placeholder leaked into output' >&2
  exit 2
fi
if grep -Fq 'HOCKEYDATA_API_KEY' "$CFG"; then
  echo 'ERROR: secret reference must not be stored in tenant content config' >&2
  exit 2
fi
echo 'HockeyData integration structure validated'

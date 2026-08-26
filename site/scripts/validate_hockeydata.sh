#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PAGE="$ROOT/site/public/river-rats/index.html"
CFG="$ROOT/content/river-rats/hockeydata.json"
TEAM="$ROOT/content/river-rats/team.json"

require_file(){ test -f "$1" || { echo "ERROR: missing $1" >&2; exit 2; }; }
require_fixed(){ grep -Fq "$2" "$1" || { echo "ERROR: expected '$2' missing from $1" >&2; exit 2; }; }

require_file "$PAGE"
require_file "$CFG"
require_file "$TEAM"
require_fixed "$PAGE" 'hockeydata.los.GameSlider'
require_fixed "$PAGE" 'hockeydata.los.Schedule'
require_fixed "$PAGE" 'hockeydata.los.Standings'
require_fixed "$PAGE" 'bevbyl_sen_vr'
require_fixed "$PAGE" 'href="#uebersicht"'
require_fixed "$PAGE" 'href="#teamfoto"'
require_fixed "$PAGE" 'href="#mannschaft"'
require_fixed "$PAGE" 'href="#news"'
require_fixed "$PAGE" 'href="#spielplan"'
require_fixed "$PAGE" 'href="#tabelle"'
require_fixed "$PAGE" 'href="#ergebnisse"'
require_fixed "$PAGE" 'id="teamfoto"'
require_fixed "$PAGE" 'id="ergebnisse"'
require_fixed "$PAGE" 'Nächstes Spiel'
BASE_PATH="$(python3 -c 'import sys; from urllib.parse import urlsplit; print(urlsplit(sys.argv[1]).path.rstrip("/"))' "${HUGO_BASEURL:-/}")"
require_fixed "$PAGE" "src=\"$BASE_PATH/images/hero/hero-02-team.jpeg\""
require_fixed "$PAGE" "href=\"$BASE_PATH/aktuelles/\""
require_fixed "$TEAM" '"team_photo": "images/hero/hero-02-team.jpeg"'
require_fixed "$CFG" '"team_id": 13305'
require_fixed "$CFG" '"division_id": 21620'
python3 - "$PAGE" <<'PY'
import re
import sys
from pathlib import Path

html = Path(sys.argv[1]).read_text(encoding='utf-8')
section_ids = re.findall(r'<section[^>]+id="([^"]+)"', html)
expected = ['uebersicht', 'teamfoto', 'mannschaft', 'news', 'spielplan', 'tabelle', 'ergebnisse']
if section_ids != expected:
    raise SystemExit(f'ERROR: River Rats section order is {section_ids!r}, expected {expected!r}')
nav_ids = re.findall(r'<a href="#([^"]+)">', html)
if nav_ids != expected:
    raise SystemExit(f'ERROR: River Rats navigation order is {nav_ids!r}, expected {expected!r}')
if html.count('hockeydata.los.GameSlider') != 1 or html.count('hockeydata.los.Standings') != 1 or html.count('hockeydata.los.Schedule') != 2:
    raise SystemExit('ERROR: HockeyData widget structure changed unexpectedly')
PY
if grep -Fq '__HOCKEYDATA_API_KEY__' "$PAGE"; then
  echo 'ERROR: HockeyData API key placeholder leaked into output' >&2
  exit 2
fi
if grep -Fq 'HOCKEYDATA_API_KEY' "$CFG"; then
  echo 'ERROR: secret reference must not be stored in tenant content config' >&2
  exit 2
fi
echo 'River Rats team page and HockeyData integration structure validated'

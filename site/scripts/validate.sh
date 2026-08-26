#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="$ROOT/site/public"
INDEX="$OUT/index.html"
SPONSOR_DATA="$ROOT/content/sponsors/sponsors.json"
SPONSOR_ASSETS="$ROOT/content/sponsors/assets"
SPONSOR_MANIFEST="$ROOT/docs/operations/sponsor-assets.sha256"
TEAM_MANIFEST="$ROOT/docs/operations/esc-int-team-assets.sha256"
HOME_DATA="$ROOT/content/home/home.json"
PAGE_MANIFEST="$ROOT/docs/operations/esc-int-pages-manifest.json"

require_file(){ test -f "$1" || { echo "ERROR: missing generated file $1" >&2; exit 2; }; }
require_text(){ grep -q "$2" "$1" || { echo "ERROR: expected text '$2' missing from $1" >&2; exit 2; }; }

require_file "$INDEX"
python3 "$ROOT/scripts/sync_founder_team_rosters.py"
python3 "$ROOT/site/scripts/test_news_retention.py"
grep -qi '<!doctype html>' "$INDEX"
require_text "$INDEX" 'Eishockey\. Gemeinschaft\. Geretsried\.'
require_text "$INDEX" 'data-hero-source'
require_text "$INDEX" 'images/teams/eislaufschule-2025-2026.png'
require_text "$INDEX" 'images/teams/inklusion.jpg'
require_text "$INDEX" 'noindex,nofollow,noarchive'
require_text "$INDEX" 'Unsere Partner'
require_text "$INDEX" 'Aktuelles'
require_text "$INDEX" 'Doppelpack für die Defensive'
require_text "$INDEX" 'U20 gegen SG Bad Aibling/Inzell'
require_text "$INDEX" 'Nächste Termine'
require_text "$INDEX" 'Werde Teil der River Rats'
require_text "$INDEX" 'Mitmachen im Ehrenamt'
require_text "$INDEX" 'team-page\.min\.'

(
  cd "$SPONSOR_ASSETS"
  sha256sum -c "$SPONSOR_MANIFEST"
)
(
  cd "$ROOT"
  sha256sum -c "$TEAM_MANIFEST"
)

test "$(find "$OUT/images/teams" -maxdepth 1 -type f | wc -l)" -eq 11 || { echo 'ERROR: expected 11 published team assets' >&2; exit 2; }
test "$(find "$OUT/images/people/river-rats/players" -maxdepth 1 -type f | wc -l)" -eq 11 || { echo 'ERROR: expected 11 published player photos' >&2; exit 2; }
test "$(find "$OUT/images/people/river-rats/staff" -maxdepth 1 -type f | wc -l)" -eq 9 || { echo 'ERROR: expected 9 published River Rats staff photos' >&2; exit 2; }
for path in sponsoren river-rats river-rats-damen nachwuchs eislaufschule eiskunstlauf inklusion verein verein/vereinsfuehrung verein/foerderverein impressum datenschutz; do require_file "$OUT/$path/index.html"; done
require_text "$OUT/aktuelles/2026-08-04-river-rats-defensive-verlaengerungen/index.html" 'Doppelpack für die Defensive'
require_text "$OUT/sponsoren/index.html" 'Ansprechpartner Sponsoring'
require_text "$OUT/verein/vereinsfuehrung/index.html" 'Thomas Gania'
require_text "$OUT/verein/vereinsfuehrung/index.html" 'Romy Schiek'
if grep -q 'Markus Hätinen' "$OUT/verein/vereinsfuehrung/index.html"; then
  echo 'ERROR: excluded former Vereinsführung record is publicly rendered' >&2
  exit 2
fi
test "$(find "$OUT/images/people/vereinsfuehrung" -maxdepth 1 -type f | wc -l)" -eq 8 || { echo 'ERROR: expected 8 published Vereinsführung portraits' >&2; exit 2; }
(
  cd "$ROOT"
  sha256sum -c docs/operations/vereinsfuehrung-portraits.sha256
)

python3 - "$SPONSOR_DATA" "$HOME_DATA" "$PAGE_MANIFEST" "$INDEX" "$OUT/sponsors/assets" <<'PY'
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

sponsor_path, home_path, page_manifest_path, index_path, public_assets = map(Path, sys.argv[1:])
data = json.loads(sponsor_path.read_text(encoding='utf-8'))
home = json.loads(home_path.read_text(encoding='utf-8'))
page_manifest = json.loads(page_manifest_path.read_text(encoding='utf-8'))
sponsors = data['sponsors']
if len(sponsors) != 37:
    raise SystemExit(f'ERROR: expected 37 sponsors, got {len(sponsors)}')
ids = [s['id'] for s in sponsors]
if len(ids) != len(set(ids)):
    raise SystemExit('ERROR: duplicate sponsor ids')
for sponsor in sponsors:
    if not sponsor.get('visible'):
        raise SystemExit(f"ERROR: approved sponsor unexpectedly hidden: {sponsor['id']}")
    logo = sponsor.get('logo')
    if not logo or sponsor.get('logo_status') != 'accepted_tenant_copy':
        raise SystemExit(f"ERROR: sponsor lacks accepted tenant logo: {sponsor['id']}")
    if not (public_assets / Path(logo).name).is_file():
        raise SystemExit(f"ERROR: published logo missing: {sponsor['id']}")

if len(home.get('news_groups', [])) != 5:
    raise SystemExit('ERROR: expected five esc-int homepage news groups')
if len(home.get('events', [])) != 3:
    raise SystemExit('ERROR: expected three esc-int event placeholders')
if len(home.get('community', [])) != 4:
    raise SystemExit('ERROR: expected four esc-int community actions')
if home.get('source', {}).get('repository') != 'open-reference-platform/esc-int':
    raise SystemExit('ERROR: homepage provenance missing esc-int source')
if len(page_manifest.get('pages', [])) < 20:
    raise SystemExit('ERROR: frozen esc-int page snapshot unexpectedly small')

class PageHTML(HTMLParser):
    def __init__(self):
        super().__init__(); self.current_anchor=None; self.anchors=[]; self.sponsor_img_srcs=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='a': self.current_anchor={'href':attrs.get('href'),'target':attrs.get('target'),'text':''}
        if tag=='img' and '/sponsors/assets/' in (attrs.get('src') or ''): self.sponsor_img_srcs.append(attrs.get('src'))
    def handle_data(self, data):
        if self.current_anchor is not None: self.current_anchor['text'] += data
    def handle_endtag(self, tag):
        if tag=='a' and self.current_anchor is not None:
            self.current_anchor['text']=' '.join(self.current_anchor['text'].split()); self.anchors.append(self.current_anchor); self.current_anchor=None

html=index_path.read_text(encoding='utf-8')
if 'https://www.esc-geretsried.de/static/' in html:
    raise SystemExit('ERROR: runtime logo hotlink remains in generated HTML')
parser=PageHTML(); parser.feed(html)
if len({Path(src).name for src in parser.sponsor_img_srcs}) != 37:
    raise SystemExit('ERROR: sponsor band asset count changed')
def anchors_with_text(text): return [a for a in parser.anchors if a['text']==text]
kolbeck=anchors_with_text('Kolbeck Hightech-Logistik GmbH')
if len(kolbeck)!=1 or kolbeck[0]['href']!='https://spedition-kolbeck.de/' or kolbeck[0]['target']!='_blank':
    raise SystemExit('ERROR: Kolbeck direct-link behavior is incorrect')
if anchors_with_text('Krämmel'):
    raise SystemExit('ERROR: sponsor without verified URL must not be clickable')
all_sponsors=anchors_with_text('Alle Sponsoren →')
if len(all_sponsors)!=1 or not all_sponsors[0]['href'].endswith('/sponsoren/') or all_sponsors[0]['target'] is not None:
    raise SystemExit('ERROR: Alle Sponsoren must route internally without new tab')
PY

if grep -RInE '(BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})' "$OUT"; then
  echo "ERROR: credential-like material found in generated output" >&2
  exit 3
fi

if grep -RIl 'orp-esc-int.netlify.app' "$OUT"; then
  echo "ERROR: Netlify runtime dependency leaked into generated output" >&2
  exit 4
fi

python3 "$ROOT/site/scripts/validate_public_copy.py" "$OUT"

echo "Static smoke validation passed with structured navigation, curated photo-first heroes, canonical routes, internal sponsors page and transitional esc-int content"

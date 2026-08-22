#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="$ROOT/site/public"
INDEX="$OUT/index.html"
SPONSOR_DATA="$ROOT/content/sponsors/sponsors.json"
SPONSOR_ASSETS="$ROOT/content/sponsors/assets"
SPONSOR_MANIFEST="$ROOT/docs/operations/sponsor-assets.sha256"
HOME_DATA="$ROOT/content/home/home.json"

test -f "$INDEX" || { echo "ERROR: missing $INDEX" >&2; exit 2; }
grep -qi '<!doctype html>' "$INDEX"
grep -q 'Leidenschaft\.' "$INDEX"
grep -q 'Team\. Zukunft\.' "$INDEX"
grep -q 'noindex,nofollow,noarchive' "$INDEX"
grep -q 'Unsere Partner' "$INDEX"
grep -q 'Aktuelles' "$INDEX"
grep -q 'Doppelpack für die Defensive' "$INDEX"
grep -q 'Goldener Puck für Alexandra Boico' "$INDEX"
grep -q 'U20 gegen SG Bad Aibling/Inzell' "$INDEX"
grep -q 'Nächste Termine' "$INDEX"
grep -q 'Werde Teil der River Rats' "$INDEX"
grep -q 'Mitmachen im Ehrenamt' "$INDEX"

(
  cd "$SPONSOR_ASSETS"
  sha256sum -c "$SPONSOR_MANIFEST"
)

python3 - "$SPONSOR_DATA" "$HOME_DATA" "$INDEX" "$OUT/sponsors/assets" <<'PY'
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

sponsor_path, home_path, index_path, public_assets = map(Path, sys.argv[1:])
data = json.loads(sponsor_path.read_text(encoding='utf-8'))
home = json.loads(home_path.read_text(encoding='utf-8'))
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
if len(all_sponsors)!=1 or all_sponsors[0]['href']!=data['all_sponsors_url'] or all_sponsors[0]['target']!='_blank':
    raise SystemExit('ERROR: Alle Sponsoren link behavior is incorrect')
PY

if grep -RInE '(BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})' "$OUT"; then
  echo "ERROR: credential-like material found in generated output" >&2
  exit 3
fi

echo "Static smoke validation passed with esc-int homepage modules and unchanged canonical sponsor band"

#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="$ROOT/site/public"
INDEX="$OUT/index.html"
SPONSOR_DATA="$ROOT/content/sponsors/sponsors.json"
SPONSOR_ASSETS="$ROOT/content/sponsors/assets"
SPONSOR_MANIFEST="$ROOT/docs/operations/sponsor-assets.sha256"

test -f "$INDEX" || { echo "ERROR: missing $INDEX" >&2; exit 2; }
grep -qi '<!doctype html>' "$INDEX"
grep -q 'Leidenschaft\.' "$INDEX"
grep -q 'Team\. Zukunft\.' "$INDEX"
grep -q 'noindex,nofollow,noarchive' "$INDEX"
grep -q 'Unsere Partner' "$INDEX"

(
  cd "$SPONSOR_ASSETS"
  sha256sum -c "$SPONSOR_MANIFEST"
)

python3 - "$SPONSOR_DATA" "$INDEX" "$OUT/sponsors/assets" <<'PY'
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

data_path, index_path, public_assets = map(Path, sys.argv[1:])
data = json.loads(data_path.read_text(encoding='utf-8'))
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
    if not Path(logo).name:
        raise SystemExit(f"ERROR: invalid logo path: {sponsor['id']}")
    if not (public_assets / Path(logo).name).is_file():
        raise SystemExit(f"ERROR: published logo missing: {sponsor['id']}")

class SponsorHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_anchor = None
        self.anchors = []
        self.sponsor_img_srcs = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a':
            self.current_anchor = {'href': attrs.get('href'), 'target': attrs.get('target'), 'text': ''}
        if tag == 'img' and '/sponsors/assets/' in (attrs.get('src') or ''):
            self.sponsor_img_srcs.append(attrs.get('src'))
    def handle_data(self, data):
        if self.current_anchor is not None:
            self.current_anchor['text'] += data
    def handle_endtag(self, tag):
        if tag == 'a' and self.current_anchor is not None:
            self.current_anchor['text'] = ' '.join(self.current_anchor['text'].split())
            self.anchors.append(self.current_anchor)
            self.current_anchor = None

html = index_path.read_text(encoding='utf-8')
if 'https://www.esc-geretsried.de/static/' in html:
    raise SystemExit('ERROR: runtime logo hotlink remains in generated HTML')
parser = SponsorHTML(); parser.feed(html)
unique_logo_names = {Path(src).name for src in parser.sponsor_img_srcs}
if len(unique_logo_names) != 37:
    raise SystemExit(f'ERROR: expected 37 unique rendered sponsor logos, got {len(unique_logo_names)}')

def anchors_with_text(text):
    return [a for a in parser.anchors if a['text'] == text]

kolbeck = anchors_with_text('Kolbeck Hightech-Logistik GmbH')
if len(kolbeck) != 1 or kolbeck[0]['href'] != 'https://spedition-kolbeck.de/' or kolbeck[0]['target'] != '_blank':
    raise SystemExit('ERROR: Kolbeck direct-link behavior is incorrect')
if anchors_with_text('Krämmel'):
    raise SystemExit('ERROR: sponsor without verified URL must not be clickable')
all_sponsors = anchors_with_text('Alle Sponsoren →')
if len(all_sponsors) != 1 or all_sponsors[0]['href'] != data['all_sponsors_url'] or all_sponsors[0]['target'] != '_blank':
    raise SystemExit('ERROR: Alle Sponsoren link behavior is incorrect')
PY

if grep -RInE '(BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})' "$OUT"; then
  echo "ERROR: credential-like material found in generated output" >&2
  exit 3
fi

echo "Static smoke validation passed with 37 canonical sponsor assets"

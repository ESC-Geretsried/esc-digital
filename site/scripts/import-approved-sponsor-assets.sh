#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ASSET_DIR="$ROOT/content/sponsors/assets"
DATA_FILE="$ROOT/content/sponsors/sponsors.json"
mkdir -p "$ASSET_DIR"

# Founder-approved roster/source: https://www.esc-geretsried.de/sponsoring/
# Source URLs are the logo URLs already preserved in the prior esc-int reference build.
read -r -d '' SOURCES <<'EOF' || true
edeka-heininger|https://www.esc-geretsried.de/static/844160d2f7df10c329f9537993c46447/4fe8c/Edeka-Logo-1.jpg
Ehgartner-entsorgung|https://www.esc-geretsried.de/static/09e05cfbe4f660c5e6a9279e7f845706/4fe8c/ehgartner.jpg
energie-suedbayern|https://www.esc-geretsried.de/static/6ef2173ca1c73d4dcb9ae713e8e90baf/9c108/EC2024-1.png
sparkasse|https://www.esc-geretsried.de/static/e5f9fdb84659919d04f8e875b49f853b/4fe8c/Sparkasse.jpg
ipe-dach|https://www.esc-geretsried.de/static/16932cb3f2dec93ff48acea9a32b8554/4fe8c/IPE-DACH-Logo.jpg
elektro-friedl|https://www.esc-geretsried.de/static/9187cc399c24537debbfdf2d85be7a94/4fe8c/ElektroFriedl.jpg
agrobs|https://www.esc-geretsried.de/static/39bb7eb37647abad42f1ba3081d9de5b/4fe8c/Agrobs.jpg
bartsch-immobilien|https://www.esc-geretsried.de/static/c0bdb607aec793c65bb1996dfefd84b6/9dc27/Bartsch-Logo.jpg
pana|https://www.esc-geretsried.de/static/2e05f0f857c458caded7e549d06d1763/9dc27/Pana-Logo.jpg
planisware-deutschland|https://www.esc-geretsried.de/static/2c2d022914b48e4edbe5a8bbfd9b97b7/2a4de/PLW-blue_sign-web-01.png
autohaus-jorde|https://www.esc-geretsried.de/static/ba91add0fb53aecc0afe30e40a4bff76/9dc27/meisterhaft-1.jpg
kraemmel|https://www.esc-geretsried.de/static/d54a5cd79b4f84f582bb060840e59165/9dc27/Kraemmel-Logo.jpg
lhs|https://www.esc-geretsried.de/static/c977c12357c9c69387a79c9caf518611/4fe8c/LHS-Logo.jpg
bronberger-kessler|https://www.esc-geretsried.de/static/a6c103dc78890947383a46fa71ea7724/4fe8c/BronbergerKessler.jpg
lr-automobile|https://www.esc-geretsried.de/static/19280f8653df925cb5cbb3f5cceba1ce/4fe8c/lundr.jpg
lvm-versicherung|https://www.esc-geretsried.de/static/334042ed42243561df8a07c1b42ce593/9dc27/LVM-Banner.jpg
hockey-sports-ott|https://www.esc-geretsried.de/static/2a896b7c6d771d54340b01f6bc078bed/4fe8c/Ott-Logo.jpg
autohaus-pennig|https://www.esc-geretsried.de/static/d79265045d43ace0f97b5b5242ea41c0/4fe8c/pennig.jpg
gecko-fastener|https://www.esc-geretsried.de/static/3da064a1ba943201ae0b79f1e2a06122/4fe8c/geckofastener.jpg
konrad-gmbh|https://www.esc-geretsried.de/static/8d3243fb1eb09e74ece62420f26ebdcc/4fe8c/konrad.jpg
speck-pumpen|https://www.esc-geretsried.de/static/d6308df762e863f774a651e2ba344cda/9dc27/speck.jpg
gls|https://www.esc-geretsried.de/static/454e277d40eb7a543a7c716a78e269a3/1ea00/gls2024.png
fueger-fachhandel|https://www.esc-geretsried.de/static/acff380151c4dae90522c91b741edb23/4fe8c/fueger.jpg
fts-bauelemente|https://www.esc-geretsried.de/static/dcdac689f5cbbec445d6ca273dcd60f7/4fe8c/fts.jpg
raiffeisenbank-isar-loisachtal|https://www.esc-geretsried.de/static/be25d87f65877f84385c0a19036d8bc1/4fe8c/raiffeisen.jpg
fischer-johann|https://www.esc-geretsried.de/static/89b5c1b79d8f5b78aa52dc0ec1407271/4fe8c/fischer.jpg
lug|https://www.esc-geretsried.de/static/a46511f53648f5f88df965c22cea0e24/4fe8c/Lug.jpg
pw-dienstleistungen|https://www.esc-geretsried.de/static/fb0956fb1a621999997b6668cf415249/4fe8c/pw.jpg
auto-graf|https://www.esc-geretsried.de/static/256727bc4d777bba51137793fb7310cd/9dc27/graf.jpg
dielack|https://www.esc-geretsried.de/static/3e475612eff885e7347d7706580e466a/630fb/dielack_logo_final.png
franco-fresco|https://www.esc-geretsried.de/static/cd571e1a44d6ee2978da6160c9909bf4/9dc27/gustavo.jpg
hotel-zur-post|https://www.esc-geretsried.de/static/77fa4abb6e0fd7ea336b482cd53fcac0/9dc27/oberhauser.jpg
holzer-tiefbau|https://www.esc-geretsried.de/static/358bd0e7e835024d259e8c8cd86499c7/2a4de/Holzer-Tiefbau-Logo.png
kolbeck-hightech-logistik|https://www.esc-geretsried.de/static/b5c911bcdea64d322b03da4f67dc344b/4fe8c/Kolbeck-Logo.jpg
josef-mayr-bauunternehmen|https://www.esc-geretsried.de/static/8b9b73066535113d94cef27fcab834a9/4fe8c/May-Bau-Logo.jpg
quantum-systems|https://www.esc-geretsried.de/static/f0fc22c47d2228b0347e35d8cdc0d32c/2a4de/quantum-systems.png
raiffeisen-ware-oberland|https://www.esc-geretsried.de/static/8d91f9f1769cddec5d4079b02a625500/2a4de/raiffeisen.png
EOF

manifest="$ASSET_DIR/SHA256SUMS"
: > "$manifest"
metadata="$ASSET_DIR/.import-metadata.tsv"
: > "$metadata"

while IFS='|' read -r raw_id url; do
  [[ -z "$raw_id" ]] && continue
  id="$(printf '%s' "$raw_id" | tr '[:upper:]' '[:lower:]')"
  case "$url" in
    https://www.esc-geretsried.de/static/*) ;;
    *) echo "ERROR: unapproved logo source: $url" >&2; exit 4 ;;
  esac
  ext=".${url##*.}"
  ext="$(printf '%s' "$ext" | tr '[:upper:]' '[:lower:]')"
  out="$ASSET_DIR/$id$ext"
  echo "Importing $id"
  curl --fail --location --silent --show-error --retry 3 --connect-timeout 15 --max-time 90 "$url" -o "$out"
  test -s "$out"
  mime="$(file -b --mime-type "$out")"
  case "$mime" in image/*) ;; *) echo "ERROR: $id is $mime, expected image" >&2; exit 5 ;; esac
  sha256sum "$out" | sed "s#  $ASSET_DIR/#  #" >> "$manifest"
  printf '%s\t%s\t%s\n' "$id" "content/sponsors/assets/$id$ext" "$url" >> "$metadata"
done <<< "$SOURCES"

count="$(grep -c . "$metadata")"
[[ "$count" -eq 37 ]] || { echo "ERROR: expected 37 imported logos, got $count" >&2; exit 6; }

python3 - "$DATA_FILE" "$metadata" <<'PY'
import json, sys
from pathlib import Path

data_path = Path(sys.argv[1])
meta_path = Path(sys.argv[2])
meta = {}
for line in meta_path.read_text(encoding='utf-8').splitlines():
    sponsor_id, asset_path, source_url = line.split('\t')
    meta[sponsor_id] = (asset_path, source_url)

data = json.loads(data_path.read_text(encoding='utf-8'))
ids = {s['id'] for s in data['sponsors']}
if ids != set(meta):
    raise SystemExit(f'ERROR: sponsor ids and imported asset ids differ: data-only={sorted(ids-set(meta))}, asset-only={sorted(set(meta)-ids)}')
for sponsor in data['sponsors']:
    path, source_url = meta[sponsor['id']]
    sponsor['logo'] = path
    sponsor['logo_status'] = 'accepted_tenant_copy'
    sponsor['logo_source_url'] = source_url

data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
PY

rm -f "$metadata"
echo "Imported and verified 37 sponsor logos into canonical tenant content."

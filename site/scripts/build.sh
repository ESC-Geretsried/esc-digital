#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SITE="$ROOT/site"

command -v hugo >/dev/null 2>&1 || { echo "ERROR: hugo is required" >&2; exit 2; }

rm -rf "$SITE/public"

# Stage canonical tenant data for Hugo without making the generated/staged copy
# authoritative. Git under content/ remains the source of truth.
mkdir -p "$SITE/data"
cp "$ROOT/content/sponsors/sponsors.json" "$SITE/data/sponsors.json"
cp "$ROOT/content/sponsors/page.json" "$SITE/data/sponsor_page.json"
cp "$ROOT/content/home/home.json" "$SITE/data/home.json"
cp "$ROOT/content/home/heroes.json" "$SITE/data/home_heroes.json"
cp "$ROOT/content/navigation.json" "$SITE/data/navigation.json"
cp "$ROOT/content/river-rats/hockeydata.json" "$SITE/data/hockeydata.json"
cleanup() {
  rm -f "$SITE/data/sponsors.json" "$SITE/data/sponsor_page.json" "$SITE/data/home.json" "$SITE/data/home_heroes.json" "$SITE/data/navigation.json" "$SITE/data/hockeydata.json"
  rmdir "$SITE/data" 2>/dev/null || true
}
trap cleanup EXIT

HUGO_ARGS=(--source "$SITE" --config "$SITE/hugo.toml" --minify)
if [[ -n "${HUGO_BASEURL:-}" ]]; then
  HUGO_ARGS+=(--baseURL "$HUGO_BASEURL")
fi

hugo "${HUGO_ARGS[@]}"

# Structured JSON is build input/provenance, not public website content.
# Hugo treats non-page files below content/ as publishable resources, so remove
# these staged copies explicitly from output.
rm -rf "$SITE/public/home"
rm -f "$SITE/public/navigation.json"
rm -f "$SITE/public/sponsors/sponsors.json" "$SITE/public/sponsors/page.json"
rm -f "$SITE/public/river-rats/hockeydata.json"

# Visual assets are canonical tenant copies in Git. No runtime dependency on
# esc-int or Netlify remains after the one-time import.
mkdir -p "$SITE/public/images/hero" "$SITE/public/images/teams"
cp "$ROOT/images/river-rats-logo.png" "$SITE/public/images/river-rats-logo.png"
cp "$ROOT"/images/hero/*.jpeg "$SITE/public/images/hero/"
cp "$ROOT"/images/teams/* "$SITE/public/images/teams/"

# Sponsor logos are canonical tenant copies under content/sponsors/assets.
mkdir -p "$SITE/public/sponsors/assets"
find "$ROOT/content/sponsors/assets" -maxdepth 1 -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' -o -iname '*.svg' \) -exec cp {} "$SITE/public/sponsors/assets/" \;

# Build the new internal sponsors page directly from structured tenant data.
python3 "$SITE/scripts/render_sponsors_page.py" "${HUGO_BASEURL:-/}"

# Render transitional esc-int pages without overwriting canonical ESC routes.
python3 "$SITE/scripts/render_imported_pages.py" "${HUGO_BASEURL:-/}"

# Binding public-news rule: at the exact 24-month anniversary the article is
# no longer emitted publicly. Source/import material is retained; only public
# build output is removed here.
python3 "$SITE/scripts/enforce_news_retention.py"

# Render the River Rats HockeyData block deterministically from canonical
# tenant configuration. This avoids relying on fragile transitional Hugo
# section lookup while M2 is being consolidated.
python3 "$SITE/scripts/render_hockeydata.py"

# HockeyData requires its domain-bound API key in the client-side widget
# options. The key is never stored in Git; Pages injects it from Actions.
python3 "$SITE/scripts/inject_hockeydata_key.py"
bash "$SITE/scripts/validate_hockeydata.sh"
python3 "$SITE/scripts/validate_m2_content.py"

test -f "$SITE/public/index.html"
test -f "$SITE/public/sponsoren/index.html"
test -f "$SITE/public/river-rats/index.html"
test -f "$SITE/public/nachwuchs/index.html"
test -f "$SITE/public/images/river-rats-logo.png"
test -f "$SITE/public/images/hero/hero-01-bewegung.jpeg"
test "$(find "$SITE/public/images/teams" -maxdepth 1 -type f | wc -l)" -eq 10
test "$(find "$SITE/public/sponsors/assets" -maxdepth 1 -type f | wc -l)" -eq 37
echo "Built ESC site with $(hugo version), 24-month public news retention, curated homepage heroes, structured navigation, HockeyData widgets, M2 content policy gates, internal sponsors page, transitional esc-int content and 37 canonical sponsor logos"

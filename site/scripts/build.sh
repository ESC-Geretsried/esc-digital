#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SITE="$ROOT/site"

command -v hugo >/dev/null 2>&1 || { echo "ERROR: hugo is required" >&2; exit 2; }

rm -rf "$SITE/public"

# Stage canonical tenant data for Hugo without making the generated/staged copy
# authoritative. Git under content/ remains the source of truth.
mkdir -p "$SITE/data"
mkdir -p "$SITE/data/teams"
cp "$ROOT/content/sponsors/sponsors.json" "$SITE/data/sponsors.json"
cp "$ROOT/content/sponsors/page.json" "$SITE/data/sponsor_page.json"
cp "$ROOT/content/home/home.json" "$SITE/data/home.json"
cp "$ROOT/content/home/heroes.json" "$SITE/data/home_heroes.json"
cp "$ROOT/content/navigation.json" "$SITE/data/navigation.json"
cp "$ROOT/content/river-rats/hockeydata.json" "$SITE/data/hockeydata.json"
cp "$ROOT/content/river-rats/team.json" "$SITE/data/river_rats_team.json"
for source in "$ROOT"/content/teams/*/team.json; do
  team_key="$(basename "$(dirname "$source")")"
  cp "$source" "$SITE/data/teams/$team_key.json"
done
# Filter only the staged public projection. Canonical and imported Git sources
# remain untouched so publication history and provenance are never lost.
python3 "$SITE/scripts/enforce_news_retention.py" --filter-staged-home "$SITE/data/home.json"
cleanup() {
  rm -f "$SITE/data/sponsors.json" "$SITE/data/sponsor_page.json" "$SITE/data/home.json" "$SITE/data/home_heroes.json" "$SITE/data/navigation.json" "$SITE/data/hockeydata.json" "$SITE/data/river_rats_team.json"
  rm -rf "$SITE/data/teams"
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
rm -rf "$SITE/public/teams"
rm -f "$SITE/public/navigation.json"
rm -f "$SITE/public/sponsors/sponsors.json" "$SITE/public/sponsors/page.json"
rm -f "$SITE/public/river-rats/hockeydata.json" "$SITE/public/river-rats/team.json"

# Visual assets are canonical tenant copies in Git. No runtime dependency on
# esc-int or Netlify remains after the one-time import.
mkdir -p "$SITE/public/images/hero" "$SITE/public/images/teams" "$SITE/public/images/inklusion" "$SITE/public/images/people/river-rats/staff" "$SITE/public/images/people/river-rats/players"
cp "$ROOT/images/river-rats-logo.png" "$SITE/public/images/river-rats-logo.png"
cp "$ROOT"/images/hero/*.jpeg "$SITE/public/images/hero/"
cp "$ROOT"/images/teams/* "$SITE/public/images/teams/"
cp "$ROOT"/images/inklusion/*.png "$SITE/public/images/inklusion/"
cp "$ROOT"/content/river-rats/assets/staff/*.jpg "$SITE/public/images/people/river-rats/staff/"
cp "$ROOT"/content/river-rats/assets/players/*.jpg "$SITE/public/images/people/river-rats/players/"

# Sponsor logos are canonical tenant copies under content/sponsors/assets.
mkdir -p "$SITE/public/sponsors/assets"
find "$ROOT/content/sponsors/assets" -maxdepth 1 -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' -o -iname '*.svg' \) -exec cp {} "$SITE/public/sponsors/assets/" \;

# Build the new internal sponsors page directly from structured tenant data.
python3 "$SITE/scripts/render_sponsors_page.py" "${HUGO_BASEURL:-/}"

# Render transitional esc-int pages without overwriting canonical ESC routes.
python3 "$SITE/scripts/render_imported_pages.py" "${HUGO_BASEURL:-/}"

# Binding public-news rule: at the exact 12-month anniversary the article is
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
for path in river-rats-damen u20 u17 u15 u13 u11 u9 u7; do test -f "$SITE/public/$path/index.html"; done
test -f "$SITE/public/images/river-rats-logo.png"
test -f "$SITE/public/images/hero/hero-01-bewegung.jpeg"
test -f "$SITE/public/images/people/river-rats/staff/thomas-gams.jpg"
test -f "$SITE/public/images/people/river-rats/players/korbinian-sertl.jpg"
test -f "$SITE/public/images/inklusion/d-wagner-immobilien.png"
test -f "$SITE/public/images/inklusion/rotary-club-wolfratshausen-isartal.png"
test "$(find "$SITE/public/images/teams" -maxdepth 1 -type f | wc -l)" -eq 11
test "$(find "$SITE/public/images/people/river-rats/staff" -maxdepth 1 -type f | wc -l)" -eq 9
test "$(find "$SITE/public/images/people/river-rats/players" -maxdepth 1 -type f | wc -l)" -eq 11
test "$(find "$SITE/public/sponsors/assets" -maxdepth 1 -type f | wc -l)" -eq 37
echo "Built ESC site with $(hugo version), 12-month public news retention, eight Founder-sourced team pages, curated homepage heroes, structured navigation, HockeyData widgets, structured River Rats profile with 11 verified local player and 9 staff photos, M2 content policy gates, internal sponsors page, transitional esc-int content and 37 canonical sponsor logos"

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
cleanup() {
  rm -f "$SITE/data/sponsors.json" "$SITE/data/sponsor_page.json" "$SITE/data/home.json"
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
rm -f "$SITE/public/sponsors/sponsors.json" "$SITE/public/sponsors/page.json"

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

# Render the frozen esc-int content snapshot inside the authoritative
# esc-digital shell. /sponsoren/ is explicitly excluded from the snapshot.
python3 "$SITE/scripts/render_imported_pages.py" "${HUGO_BASEURL:-/}"

test -f "$SITE/public/index.html"
test -f "$SITE/public/sponsoren/index.html"
test -f "$SITE/public/river-rats/index.html"
test -f "$SITE/public/nachwuchs/index.html"
test -f "$SITE/public/images/river-rats-logo.png"
test -f "$SITE/public/images/hero/hero-01-bewegung.jpeg"
test "$(find "$SITE/public/images/teams" -maxdepth 1 -type f | wc -l)" -eq 10
test "$(find "$SITE/public/sponsors/assets" -maxdepth 1 -type f | wc -l)" -eq 37
echo "Built ESC site with $(hugo version), internal sponsors page, frozen esc-int content, 14 rotating hero/team images and 37 canonical sponsor logos"

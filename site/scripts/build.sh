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
cp "$ROOT/content/home/home.json" "$SITE/data/home.json"
cleanup() {
  rm -f "$SITE/data/sponsors.json" "$SITE/data/home.json"
  rmdir "$SITE/data" 2>/dev/null || true
}
trap cleanup EXIT

HUGO_ARGS=(--source "$SITE" --config "$SITE/hugo.toml" --minify)
if [[ -n "${HUGO_BASEURL:-}" ]]; then
  HUGO_ARGS+=(--baseURL "$HUGO_BASEURL")
fi

hugo "${HUGO_ARGS[@]}"

# Transitional visual assets already versioned in this repository are staged
# into generated output. They remain reproducible Git inputs; no provider or
# external runtime dependency is introduced.
mkdir -p "$SITE/public/images/hero"
cp "$ROOT/images/river-rats-logo.png" "$SITE/public/images/river-rats-logo.png"
cp "$ROOT"/images/hero/*.jpeg "$SITE/public/images/hero/"

# Sponsor logos are canonical tenant copies under content/sponsors/assets.
# Publish only image files; provenance/manifest files remain repository-only.
mkdir -p "$SITE/public/sponsors/assets"
find "$ROOT/content/sponsors/assets" -maxdepth 1 -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' -o -iname '*.svg' \) -exec cp {} "$SITE/public/sponsors/assets/" \;

test -f "$SITE/public/index.html"
test -f "$SITE/public/images/river-rats-logo.png"
test -f "$SITE/public/images/hero/hero-01-bewegung.jpeg"
test "$(find "$SITE/public/sponsors/assets" -maxdepth 1 -type f | wc -l)" -eq 37
echo "Built ESC site with $(hugo version), imported home modules and 37 canonical sponsor logos"

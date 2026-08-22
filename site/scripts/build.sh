#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SITE="$ROOT/site"

command -v hugo >/dev/null 2>&1 || { echo "ERROR: hugo is required" >&2; exit 2; }

rm -rf "$SITE/public"

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

test -f "$SITE/public/index.html"
test -f "$SITE/public/images/river-rats-logo.png"
test -f "$SITE/public/images/hero/hero-01-bewegung.jpeg"
echo "Built ESC site with $(hugo version)"

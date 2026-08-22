#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SITE="$ROOT/site"

command -v hugo >/dev/null 2>&1 || { echo "ERROR: hugo is required" >&2; exit 2; }

rm -rf "$SITE/public"
hugo --source "$SITE" --config "$SITE/hugo.toml" --minify

test -f "$SITE/public/index.html"
echo "Built ESC site with $(hugo version)"

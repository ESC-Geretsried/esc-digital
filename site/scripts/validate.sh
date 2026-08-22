#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="$ROOT/site/public"
INDEX="$OUT/index.html"

test -f "$INDEX" || { echo "ERROR: missing $INDEX" >&2; exit 2; }
grep -qi '<!doctype html>' "$INDEX"
grep -q 'Leidenschaft. Team. Zukunft.' "$INDEX"
grep -q 'noindex,nofollow,noarchive' "$INDEX"

if grep -RInE '(BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})' "$OUT"; then
  echo "ERROR: credential-like material found in generated output" >&2
  exit 3
fi

echo "Static smoke validation passed"

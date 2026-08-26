#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/content/river-rats/assets/players"
mkdir -p "$OUT"

curl -fsSL 'https://www.esc-geretsried.de/static/641714204ffa478f05d023a4078dbf4c/f836f/1938-1.jpg' -o "$OUT/korbinian-sertl.jpg"
curl -fsSL 'https://www.esc-geretsried.de/static/122b21b8813dbce6c5b2a15a8d65dd14/f836f/1950-1.jpg' -o "$OUT/maximilian-freytag.jpg"
curl -fsSL 'https://www.esc-geretsried.de/static/69c2a61d99473ebdf00e2083e606c038/f836f/1953-Muehlpointner.jpg' -o "$OUT/kilian-muehlpointner.jpg"
curl -fsSL 'https://www.esc-geretsried.de/static/2d1b7f76f903fb93c58c3e49ea6c6976/f836f/2007.jpg' -o "$OUT/martin-sanner.jpg"
curl -fsSL 'https://www.esc-geretsried.de/static/c30a3f3bb326241c2f5a521f8ba8e977/f836f/1918-1.jpg' -o "$OUT/stephan-englbrecht.jpg"
curl -fsSL 'https://www.esc-geretsried.de/static/150c7b8588ee203f757ecf8510f305d0/f836f/1954.jpg' -o "$OUT/moritz-schug.jpg"
curl -fsSL 'https://www.esc-geretsried.de/static/9aaf4899d5621682fdf73783d86ccfc0/f836f/1946-1.jpg' -o "$OUT/dominik-soukup.jpg"
curl -fsSL 'https://www.esc-geretsried.de/static/1fc6fd2238d812c70c402ec9371d7d25/f836f/1930.jpg' -o "$OUT/max-huesken.jpg"
curl -fsSL 'https://www.esc-geretsried.de/static/08799f67a6ef4186323d255d62d73c31/f836f/1962.jpg' -o "$OUT/ondrej-horvath.jpg"
curl -fsSL 'https://www.esc-geretsried.de/static/2695e8b9269f59ab6702f86b55c88cac/f836f/1987.jpg' -o "$OUT/luis-huber.jpg"
curl -fsSL 'https://www.esc-geretsried.de/static/3b05b79fac41dea9fb781e8519d1d810/f836f/1914-1.jpg' -o "$OUT/oliver-ott.jpg"

echo "Fetched 11 verified official ESC player photos into Git-owned assets"

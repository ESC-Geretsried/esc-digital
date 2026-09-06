#!/usr/bin/env python3
"""Fail-closed checks for the public, fully static demo snapshot."""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "site/public")
pages = list(root.rglob("*.html"))
if not (root / "index.html").exists() or not pages:
    raise SystemExit("ERROR: static demo has no HTML homepage")

joined = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in pages)
for marker in ("data-esc-gamepitch", "__HOCKEYDATA_API_KEY__", "api.hockeydata.net/js", "api.hockeydata.net/css"):
    if marker in joined:
        raise SystemExit(f"ERROR: dynamic provider marker remains in static demo: {marker}")
if re.search(r"<script[^>]+src=[\"']https?://", joined, re.I):
    raise SystemExit("ERROR: external JavaScript remains in static demo")
if "orp-esc-int.netlify.app" in joined:
    raise SystemExit("ERROR: demo hostname leaked into static page copy")
print(f"Static demo snapshot validated: {len(pages)} HTML pages, no runtime provider widgets")

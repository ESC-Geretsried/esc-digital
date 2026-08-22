#!/usr/bin/env python3
from pathlib import Path
from datetime import date
import json
import re

root = Path(__file__).resolve().parents[2]
public = root / "site" / "public"

heroes = json.loads((root / "content" / "home" / "heroes.json").read_text(encoding="utf-8"))
active = sorted((s for s in heroes["slides"] if s.get("active")), key=lambda s: s.get("order", 0))
max_active = int(heroes.get("max_active", 6))
if not active:
    raise SystemExit("ERROR: homepage requires at least one active hero")
if len(active) > max_active or len(active) > 6:
    raise SystemExit(f"ERROR: homepage has {len(active)} active heroes; maximum is 6")
for slide in active:
    image = root / slide["image"]
    if not image.is_file():
        raise SystemExit(f"ERROR: hero asset missing: {slide['image']}")
    for key in ("area", "headline", "cta_label", "cta_path", "focus_desktop", "focus_mobile"):
        if not slide.get(key):
            raise SystemExit(f"ERROR: hero {slide.get('id', '<unknown>')} missing {key}")

home = json.loads((root / "content" / "home" / "home.json").read_text(encoding="utf-8"))
today = date.today()
try:
    cutoff = today.replace(year=today.year - 2)
except ValueError:
    cutoff = today.replace(year=today.year - 2, day=28)
for group in home.get("news_groups", []):
    for item in group.get("items", []):
        match = re.search(r"/(\d{4})-(\d{2})-(\d{2})-", item.get("path", ""))
        if not match:
            raise SystemExit(f"ERROR: homepage news path lacks publication date: {item.get('path')}")
        published = date(*(int(v) for v in match.groups()))
        if published <= cutoff:
            raise SystemExit(f"ERROR: news at or beyond 24 months is publicly referenced: {item.get('path')}")
        target = public / item["path"].strip("/") / "index.html"
        if not target.is_file():
            raise SystemExit(f"ERROR: homepage references news not present in public build: {item.get('path')}")

navigation = json.loads((root / "content" / "navigation.json").read_text(encoding="utf-8"))
visible_paths = []
for item in navigation.get("main", []) + navigation.get("actions", []):
    if item.get("visible"):
        visible_paths.append(item["path"])
for group in navigation.get("footer_groups", []):
    for item in group.get("links", []):
        if item.get("visible"):
            visible_paths.append(item["path"])

for path in sorted(set(visible_paths)):
    if not path.startswith("/"):
        raise SystemExit(f"ERROR: visible internal navigation path must be root-relative: {path}")
    target = public / path.strip("/") / "index.html"
    if path == "/":
        target = public / "index.html"
    if not target.is_file():
        raise SystemExit(f"ERROR: visible navigation route missing from build: {path}")

print(f"M2 content policy PASS: {len(active)} active heroes, exact news cutoff {cutoff.isoformat()}, {len(set(visible_paths))} visible internal routes")

#!/usr/bin/env python3
from pathlib import Path
from datetime import date
from hashlib import sha256
import json
import re

root = Path(__file__).resolve().parents[2]
public = root / "site" / "public"

team = json.loads((root / "content" / "river-rats" / "team.json").read_text(encoding="utf-8"))
staff_manifest = json.loads((root / "content" / "river-rats" / "staff-photos.json").read_text(encoding="utf-8"))
staff_photos = staff_manifest.get("photos", [])
if staff_manifest.get("team_id") != "river-rats" or len(staff_photos) != 9:
    raise SystemExit("ERROR: River Rats staff photo manifest must contain exactly 9 records")
if {row["name"] for row in staff_photos} != {row["name"] for row in team.get("staff", [])}:
    raise SystemExit("ERROR: River Rats staff photo manifest differs from canonical staff names")
manifest_by_name = {row["name"]: row for row in staff_photos}
if len(manifest_by_name) != len(staff_photos):
    raise SystemExit("ERROR: duplicate River Rats staff photo manifest name")
for staff in team["staff"]:
    photo = manifest_by_name[staff["name"]]
    if staff.get("image") != photo.get("public_path"):
        raise SystemExit(f"ERROR: team image differs from staff photo manifest: {staff['name']}")
    source_page = str(photo.get("source_page", ""))
    source_image = str(photo.get("source_image", ""))
    if not source_page.startswith("https://www.esc-geretsried.de/") or not source_image.startswith("https://www.esc-geretsried.de/static/"):
        raise SystemExit(f"ERROR: staff photo provenance is not an official ESC source: {staff['name']}")
    asset = root / photo["asset"]
    published = public / photo["public_path"]
    if not asset.is_file() or not published.is_file():
        raise SystemExit(f"ERROR: local or published staff photo missing: {staff['name']}")
    expected_hash = photo.get("sha256")
    if sha256(asset.read_bytes()).hexdigest() != expected_hash or sha256(published.read_bytes()).hexdigest() != expected_hash:
        raise SystemExit(f"ERROR: staff photo checksum mismatch: {staff['name']}")

published_staff = list((public / "images" / "people" / "river-rats" / "staff").glob("*.jpg"))
if len(published_staff) != 9:
    raise SystemExit(f"ERROR: expected 9 published River Rats staff photos, got {len(published_staff)}")

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

print(f"M2 content policy PASS: {len(active)} active heroes, 9 verified local River Rats staff photos, exact news cutoff {cutoff.isoformat()}, {len(set(visible_paths))} visible internal routes")

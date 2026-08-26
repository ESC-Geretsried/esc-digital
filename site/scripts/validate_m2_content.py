#!/usr/bin/env python3
from pathlib import Path
from datetime import date, datetime
from hashlib import sha256
import json
import os
import re
from zoneinfo import ZoneInfo

from enforce_news_retention import expiry_for

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

player_manifest = json.loads((root / "content" / "river-rats" / "player-photos.json").read_text(encoding="utf-8"))
player_photos = player_manifest.get("photos", [])
roster_with_photos = [row for row in team.get("roster", []) if row.get("image")]
if player_manifest.get("team_id") != "river-rats" or len(player_photos) != 11:
    raise SystemExit("ERROR: River Rats player photo manifest must contain exactly 11 records")
if {row["name"] for row in player_photos} != {row["name"] for row in roster_with_photos}:
    raise SystemExit("ERROR: River Rats player photo manifest differs from canonical roster photo names")
player_manifest_by_name = {row["name"]: row for row in player_photos}
for player in roster_with_photos:
    photo = player_manifest_by_name[player["name"]]
    if player.get("image") != photo.get("public_path") or player.get("source_image") != photo.get("source_image"):
        raise SystemExit(f"ERROR: player image/provenance differs from manifest: {player['name']}")
    if not str(photo.get("source_image", "")).startswith("https://www.esc-geretsried.de/static/"):
        raise SystemExit(f"ERROR: player photo provenance is not an official ESC source: {player['name']}")
    asset = root / photo["asset"]
    published = public / photo["public_path"]
    if not asset.is_file() or not published.is_file():
        raise SystemExit(f"ERROR: local or published player photo missing: {player['name']}")
    expected_hash = photo.get("sha256")
    if sha256(asset.read_bytes()).hexdigest() != expected_hash or sha256(published.read_bytes()).hexdigest() != expected_hash:
        raise SystemExit(f"ERROR: player photo checksum mismatch: {player['name']}")

published_players = list((public / "images" / "people" / "river-rats" / "players").glob("*.jpg"))
if len(published_players) != 11:
    raise SystemExit(f"ERROR: expected 11 published River Rats player photos, got {len(published_players)}")

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
policy = json.loads((root / "config" / "news-retention.json").read_text(encoding="utf-8"))
if policy.get("public_window_months") != 12:
    raise SystemExit("ERROR: public news retention must be exactly 12 months")
explicit_as_of = os.environ.get("NEWS_RETENTION_AS_OF", "").strip()
today = datetime.strptime(explicit_as_of, "%Y-%m-%d").date() if explicit_as_of else datetime.now(ZoneInfo(policy["policy_timezone"])).date()
homepage_html = (public / "index.html").read_text(encoding="utf-8")
for group in home.get("news_groups", []):
    for item in group.get("items", []):
        match = re.search(r"/(\d{4})-(\d{2})-(\d{2})-", item.get("path", ""))
        if not match:
            raise SystemExit(f"ERROR: homepage news path lacks publication date: {item.get('path')}")
        published = date(*(int(v) for v in match.groups()))
        target = public / item["path"].strip("/") / "index.html"
        expired = today >= expiry_for(published, int(policy["public_window_months"]))
        public_href = item["path"].strip("/") in homepage_html
        if expired and (target.is_file() or public_href):
            raise SystemExit(f"ERROR: expired news remains in public projection: {item.get('path')}")
        if not expired and (not target.is_file() or not public_href):
            raise SystemExit(f"ERROR: retained news missing from public projection: {item.get('path')}")

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

print(f"M2 content policy PASS: {len(active)} active heroes, 11 verified local River Rats player and 9 staff photos, exact 12-month news policy as of {today.isoformat()}, {len(set(visible_paths))} visible internal routes")

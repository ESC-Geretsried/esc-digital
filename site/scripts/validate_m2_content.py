#!/usr/bin/env python3
from pathlib import Path
from datetime import date, datetime
from hashlib import sha256
from html import unescape
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

expected_heroes = {
    "river-rats-action": ("Eishockey. Gemeinschaft. Geretsried.", "/river-rats/", "images/hero/hero-01-bewegung.jpeg"),
    "damen": ("Gemeinsam auf dem Eis.", "/river-rats-damen/", "images/teams/damen-team.jpg"),
    "nachwuchs": ("Die Zukunft der River Rats.", "/nachwuchs/", "images/teams/u13-team.jpg"),
    "eislaufschule": ("Die ersten Schritte auf dem Eis.", "/eislaufschule/", "images/teams/eislaufschule-2025-2026.png"),
    "eiskunstlauf": ("Bewegung. Präzision. Ausdruck.", "/eiskunstlauf/", "images/teams/eiskunstlauf.jpeg"),
    "inklusion": ("Gemeinsam Sport erleben.", "/inklusion/", "images/teams/inklusion.jpg"),
}
actual_heroes = {slide["id"]: (slide["headline"], slide["cta_path"], slide["image"]) for slide in active}
if actual_heroes != expected_heroes:
    raise SystemExit("ERROR: Founder-confirmed six-slide Homepage mapping drift")
youth = next(slide for slide in active if slide["id"] == "nachwuchs")
if youth.get("daily_images") != [f"images/teams/{team}-team.jpg" for team in ("u7", "u9", "u11", "u13", "u15", "u17", "u20")]:
    raise SystemExit("ERROR: Monday-Sunday youth hero image mapping drift")
if "daily_paths" in youth or youth.get("cta_path") != "/nachwuchs/":
    raise SystemExit("ERROR: youth hero may rotate only its image; its target must stay /nachwuchs/")

announcements = json.loads((root / "content" / "home" / "announcements.json").read_text(encoding="utf-8"))
active_announcements = sorted((item for item in announcements.get("messages", []) if item.get("active")), key=lambda item: item.get("order", 0))
if not active_announcements:
    raise SystemExit("ERROR: AnnouncementTicker has no active message")
if announcements.get("rotation") != "sequential-slow" or announcements.get("reduced_motion") != "first-message-static":
    raise SystemExit("ERROR: AnnouncementTicker motion contract drift")
first_announcement = active_announcements[0]
if first_announcement != {
    "id": "season-ticket-2026-2027",
    "text": "DAUERKARTE   Dauerkarten Saison 2026/2027 – jetzt hier verbindlich bestellen",
    "label": "DAUERKARTE",
    "message": "Dauerkarten Saison 2026/2027 – jetzt hier verbindlich bestellen",
    "url": "https://esc-geretsried.github.io/bestellung/",
    "new_tab": True,
    "active": True,
    "order": 10,
}:
    raise SystemExit("ERROR: Founder-confirmed first AnnouncementTicker message drift")

home = json.loads((root / "content" / "home" / "home.json").read_text(encoding="utf-8"))
expected_home_areas = {
    "primary_entrances": [("River Rats", "/river-rats/"), ("Nachwuchs", "/nachwuchs/"), ("Mitglied werden", "/mitgliedschaft/")],
    "sport_areas": [("Damen", "/river-rats-damen/"), ("Eislaufschule", "/eislaufschule/"), ("Eiskunstlauf", "/eiskunstlauf/"), ("Inklusionssport", "/inklusion/")],
    "club_areas": [("Verein", "/verein/"), ("Förderverein", "/foerderverein/")],
}
for field, expected in expected_home_areas.items():
    actual = [(item.get("title"), item.get("path")) for item in home.get(field, [])]
    if actual != expected:
        raise SystemExit(f"ERROR: Homepage {field} mapping drift: {actual}")
policy = json.loads((root / "config" / "news-retention.json").read_text(encoding="utf-8"))
if policy.get("public_window_months") != 12:
    raise SystemExit("ERROR: public news retention must be exactly 12 months")
explicit_as_of = os.environ.get("NEWS_RETENTION_AS_OF", "").strip()
today = datetime.strptime(explicit_as_of, "%Y-%m-%d").date() if explicit_as_of else datetime.now(ZoneInfo(policy["policy_timezone"])).date()
homepage_html = (public / "index.html").read_text(encoding="utf-8")
decoded_homepage_html = unescape(unescape(homepage_html)).replace("\xa0", " ")
if "DAUERKARTE" not in decoded_homepage_html or "Dauerkarten Saison 2026/2027 – jetzt hier verbindlich bestellen" not in decoded_homepage_html:
    raise SystemExit("ERROR: first AnnouncementTicker message missing from Homepage")
announcement_link = r'<a[^>]*href=(?:"|)https://esc-geretsried\.github\.io/bestellung/(?:"|)[^>]*target=(?:"|)_blank(?:"|)[^>]*rel="noopener noreferrer"'
if not re.search(announcement_link, homepage_html):
    raise SystemExit("ERROR: AnnouncementTicker target/new-tab boundary missing from Homepage")
if ('announcement-ticker__track is-rotating' not in homepage_html
        or '--announcement-duration:56s' not in homepage_html
        or homepage_html.count('announcement-ticker__sequence') != 2):
    raise SystemExit("ERROR: AnnouncementTicker slow-loop structure missing from Homepage")
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
expected_header = ["River Rats", "Nachwuchs", "Damen", "Eiskunstlauf", "Inklusionssport", "Eislaufschule", "Verein", "Förderverein"]
actual_header = [item["label"] for item in sorted(navigation.get("main", []), key=lambda item: item.get("order", 0)) if item.get("visible")]
if actual_header != expected_header:
    raise SystemExit(f"ERROR: global header mapping drift: {actual_header}")
if [item["label"] for item in navigation.get("actions", []) if item.get("visible")] != ["Mitglied werden"]:
    raise SystemExit("ERROR: global header action mapping drift")
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

primary_paths = ["/river-rats/", "/nachwuchs/", "/mitgliedschaft/"]
primary_match = re.search(r'<nav class=(?:"[^"]*\bprimary-entrances\b[^"]*"|primary-entrances)\b', homepage_html)
primary_start = primary_match.start() if primary_match else -1
primary_end = homepage_html.find("</nav>", primary_start)
primary_html = homepage_html[primary_start:primary_end]
primary_positions = []
for path in primary_paths:
    match = re.search(rf'href=(?:"|){re.escape(path)}(?:"|)', primary_html)
    primary_positions.append(match.start() if match else -1)
if any(position < 0 for position in primary_positions) or primary_positions != sorted(primary_positions):
    raise SystemExit("ERROR: PrimaryEntrances missing or out of order")
partners_match = re.search(r'<section class=(?:"[^"]*\bpartners\b[^"]*"|partners)\b', homepage_html)
if not partners_match or primary_end > partners_match.start():
    raise SystemExit("ERROR: PrimaryEntrances must be directly before SponsorTicker")

position_codes = {"T", "V", "S"}
external_teams = {"damen", "u13", "u15", "u17", "u20"}
young_teams = {"u7", "u9", "u11"}
for team_key in sorted(external_teams | young_teams):
    team_data = json.loads((root / "content" / "teams" / team_key / "team.json").read_text(encoding="utf-8"))
    for player in team_data.get("roster", []):
        if not str(player.get("name", "")).strip() or not str(player.get("number", "")).strip():
            raise SystemExit(f"ERROR: {team_key} player requires name and number")
        if player.get("position_code") not in position_codes:
            raise SystemExit(f"ERROR: {team_key} player position must be T/V/S")
        if team_key in young_teams and player.get("rodi_url"):
            raise SystemExit(f"ERROR: {team_key} must not expose RODI")
    for forbidden in ("official_table_url", "official_results_url"):
        if team_data.get(forbidden):
            raise SystemExit(f"ERROR: {team_key} must not maintain internal {forbidden}")
    if team_key in young_teams and team_data.get("official_schedule_url"):
        raise SystemExit(f"ERROR: {team_key} must not expose DEB/RODI competition links")
    page_html = (public / team_data["public_path"].strip("/") / "index.html").read_text(encoding="utf-8")
    if any(f'id="{section}"' in page_html for section in ("spielplan", "tabelle", "ergebnisse")):
        raise SystemExit(f"ERROR: {team_key} contains forbidden internal competition section")
    external_buttons = page_html.count("SPIELPLAN &amp; TABELLE")
    expected_buttons = 1 if team_key in external_teams and team_data.get("official_schedule_url") else 0
    if external_buttons != expected_buttons:
        raise SystemExit(f"ERROR: {team_key} external competition button count is {external_buttons}, expected {expected_buttons}")

river_html = (public / "river-rats" / "index.html").read_text(encoding="utf-8")
hero_end = river_html.find("</section>", river_html.find('class="team-hero"'))
if "GameSlider" in river_html[river_html.find('class="team-hero"'):hero_end]:
    raise SystemExit("ERROR: River Rats hero must not contain graphical game widget")
next_home = team.get("next_home_game") or {}
if "next-home-game" in river_html and not (next_home.get("verified") is True and all(next_home.get(key) for key in ("date", "time", "opponent"))):
    raise SystemExit("ERROR: unverified or incomplete next home game was rendered")

placeholder_status = (root / "docs" / "operations" / "player-placeholder-status.md").read_text(encoding="utf-8")
if "Status: **OPEN**" not in placeholder_status:
    raise SystemExit("ERROR: unavailable canonical player placeholder must remain explicitly OPEN")

print(f"M2 content policy PASS: {len(active)} active heroes, 11 verified local River Rats player and 9 staff photos, exact 12-month news policy as of {today.isoformat()}, {len(set(visible_paths))} visible internal routes")

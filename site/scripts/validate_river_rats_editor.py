#!/usr/bin/env python3
from hashlib import sha256
import json
from pathlib import Path


root = Path(__file__).resolve().parents[2]
editor = root / "content" / ".orp-editor"
team_source = json.loads((root / "content" / "river-rats" / "team.json").read_text(encoding="utf-8"))
renderer = (root / "site" / "scripts" / "render_hockeydata.py").read_text(encoding="utf-8")


def records(kind):
    rows = []
    for path in sorted((editor / kind).glob("*.json")):
        row = json.loads(path.read_text(encoding="utf-8"))
        expected = sha256(row["record_id"].encode()).hexdigest() + ".json"
        if path.name != expected:
            raise SystemExit(f"ERROR: {kind} record filename does not bind record_id: {path.name}")
        if row.get("team_key") == "river-rats" or (kind == "news" and row.get("area_key") == "river-rats"):
            rows.append(row)
    return rows


players = records("players")
staff = records("staff")
news = records("news")
if (len(players), len(staff), len(news)) != (16, 9, 4):
    raise SystemExit(f"ERROR: expected 16/9/4 River Rats player/staff/news records, got {len(players)}/{len(staff)}/{len(news)}")

if {row["display_name"] for row in players} != {row["name"] for row in team_source["roster"]}:
    raise SystemExit("ERROR: editor player names differ from canonical River Rats team source")
if {row["display_name"] for row in staff} != {row["name"] for row in team_source["staff"]}:
    raise SystemExit("ERROR: editor staff names differ from canonical River Rats team source")
if {row["title"] for row in news} != {row["title"] for row in team_source["news"]}:
    raise SystemExit("ERROR: editor news titles differ from canonical River Rats team source")

# Product rule: generic schema fields may remain, but team frontend must not render height or weight.
if 'height_cm' in renderer or 'weight_kg' in renderer:
    raise SystemExit("ERROR: height/weight fields referenced by River Rats frontend renderer")
for required in ('row.get("group"', 'row.get("nationality"', 'row.get("handedness"'):
    if required not in renderer:
        raise SystemExit(f"ERROR: verified player metadata missing from frontend renderer: {required}")

expected_news = {
    "Doppelpack für die Defensive – Englbrecht und Sanner verlängern": "Stephan Englbrecht und Martin Sanner verlängern bei den River Rats.",
    "Saisonkarten-Verkauf gestartet": "Der Saisonkarten-Verkauf ist gestartet.",
    "Internationale Erfahrung für die River Rats": "Gunārs Skvorcovs verstärkt die River Rats.",
    "13 Jahre und kein Ende in Sicht – Ondrej Horvath bleibt": "Ondrej Horvath bleibt in Geretsried.",
}
for row in news:
    expected = expected_news[row["title"]]
    if row.get("summary") != expected or row.get("body") != expected:
        raise SystemExit(f"ERROR: editor news is not source-pure: {row['title']}")

for row in players + staff + news:
    for protected in ("api_binding", "league_binding", "division_binding", "hockeydata_config", "gamepitch_binding"):
        if protected in row:
            raise SystemExit(f"ERROR: protected provider fact copied into editor record: {protected}")

team_record = json.loads((editor / "teams" / "cb609c63504dd50d6ebf638b7ff31ff366c89dd2c89d52752587a15053846a4a.json").read_text(encoding="utf-8"))
if team_record.get("sports_provider") != "hockeydata":
    raise SystemExit("ERROR: protected HockeyData provider marker changed")
if team_record.get("hero_asset_key") or team_record.get("team_photo_asset_key"):
    raise SystemExit("ERROR: unverified Binary Assets V1 key was invented")

page_files = list((editor / "pages").glob("*.json"))
page = next(json.loads(path.read_text(encoding="utf-8")) for path in page_files if json.loads(path.read_text(encoding="utf-8")).get("team_key") == "river-rats")
source_overview = "Die River Rats sind die erste Mannschaft des ESC River Rats Geretsried."
block_record = json.loads((editor / "blocks" / "dff167f4537681950a1930c4bdcf2791b789b4d15b472ab586596bf5bf86c778.json").read_text(encoding="utf-8"))
if page.get("body") != source_overview or page.get("summary") != source_overview:
    raise SystemExit("ERROR: River Rats Page content is not source-pure")
if block_record.get("body") != source_overview or team_record.get("short_description") != source_overview:
    raise SystemExit("ERROR: River Rats overview/team content is not source-pure")

forbidden_public_phrases = (
    "für die int-migration", "im int-stand", "quelle:", "orp editor",
    "zentraler seniorenbereich", "geschützte hockeydata-spielbetriebsintegration",
)
for row in news + [page, block_record, team_record]:
    visible = " ".join(str(row.get(field, "")) for field in ("title", "summary", "body", "short_description")).casefold()
    for phrase in forbidden_public_phrases:
        if phrase in visible:
            raise SystemExit(f"ERROR: technical/migration wording leaked into visible editor content: {phrase}")

for key in ("hero_image", "team_photo"):
    path = root / team_source[key]
    if not path.is_file():
        raise SystemExit(f"ERROR: existing Git image reference is missing: {team_source[key]}")

print("River Rats editor initial state validated: 16 players, 9 staff, 4 news; HockeyData protected; height/weight frontend display disabled")

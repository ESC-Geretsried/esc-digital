#!/usr/bin/env python3
from hashlib import sha256
import json
from pathlib import Path


root = Path(__file__).resolve().parents[2]
editor = root / "content" / ".orp-editor"
team_source = json.loads((root / "content" / "river-rats" / "team.json").read_text(encoding="utf-8"))


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
for phrase in ("Teamfoto", "Mannschaft/Kader", "HockeyData/GamePitch", "Freundschaftsspiele"):
    if phrase not in page.get("body", ""):
        raise SystemExit(f"ERROR: River Rats editor page body missing {phrase!r}")

for key in ("hero_image", "team_photo"):
    path = root / team_source[key]
    if not path.is_file():
        raise SystemExit(f"ERROR: existing Git image reference is missing: {team_source[key]}")

print("River Rats editor initial state validated: 16 players, 9 staff, 4 news; HockeyData protected")

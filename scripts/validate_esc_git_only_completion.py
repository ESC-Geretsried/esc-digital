#!/usr/bin/env python3
"""Validate the ESC Git-only roster/media/runtime completion contract."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
EDITOR = ROOT / "content/.orp-editor"
TEAM_KEYS = ("damen", "u20", "u17", "u15", "u13", "u11", "u9", "u7")
TEAM_ROUTES = {
    "damen": "river-rats-damen",
    "u20": "u20", "u17": "u17", "u15": "u15", "u13": "u13",
    "u11": "u11", "u9": "u9", "u7": "u7",
}


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_records(kind: str) -> list[dict]:
    rows = []
    for path in sorted((EDITOR / kind).glob("*.json")):
        row = json.loads(path.read_text(encoding="utf-8"))
        expected = hashlib.sha256(str(row.get("record_id", "")).encode("utf-8")).hexdigest() + ".json"
        if path.name != expected:
            fail(f"{kind} filename is not bound to record_id: {path.name}")
        rows.append(row)
    return rows


subprocess.run(["python3", str(ROOT / "scripts/sync_founder_team_rosters.py")], check=True)
runtime = json.loads((ROOT / "config/editor-runtime.json").read_text(encoding="utf-8"))
if runtime.get("content_provider") != "git" or runtime.get("binary_asset_provider") != "git-repository":
    fail("ESC website/editor content and media providers are not Git-only")
if runtime.get("identity_provider") != "microsoft-entra" or "server-side-scopes" not in runtime.get("authorization_model", ""):
    fail("Entra identity/server-side RBAC boundary is missing")
if runtime.get("required_content_and_media_dependencies") != ["git"]:
    fail("a non-Git content/media dependency is still required")

teams = []
source_roster = Counter()
for key in TEAM_KEYS:
    path = ROOT / "content/teams" / key / "team.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    teams.append(data)
    if data.get("team_key") != key or data.get("source", {}).get("status") != "founder-provided":
        fail(f"canonical team provenance missing for {key}")
    photo = ROOT / data["team_photo"]
    if not photo.is_file():
        fail(f"verified team photo missing for {key}: {data['team_photo']}")
    route_source = ROOT / "content" / TEAM_ROUTES[key] / "_index.md"
    if not route_source.is_file():
        fail(f"canonical team route source missing for {key}")
    for row in data["roster"]:
        source_roster[(key, row["position_code"], str(row["number"]), row["name"])] += 1

if sum(source_roster.values()) != 268:
    fail(f"expected 268 exact Founder roster rows, got {sum(source_roster.values())}")

editor_teams = {row.get("team_key"): row for row in load_records("teams") if row.get("team_key") in TEAM_KEYS}
editor_areas = {row.get("area_key"): row for row in load_records("areas") if row.get("area_key") in TEAM_KEYS}
editor_pages = {row.get("team_key"): row for row in load_records("pages") if row.get("team_key") in TEAM_KEYS}
if set(editor_teams) != set(TEAM_KEYS) or set(editor_areas) != set(TEAM_KEYS) or set(editor_pages) != set(TEAM_KEYS):
    fail("all eight teams must have Area, Team and Page editor records")

editor_roster = Counter()
for row in load_records("players"):
    key = row.get("team_key")
    if key in TEAM_KEYS:
        editor_roster[(key, row.get("position"), str(row.get("jersey_number")), row.get("display_name"))] += 1
if editor_roster != source_roster:
    fail("Editor player projection differs from exact Founder roster rows")

for key, route in TEAM_ROUTES.items():
    page = ROOT / "site/public" / route / "index.html"
    if page.exists():
        html = page.read_text(encoding="utf-8")
        source = next(team for team in teams if team["team_key"] == key)
        for row in source["roster"]:
            if row["name"] not in html:
                fail(f"public team page {route} omits Founder roster name {row['name']}")
        if source["contact_source_text"].removeprefix("Kontakt: ") and not all(contact["value"] in html for contact in source["contacts"]):
            fail(f"public team page {route} omits Founder contact data")

active_text = "\n".join(
    path.read_text(encoding="utf-8", errors="ignore")
    for base in (ROOT / "site/src", ROOT / "site/scripts")
    for path in base.rglob("*") if path.is_file()
)
if re.search(r"sharepoint|graph\.microsoft", active_text, flags=re.I):
    fail("active website build/runtime source still references a SharePoint content dependency")

print("ESC Git-only completion validation: PASS")
print("Validated: 8 teams, 268 exact Founder rows, Editor projections, Git media paths, Entra/RBAC boundary and active SharePoint independence.")

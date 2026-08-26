#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "docs/content-migration/initial-intake/migration-spec.v1.json"
data = json.loads(path.read_text(encoding="utf-8"))
allowed = {"VERIFIZIERT", "ZU VERIFIZIEREN", "FEHLT", "WIDERSPRUCH", "NICHT MIGRIEREN"}
assert data["implementation_ready"] is False
assert all(v in {"NONE", "NO"} for v in data["mutation_guards"].values())
required_pages = {"homepage","river-rats","damen","nachwuchs","u20","u17","u15","u13","u11","u9","u7","eislaufschule","eiskunstlauf","inklusion","verein","foerderverein","sponsoren","impressum","datenschutz"}
assert required_pages <= {p["key"] for p in data["pages"]}
for group in ["pages","teams","sport_data","media_downloads","sponsors","news","legal","social_video","acceptance","open_points"]:
    for row in data[group]:
        if "status" in row: assert row["status"] in allowed, (group,row)
teams = {t["display_name"]:t for t in data["teams"]}
assert set(teams) == {"River Rats","Damen","U20","U17","U15","U13","U11","U9","U7"}
for name,t in teams.items():
    assert t["target_sections"][1:4] == ["ÜBERSICHT","TEAMFOTO","MANNSCHAFT / KADER"]
    assert ("TABELLE" in t["target_sections"]) == (name not in {"U11","U9","U7"})
sports = {s["team_key"]:s for s in data["sport_data"]}
assert sports["river-rats"]["provider_required"] and sports["river-rats"]["binding_protected"]
for key in {"damen","u20","u17","u15","u13"}: assert not sports[key]["provider_required"]
for key in {"u11","u9","u7"}: assert sports[key]["table_source"] == "NICHT VORHANDEN"
allowed_news = {"river-rats","eiskunstlauf","u13"}
for n in data["news"]:
    if n["decision"] == "MIGRIEREN": assert n["area"] in allowed_news
assert len(data["sponsors"]) == 47
assert len({s["sponsor_key"] for s in data["sponsors"]}) == 47
assert all(s["source_link"] and s["source_image_sha256"] and s["logo_verified"] for s in data["sponsors"])
assert any(s["display_name"] == "Josef Mayr Bauunternehmen" and s["status"] == "WIDERSPRUCH" for s in data["sponsors"])
assert any(m["area"] == "U11" and m["status"] == "VERIFIZIERT" for m in data["media_downloads"])
assert any(m["area"] == "Damen" and "rename planned" in m["notes"] for m in data["media_downloads"])
assert {a["person"] for a in data["acceptance"]} == {"Jens Neuhaus","Hannes Köhler","Kevin Olivo","Tanja Serr","Dieter Krampert","Matthias Remde"}
assert all(a["entra_action"] == "NONE" for a in data["acceptance"])
assert {x["category"][:2] for x in data["legal"] if x["page"] == "datenschutz"} == {f"{c})" for c in "ABCDEFGHI"}
print("ESC content migration intake: OK")

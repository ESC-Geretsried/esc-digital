#!/usr/bin/env python3
import csv
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
base = root / "docs/content-migration/initial-intake"
data = json.loads((base / "migration-spec.v1.json").read_text(encoding="utf-8"))
schema = json.loads((base / "migration-spec.schema.json").read_text(encoding="utf-8"))
print("JSON parse: OK")

def schema_check(value, rule, path="$"):
    expected = rule.get("type")
    types = {"object": dict, "array": list, "string": str, "boolean": bool, "number": (int, float)}
    if expected:
        assert isinstance(value, types[expected]) and not (expected == "number" and isinstance(value, bool)), (path, expected)
    if "const" in rule:
        assert value == rule["const"], (path, value, rule["const"])
    if isinstance(value, dict):
        for key in rule.get("required", []):
            assert key in value, f"{path}.{key} missing"
        for key, child in rule.get("properties", {}).items():
            if key in value:
                schema_check(value[key], child, f"{path}.{key}")
    if isinstance(value, list):
        assert len(value) >= rule.get("minItems", 0), path
        if "maxItems" in rule:
            assert len(value) <= rule["maxItems"], path
        if "contains" in rule:
            found = False
            for index, item in enumerate(value):
                try:
                    schema_check(item, rule["contains"], f"{path}[{index}]")
                    found = True
                    break
                except AssertionError:
                    pass
            assert found, f"{path} contains"

schema_check(data, schema)
print("JSON Schema validation: OK")

def flat(value):
    if isinstance(value, bool): return "YES" if value else "NO"
    if isinstance(value, list): return " | ".join(str(x) for x in value if x != "")
    if isinstance(value, dict): return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return "" if value is None else str(value)

csv_map = {
    "pages.csv":"pages", "teams.csv":"teams", "sport-data.csv":"sport_data",
    "media-downloads.csv":"media_downloads", "sponsors.csv":"sponsors", "news.csv":"news",
    "legal.csv":"legal", "social-video.csv":"social_video", "acceptance.csv":"acceptance",
    "open-points.csv":"open_points", "resolved-decisions.csv":"resolved_decisions",
}
for filename, key in csv_map.items():
    with (base / filename).open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        actual = list(reader)
        headers = reader.fieldnames or []
    expected = [{column: flat(row.get(column, "")) for column in headers} for row in data[key]]
    assert actual == expected, filename
print("CSV/JSON consistency: OK")

allowed = {"VERIFIZIERT", "ZU VERIFIZIEREN", "FEHLT", "WIDERSPRUCH", "NICHT MIGRIEREN"}
gate_classes = {"BLOCKS INITIAL TECHNICAL SEED", "BLOCKS EDITOR ACCEPTANCE", "BLOCKS FINAL GO-LIVE", "CAN REMAIN TO VERIFY DURING INITIAL SEED"}
assert all(v in {"NONE", "NO"} for v in data["mutation_guards"].values())
assert data["readiness"]["initial_seed"]["ready"] is True and data["readiness"]["initial_seed"]["blockers"] == []
assert data["readiness"]["editor_acceptance"]["ready"] is False
assert data["readiness"]["final_golive"]["ready"] is False
assert not any(p["blocks_initial_technical_seed"] for p in data["open_points"])
assert all(p["gate_class"] in gate_classes for p in data["open_points"])
assert all(p["classification"] in allowed for p in data["open_points"])
for group in ["resolved_decisions","pages","teams","sport_data","media_downloads","sponsors","news","legal","social_video","acceptance"]:
    for row in data[group]:
        if "status" in row: assert row["status"] in allowed, (group, row)

required_pages = {"homepage","river-rats","damen","nachwuchs","u20","u17","u15","u13","u11","u9","u7","eislaufschule","eiskunstlauf","inklusion","verein","foerderverein","sponsoren","impressum","datenschutz"}
page_map = {p["key"]:p for p in data["pages"]}
assert required_pages <= set(page_map)
assert page_map["river-rats"]["status"] == "VERIFIZIERT"
assert page_map["foerderverein"]["path"] == "/foerderverein/" and page_map["foerderverein"]["status"] != "WIDERSPRUCH"

teams = {t["display_name"]:t for t in data["teams"]}
assert set(teams) == {"River Rats","Damen","U20","U17","U15","U13","U11","U9","U7"}
for name, team in teams.items():
    assert team["target_sections"][1:4] == ["ÜBERSICHT","TEAMFOTO","MANNSCHAFT / KADER"]
    assert ("TABELLE" in team["target_sections"]) == (name not in {"U11","U9","U7"})
assert teams["River Rats"]["status"] == "VERIFIZIERT"

sports = {s["team_key"]:s for s in data["sport_data"]}
assert sports["river-rats"]["provider_required"] and sports["river-rats"]["binding_protected"]
for key in {"damen","u20","u17","u15","u13"}: assert not sports[key]["provider_required"]
for key in {"u11","u9","u7"}: assert sports[key]["table_source"] == "NICHT VORHANDEN"

allowed_news = {"river-rats","eiskunstlauf","u13"}
for item in data["news"]:
    if item["decision"] == "MIGRIEREN": assert item["area"] in allowed_news
    if item["area"] not in allowed_news: assert item["decision"] == "NICHT MIGRIEREN"

assert len(data["sponsors"]) == 47 == len({s["sponsor_key"] for s in data["sponsors"]})
assert all(s["source_link"] and s["source_image_sha256"] and s["logo_verified"] for s in data["sponsors"])
assert all(s["publication_decision"] == "NOT MADE BY INTAKE" for s in data["sponsors"])
for sponsor in data["sponsors"]:
    if not sponsor["link_verified"]:
        assert sponsor["link_fail_safe"] == "DO NOT PUBLISH UNVERIFIED LINK"
assert any(s["display_name"] == "Josef Mayr Bauunternehmen" and s["status"] == "WIDERSPRUCH" for s in data["sponsors"])

u11 = next(m for m in data["media_downloads"] if m["area"] == "U11")
damen = next(m for m in data["media_downloads"] if m["area"] == "Damen")
assert u11["status"] == "VERIFIZIERT" and u11["verified"] is True
assert damen["status"] == "VERIFIZIERT" and damen["rename_planned"] is True and damen["content_change_allowed"] is False

scopes = [a for a in data["acceptance"] if a["record_type"] == "acceptance_scope"]
defects = {a["issue_number"]:a for a in data["acceptance"] if a["record_type"] == "acceptance_defect"}
assert {a["person"] for a in scopes} == {"Jens Neuhaus","Hannes Köhler","Kevin Olivo","Tanja Serr","Dieter Krampert","Matthias Remde"}
assert set(defects) == {34,35}
assert defects[34]["real_acceptance_status"] == "DEFECT OPEN"
assert defects[34]["evidence_status"] == "VERIFIZIERT" and defects[34]["resolution_status"] == "OFFEN"
assert defects[35]["implementation_status"] == "IMPLEMENTED"
assert defects[35]["automated_test_status"] == "PASS"
assert defects[35]["real_acceptance_status"] == "DEFECT OPEN"
assert defects[35]["evidence_status"] == "VERIFIZIERT" and defects[35]["resolution_status"] == "OFFEN"
assert all(a["entra_action"] == "NONE" for a in data["acceptance"])

resolved = {r["key"] for r in data["resolved_decisions"]}
assert resolved == {"HQ-R01","HQ-R02","HQ-R03","HQ-R04","HQ-R05"}
assert not {"OP-001","OP-003","OP-004"} & {p["key"] for p in data["open_points"]}
assert data["pr33_relation"]["head_sha"] == "f163825748e05bdc25b2272920360ea75ee3b4e4"
assert data["pr33_relation"]["merged"] is False and data["pr33_relation"]["visual_acceptance_pending"] is True
assert {x["category"][:2] for x in data["legal"] if x["page"] == "datenschutz"} == {f"{c})" for c in "ABCDEFGHI"}
print("Intake invariants: OK")
print("Status/gate consistency: OK")

secret_patterns = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\b(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"(?i)(?:api[_-]?key|access_token|client_secret|password)\s*=\s*[^\s&]+"),
]
for candidate in list(base.glob("*")) + [Path(__file__)]:
    if not candidate.is_file(): continue
    text = candidate.read_text(encoding="utf-8")
    for pattern in secret_patterns:
        assert not pattern.search(text), (candidate, pattern.pattern)
print("Secret scan: OK")
print("ESC content migration intake: OK")

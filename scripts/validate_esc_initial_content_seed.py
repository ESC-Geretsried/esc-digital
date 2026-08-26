#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse
from uuid import NAMESPACE_URL, uuid5


root = Path(__file__).resolve().parents[1]
editor = root / "content" / ".orp-editor"
manifest_path = editor / "initial-seed-manifest.v1.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
intake_path = root / "docs" / "content-migration" / "initial-intake" / "migration-spec.v1.json"
intake = json.loads(intake_path.read_text(encoding="utf-8"))

assert manifest["schema_version"] == 1
assert manifest["issue"] == 37
assert manifest["base_main_sha"] == "942426e1a6a3a8bf6e35cd99ecf06feab668b420"
assert manifest["intake_pr"] == 36
assert manifest["intake_head_sha"] == "bc817f887f42f4c1f8cfa3b68a2d65bd895b0f1a"
assert manifest["record_counts"] == {"areas": 9, "blocks": 15, "pages": 9, "teams": 8}

scopes = manifest["scopes"]
scope_keys = set(scopes)
team_keys = {key for key, scope in scopes.items() if scope["team_record"]}
linked_team_keys = {key for key in team_keys if scopes[key]["official_sport_source_url"]}
manual_team_keys = team_keys - linked_team_keys
assert scope_keys == {"damen", "nachwuchs", "u20", "u17", "u15", "u13", "u11", "u9", "u7"}
assert team_keys == {"damen", "u20", "u17", "u15", "u13", "u11", "u9", "u7"}
assert linked_team_keys == {"damen", "u20", "u17", "u15", "u13"}
assert manual_team_keys == {"u11", "u9", "u7"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


for source in manifest["sources"]:
    path = root / source["path"]
    assert path.is_file(), f"missing bound source: {source['path']}"
    assert sha256(path) == source["sha256"], f"source digest drift: {source['path']}"
print("Initial-seed source digests: OK")

assert intake["repositories"]["esc"]["base_sha"] == manifest["base_main_sha"]
assert intake["pr33_relation"]["head_sha"] == "f163825748e05bdc25b2272920360ea75ee3b4e4"
assert intake["pr33_relation"]["merged"] is False
assert intake["readiness"]["initial_seed"] == {
    "ready": True,
    "blockers": [],
    "safeguards": [
        "Seed only verified/source-derived content",
        "Do not invent missing content, links or assets",
        "Omit unresolved sections/assets/links or keep them draft/unpublished where explicitly authorized",
    ],
}
assert intake["readiness"]["editor_acceptance"]["ready"] is False
assert intake["readiness"]["final_golive"]["ready"] is False

intake_teams = {row["team_key"]: row for row in intake["teams"]}
sport_data = {row["team_key"]: row for row in intake["sport_data"]}
for key in team_keys:
    assert intake_teams[key]["status"] == "VERIFIZIERT"
    assert sport_data[key]["status"] == "VERIFIZIERT" and sport_data[key]["verified"] is True
    assert sport_data[key]["manual_extras"] is True
    expected_url = scopes[key]["official_sport_source_url"]
    if key in linked_team_keys:
        assert sport_data[key]["provider_required"] is False
        assert {sport_data[key][field] for field in ("schedule_source", "results_source", "table_source")} == {expected_url}
    else:
        assert sport_data[key]["provider_class"] == "manual"
        assert sport_data[key]["table_source"] == "NICHT VORHANDEN"
        assert expected_url == ""
print("Initial-seed intake mapping: OK")


def universal_id(kind: str, area_key: str, identity: str) -> str:
    context = area_key if kind == "blocks" else ""
    identity_name = json.dumps(["tenant:esc", kind, context, identity], ensure_ascii=False, separators=(",", ":"))
    return f"orp:{kind}:{uuid5(NAMESPACE_URL, identity_name)}"


def records(kind: str) -> list[tuple[Path, dict]]:
    result = []
    directory = editor / kind
    if not directory.exists():
        return result
    for path in sorted(directory.glob("*.json")):
        row = json.loads(path.read_text(encoding="utf-8"))
        expected_name = hashlib.sha256(row["record_id"].encode()).hexdigest() + ".json"
        assert path.name == expected_name, f"record filename does not bind record_id: {path}"
        result.append((path, row))
    return result


all_records: dict[str, list[tuple[Path, dict]]] = {
    kind: records(kind)
    for kind in ("areas", "blocks", "pages", "teams", "players", "staff", "schedule", "news", "events", "people", "downloads", "media")
}
record_ids = [row["record_id"] for rows in all_records.values() for _, row in rows]
assert len(record_ids) == len(set(record_ids)), "duplicate record_id"

seed_records = {
    "areas": [(path, row) for path, row in all_records["areas"] if row.get("area_key") in scope_keys],
    "blocks": [(path, row) for path, row in all_records["blocks"] if row.get("area_key") in scope_keys],
    "pages": [(path, row) for path, row in all_records["pages"] if row.get("area_key") in scope_keys],
    "teams": [(path, row) for path, row in all_records["teams"] if row.get("team_key") in team_keys],
}
assert {kind: len(rows) for kind, rows in seed_records.items()} == manifest["record_counts"]

for kind in ("players", "staff", "schedule", "news", "events", "people", "downloads", "media"):
    for _, row in all_records[kind]:
        assigned = {row.get("area_key", ""), row.get("team_key", "")}
        assigned.update(row.get("area_keys", []) if isinstance(row.get("area_keys"), list) else [])
        assigned.update(row.get("team_keys", []) if isinstance(row.get("team_keys"), list) else [])
        assert not (scope_keys & assigned), f"unapproved {kind} record in initial-seed scope: {row.get('record_id')}"

reviewed_at = manifest["reviewed_at"]
for kind, rows in seed_records.items():
    for _, row in rows:
        assert row["status"] == "draft"
        assert row["source_provider"] == "orp-editor"
        assert row["source_owner"] == "ESC Redaktion"
        assert row["approval_owner"] == "ESC Redaktion"
        assert row["source_record_id"] == row["record_id"]
        assert row["source_updated_at"] == reviewed_at == row["last_reviewed_at"]

areas = {row["area_key"]: row for _, row in seed_records["areas"]}
pages = {row["area_key"]: row for _, row in seed_records["pages"]}
teams = {row["team_key"]: row for _, row in seed_records["teams"]}
blocks: dict[str, dict[str, dict]] = {}
for _, row in seed_records["blocks"]:
    blocks.setdefault(row["area_key"], {})[row["block_key"]] = row

for key, scope in scopes.items():
    area = areas[key]
    assert area["record_id"] == universal_id("areas", "", key)
    assert area["identity_namespace"] == "tenant:esc"
    assert (area["title"], area["summary"], area["public_path"]) == (scope["title"], scope["summary"], scope["public_path"])

    page = pages[key]
    assert page["record_id"] == f"orp:esc-main:pages:{key}"
    assert page["page_key"] == key and page["page_type"] == key
    assert page["title"] == scope["title"]
    assert page["body"] == page["summary"] == scope["summary"]
    assert page["public_path"] == scope["public_path"]
    assert page["team_key"] == (key if scope["team_record"] else "")
    assert page["hero_asset_key"] == ""

    overview = blocks[key]["overview"]
    assert overview["record_id"] == universal_id("blocks", key, "overview")
    assert overview["block_type"] == "text" and overview["sort_order"] == 10
    assert overview["title"] == "Übersicht" and overview["body"] == scope["summary"]

    source_entries = [source for source in manifest["sources"] if key in source["scope_keys"] and source["path"].startswith("imports/")]
    if source_entries:
        source_text = (root / source_entries[0]["path"]).read_text(encoding="utf-8")
        assert scope["summary"] in source_text
        assert not scope["subtitle"] or scope["subtitle"] in source_text

for key, team in teams.items():
    scope = scopes[key]
    official_url = scope["official_sport_source_url"]
    assert team["record_id"] == f"orp:esc-main:teams:{key}"
    assert team["title"] == scope["title"] and team["type"] == "team"
    assert team["public_url"] == f"https://www.esc-geretsried.de/{key}/"
    assert team["navigation_group"] == "Sport"
    assert team["subtitle"] == scope["subtitle"]
    assert team["short_description"] == scope["summary"]
    assert team["hero_asset_key"] == team["team_photo_asset_key"] == ""
    assert team["sports_provider"] == ""
    assert team["league_schedule_embed_url"] == team["league_table_embed_url"] == ""
    assert team["league_schedule_url"] == team["league_table_url"] == official_url
    assert team["navigation"] == (["Spielplan", "Tabelle"] if official_url else [])
    for forbidden in ("league_results_url", "api_binding", "league_binding", "division_binding", "hockeydata_config", "gamepitch_binding"):
        assert forbidden not in team

for key in linked_team_keys:
    link_block = blocks[key]["official-sport-links"]
    official_url = scopes[key]["official_sport_source_url"]
    assert link_block["record_id"] == universal_id("blocks", key, "official-sport-links")
    assert link_block["block_type"] == "links" and link_block["sort_order"] == 60
    assert link_block["body"] == f"[Spielplan]({official_url})\n\n[Ergebnisse]({official_url})\n\n[Tabelle]({official_url})"
for key in manual_team_keys:
    assert set(blocks[key]) == {"overview"}

nachwuchs_links = blocks["nachwuchs"]["team-links"]
assert nachwuchs_links["record_id"] == universal_id("blocks", "nachwuchs", "team-links")
assert nachwuchs_links["block_type"] == "links" and nachwuchs_links["sort_order"] == 20
expected_internal = {"/u20/", "/u17/", "/u15/", "/u13/", "/u11/", "/u9/", "/u7/", "/eislaufschule/"}
assert set(re.findall(r"\]\((/[^)]+)\)", nachwuchs_links["body"])) == expected_internal
print("Initial-seed records, IDs and scopes: OK")

allowed_external_urls = {
    scope["official_sport_source_url"] for scope in scopes.values() if scope["official_sport_source_url"]
} | {f"https://www.esc-geretsried.de/{key}/" for key in team_keys}
for kind, rows in seed_records.items():
    for path, row in rows:
        serialized = path.read_text(encoding="utf-8")
        for url in re.findall(r"https://[^\s\]\)\"']+", serialized):
            parsed = urlparse(url)
            assert parsed.scheme == "https" and parsed.netloc
            assert url in allowed_external_urls, f"unapproved URL in {path}: {url}"
        for field, value in row.items():
            if field.endswith("asset_key"):
                assert value == "", f"invented asset key in {path}: {field}"
        visible = " ".join(str(row.get(field, "")) for field in ("title", "summary", "body", "short_description", "subtitle")).casefold()
        for phrase in ("für die int-migration", "im int-stand", "orp editor", "folgt nach", "datenanbindung", "redaktioneller freigabe"):
            assert phrase not in visible, f"technical/unverified wording in {path}: {phrase}"
print("Initial-seed URL, asset-key and source-purity checks: OK")

allowed_historical_news = {"river-rats", "u13", "eiskunstlauf"}
for _, row in all_records["news"]:
    assert row.get("area_key") in allowed_historical_news
    assert row.get("area_key") not in {"u13", "eiskunstlauf"}, "unverified historical news entered the initial seed"

u11 = manifest["u11_reconciliation"]
assert u11 == {
    "performed": False,
    "verified_source_name": "Geretsried_25-266.jpg",
    "reason": "The exact U11 binary is not present in canonical Git and PR #33 owns the supported homepage rotation implementation; no hotlink, asset key or binary was invented.",
}

hockeydata = root / "content" / "river-rats" / "hockeydata.json"
assert sha256(hockeydata) == "4e6240ec91ead4414dacf9728b0edce03a3fdac87114c0ab0a79ba0bedbe05c4"
river_rats_team = next(row for _, row in all_records["teams"] if row.get("team_key") == "river-rats")
assert river_rats_team["sports_provider"] == "hockeydata"
assert river_rats_team["record_id"] == "orp:esc-main:teams:river-rats"
print("River Rats and HockeyData protection: OK")

secret_patterns = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\b(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"(?i)(?:api[_-]?key|access_token|client_secret|password)\s*=\s*[^\s&]+"),
]
for candidate in [manifest_path, Path(__file__)] + [path for rows in seed_records.values() for path, _ in rows]:
    text = candidate.read_text(encoding="utf-8")
    for pattern in secret_patterns:
        assert not pattern.search(text), (candidate, pattern.pattern)
print("Initial-seed secret scan: OK")
print("ESC initial content seed: OK")

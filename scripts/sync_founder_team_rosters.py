#!/usr/bin/env python3
"""Project the founder-provided 2025/2026 rosters into Git-owned content.

The Markdown source stays the human-readable evidence record. This script is a
deterministic projection into canonical website JSON and ORP Editor records.
It never corrects names, numbers, position codes, contact text or duplicates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import unicodedata


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/content-migration/founder-team-rosters-2025-2026.md"
EDITOR = ROOT / "content/.orp-editor"
TEAM_KEYS = {
    "Damen": ("damen", "river-rats-damen", "/river-rats-damen/", "images/teams/damen-team.jpg"),
    "U20": ("u20", "u20", "/u20/", "images/teams/u20-team.jpg"),
    "U17": ("u17", "u17", "/u17/", "images/teams/u17-team.jpg"),
    "U15": ("u15", "u15", "/u15/", "images/teams/u15-team.jpg"),
    "U13": ("u13", "u13", "/u13/", "images/teams/u13-team.jpg"),
    "U11": ("u11", "u11", "/u11/", "images/teams/u11-team.jpg"),
    "U9": ("u9", "u9", "/u9/", "images/teams/u9-team.jpg"),
    "U7": ("u7", "u7", "/u7/", "images/teams/u7-team.jpg"),
}
SOURCE_REFERENCE = "docs/content-migration/founder-team-rosters-2025-2026.md"
SOURCE_DATE = "2026-08-26"
SOURCE_TIMESTAMP = "2026-08-26T00:00:00Z"
MANAGED_PREFIX = "orp:founder:esc:"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def slug(value: str) -> str:
    replacements = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss"})
    normalized = unicodedata.normalize("NFKD", value.translate(replacements))
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-") or "record"


def bound_path(kind: str, record_id: str) -> Path:
    return EDITOR / kind / (hashlib.sha256(record_id.encode("utf-8")).hexdigest() + ".json")


def parse_source() -> list[dict]:
    text = SOURCE.read_text(encoding="utf-8")
    heading_re = re.compile(r"^## (Damen|U20|U17|U15|U13|U11|U9|U7)$", re.M)
    matches = list(heading_re.finditer(text))
    if [m.group(1) for m in matches] != list(TEAM_KEYS):
        fail("founder roster headings changed or are out of order")

    teams = []
    for index, match in enumerate(matches):
        title = match.group(1)
        body = text[match.end(): matches[index + 1].start() if index + 1 < len(matches) else len(text)].strip()
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        if not lines or not lines[0].startswith("Kontakt: "):
            fail(f"{title}: exact Kontakt line missing")
        contact_text = lines[0][len("Kontakt: "):]
        if contact_text.endswith("."):
            contact_text = contact_text[:-1]
        contacts = []
        for segment in contact_text.split("; "):
            role, separator, value = segment.partition(" ")
            if not separator or role not in {"Trainer", "Betreuer", "Teamleiter", "Email", "Telefon"}:
                fail(f"{title}: unsupported contact segment {segment!r}")
            contacts.append({"role": role, "value": value})

        roster = []
        for line in lines[1:]:
            if line == "Roster (Pos | Nr | Name):":
                continue
            roster_match = re.fullmatch(r"([TVS])\|([^|]+)\|(.+)", line)
            if not roster_match:
                fail(f"{title}: invalid exact roster line {line!r}")
            roster.append({
                "position_code": roster_match.group(1),
                "number": roster_match.group(2),
                "name": roster_match.group(3),
                "source_line": line,
            })
        if not roster:
            fail(f"{title}: roster is empty")

        team_key, content_dir, public_path, photo = TEAM_KEYS[title]
        teams.append({
            "schema_version": 1,
            "team_key": team_key,
            "title": title,
            "season": "2025/2026",
            "public_path": public_path,
            "team_photo": photo,
            "team_photo_alt": f"Teamfoto {title} Saison 2025/2026",
            "contact_source_text": lines[0],
            "contacts": contacts,
            "roster": roster,
            "source": {
                "status": "founder-provided",
                "reference": SOURCE_REFERENCE,
                "provided_at": SOURCE_DATE,
                "rule": "Exact projection; no silent normalization, correction or inference.",
            },
            "_content_dir": content_dir,
        })
    return teams


def json_bytes(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def markdown_bytes(team: dict) -> bytes:
    data = {key: value for key, value in team.items() if not key.startswith("_")}
    front_matter = [
        "---",
        f'title: "{data["title"]}"',
        f'description: "Mannschaft, Kader und Kontakte {data["title"]} · Saison {data["season"]}"',
        'type: "team"',
        'layout: "list"',
        f'team_key: "{data["team_key"]}"',
        'content_status: "preview"',
        'source_status: "founder-provided"',
        "---",
        "",
        "Die Daten dieser Preview-Seite stammen aus der in Git gesicherten Founder-Quelle.",
        "",
    ]
    return "\n".join(front_matter).encode("utf-8")


def technical(record_id: str) -> dict:
    return {
        "record_id": record_id,
        "source_provider": "orp-editor",
        "source_record_id": record_id,
        "source_owner": "ESC Redaktion",
        "source_updated_at": SOURCE_TIMESTAMP,
        "last_reviewed_at": SOURCE_TIMESTAMP,
        "approval_owner": "ESC Redaktion",
        "source_reference": SOURCE_REFERENCE,
        "source_status": "founder-provided",
    }


def load_editor_records(kind: str) -> list[tuple[Path, dict]]:
    directory = EDITOR / kind
    rows = []
    if not directory.exists():
        return rows
    for path in sorted(directory.glob("*.json")):
        rows.append((path, json.loads(path.read_text(encoding="utf-8"))))
    return rows


def existing_by(kind: str, field: str, value: str) -> tuple[Path, dict] | None:
    matches = [(path, row) for path, row in load_editor_records(kind) if row.get(field) == value]
    if len(matches) > 1:
        fail(f"duplicate existing {kind} records for {field}={value}")
    return matches[0] if matches else None


def page_body(team: dict) -> str:
    lines = [
        f"Saison {team['season']}",
        "",
        team["contact_source_text"],
        "",
        "Kader (Pos | Nr | Name):",
    ]
    lines.extend(row["source_line"] for row in team["roster"])
    return "\n".join(lines)


def editor_records(teams: list[dict]) -> dict[Path, bytes]:
    output: dict[Path, bytes] = {}
    for team in teams:
        key = team["team_key"]
        email = next(item["value"] for item in team["contacts"] if item["role"] == "Email")
        phone = next(item["value"] for item in team["contacts"] if item["role"] == "Telefon")

        current = existing_by("areas", "area_key", key)
        record_id = current[1]["record_id"] if current else f"{MANAGED_PREFIX}areas:{key}"
        path = current[0] if current else bound_path("areas", record_id)
        output[path] = json_bytes({
            "identity_namespace": "tenant:esc", "area_key": key, "title": team["title"],
            "summary": f"{team['title']} · Saison {team['season']}", "public_path": team["public_path"],
            "status": "draft", **technical(record_id),
        })

        current = existing_by("teams", "team_key", key)
        record_id = current[1]["record_id"] if current else f"{MANAGED_PREFIX}teams:{key}"
        path = current[0] if current else bound_path("teams", record_id)
        output[path] = json_bytes({
            "team_key": key, "title": team["title"], "type": "team",
            "public_url": f"https://www.esc-geretsried.de{team['public_path']}",
            "navigation_group": "Nachwuchs" if key != "damen" else "Eishockey",
            "subtitle": f"Saison {team['season']}",
            "short_description": team["contact_source_text"], "hero_asset_key": "",
            "sports_provider": "", "league_schedule_url": "", "league_schedule_embed_url": "",
            "league_table_url": "", "league_table_embed_url": "", "navigation": [],
            "team_photo_repository_path": team["team_photo"], "public_email": email,
            "public_phone": phone, "status": "draft", **technical(record_id),
        })

        current = existing_by("pages", "team_key", key)
        record_id = current[1]["record_id"] if current else f"{MANAGED_PREFIX}pages:{key}"
        path = current[0] if current else bound_path("pages", record_id)
        output[path] = json_bytes({
            "title": team["title"], "page_type": "team", "area_key": key, "team_key": key,
            "body": page_body(team), "summary": f"Kader und Kontakte · Saison {team['season']}",
            "hero_asset_key": "", "public_path": team["public_path"], "status": "draft",
            "page_key": key, **technical(record_id),
        })

        seen_player_ids: set[str] = set()
        for order, player in enumerate(team["roster"], start=1):
            base = f"{MANAGED_PREFIX}players:{key}:{slug(player['name'])}"
            record_id = base
            collision = 2
            while record_id in seen_player_ids:
                record_id = f"{base}-{collision}"
                collision += 1
            seen_player_ids.add(record_id)
            team_role = "OA" if player["name"].endswith(" (OA)") else ""
            output[bound_path("players", record_id)] = json_bytes({
                "team_key": key, "age_group": team["title"], "display_name": player["name"],
                "jersey_number": player["number"], "position": player["position_code"],
                "birth_year": "", "shoots": "", "nationality": "", "height_cm": "",
                "weight_kg": "", "team_role": team_role,
                "comment": f"Exact Founder source line: {player['source_line']}", "rodi_url": "",
                "eliteprospects_url": "", "photo_asset_key": "",
                "status": "draft", **technical(record_id),
            })

        staff_order = 0
        seen_staff_ids: set[str] = set()
        for contact in team["contacts"]:
            if contact["role"] in {"Email", "Telefon"}:
                continue
            # A comma is an explicit separator in the source. "und" is kept
            # untouched because expanding it could invent a surname assignment.
            for display_name in [part.strip() for part in contact["value"].split(",") if part.strip()]:
                staff_order += 10
                base = f"{MANAGED_PREFIX}staff:{key}:{slug(contact['role'])}:{slug(display_name)}"
                record_id = base
                collision = 2
                while record_id in seen_staff_ids:
                    record_id = f"{base}-{collision}"
                    collision += 1
                seen_staff_ids.add(record_id)
                output[bound_path("staff", record_id)] = json_bytes({
                    "team_key": key, "display_name": display_name, "role": contact["role"],
                    "email": "", "phone": "", "sort_order": staff_order,
                    "comment": f"Exact Founder contact group: {contact['role']} {contact['value']}",
                    "photo_asset_key": "", "status": "draft", **technical(record_id),
                })
    return output


def expected_files(teams: list[dict]) -> dict[Path, bytes]:
    output: dict[Path, bytes] = {}
    for team in teams:
        data = {key: value for key, value in team.items() if not key.startswith("_")}
        output[ROOT / "content/teams" / team["team_key"] / "team.json"] = json_bytes(data)
        output[ROOT / "content" / team["_content_dir"] / "_index.md"] = markdown_bytes(team)
    output.update(editor_records(teams))
    return output


def managed_editor_paths() -> set[Path]:
    paths = set()
    for kind in ("areas", "teams", "pages", "players", "staff"):
        for path, row in load_editor_records(kind):
            if str(row.get("record_id", "")).startswith(MANAGED_PREFIX):
                paths.add(path)
    return paths


def check(expected: dict[Path, bytes]) -> None:
    errors = []
    for path, payload in expected.items():
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
        elif path.read_bytes() != payload:
            errors.append(f"drifted {path.relative_to(ROOT)}")
    stale = managed_editor_paths() - set(expected)
    errors.extend(f"stale managed record {path.relative_to(ROOT)}" for path in sorted(stale))
    if errors:
        fail("founder roster projection drift:\n" + "\n".join(errors))


def write(expected: dict[Path, bytes]) -> None:
    stale = managed_editor_paths() - set(expected)
    for path in stale:
        path.unlink()
    for path, payload in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write the deterministic projection")
    args = parser.parse_args()
    teams = parse_source()
    expected = expected_files(teams)
    if args.write:
        write(expected)
    check(expected)
    roster_count = sum(len(team["roster"]) for team in teams)
    print(f"Founder roster projection PASS: {len(teams)} teams, {roster_count} exact roster rows")


if __name__ == "__main__":
    main()

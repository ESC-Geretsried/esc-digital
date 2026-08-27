#!/usr/bin/env python3
"""Validate Founder-confirmed portrait identity bindings without image inference."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
MAPPING = ROOT / "content/verein/vereinsfuehrung/portrait-map.json"
CONTENT = ROOT / "content/verein/vereinsfuehrung/_index.md"
MANIFEST = ROOT / "docs/operations/vereinsfuehrung-portraits-manifest.json"
CHECKSUMS = ROOT / "docs/operations/vereinsfuehrung-portraits.sha256"
EXPECTED_IDS = {
    "esc.person.thomas-gania",
    "esc.person.markus-janka",
    "esc.person.jens-neuhaus",
    "esc.person.stefan-heindl",
    "esc.person.sabrina-kruck",
    "esc.person.ulla-koehler",
    "esc.person.melanie-vollbrecht",
    "esc.person.romy-schiek",
}


def keyed(rows: list[dict], key: str, source: str) -> dict[str, dict]:
    result = {}
    for row in rows:
        value = row.get(key)
        if not value or value in result:
            raise SystemExit(f"ERROR: missing/duplicate {key} in {source}: {value!r}")
        result[value] = row
    return result


mapping = json.loads(MAPPING.read_text(encoding="utf-8"))
if mapping.get("mapping_authority") != "Founder-confirmed identity mapping; never positional or face-derived":
    raise SystemExit("ERROR: portrait mapping authority drift")
by_id = keyed(mapping.get("people", []), "person_id", "portrait-map.json")
if set(by_id) != EXPECTED_IDS:
    raise SystemExit("ERROR: Founder-confirmed 8/8 person_id set drift")

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
manifest_by_id = keyed(manifest.get("assets", []), "person_id", "portrait manifest")
if set(manifest_by_id) != EXPECTED_IDS:
    raise SystemExit("ERROR: portrait manifest person_id set drift")

checksum_by_path = {}
for line in CHECKSUMS.read_text(encoding="utf-8").splitlines():
    digest, path = line.split(maxsplit=1)
    checksum_by_path[path] = digest

frontmatter = CONTENT.read_text(encoding="utf-8").split("---", 2)[1]
blocks = re.findall(r'^  - person_id: "([^"]+)"\n(.*?)(?=^  - person_id:|\Z)', frontmatter, re.MULTILINE | re.DOTALL)
content_by_id = {}
for person_id, block in blocks:
    values = {key: value for key, value in re.findall(r'^    (name|role|image): "([^"]+)"$', block, re.MULTILINE)}
    content_by_id[person_id] = values
if set(content_by_id) != EXPECTED_IDS:
    raise SystemExit("ERROR: Vereinsführung front matter person_id set drift")

for person_id, record in by_id.items():
    required = {"name", "role", "portrait_asset", "sha256"}
    if required - record.keys():
        raise SystemExit(f"ERROR: incomplete portrait mapping for {person_id}")
    asset = ROOT / record["portrait_asset"]
    if not asset.is_file():
        raise SystemExit(f"ERROR: portrait asset missing for {person_id}: {record['portrait_asset']}")
    digest = hashlib.sha256(asset.read_bytes()).hexdigest()
    if digest != record["sha256"] or checksum_by_path.get(record["portrait_asset"]) != digest:
        raise SystemExit(f"ERROR: portrait checksum drift for {person_id}")
    manifest_record = manifest_by_id[person_id]
    if any(manifest_record.get(key) != value for key, value in {
        "person": record["name"], "role": record["role"],
        "path": record["portrait_asset"], "sha256": record["sha256"],
    }.items()):
        raise SystemExit(f"ERROR: portrait manifest identity/path drift for {person_id}")
    if content_by_id[person_id] != {
        "name": record["name"], "role": record["role"], "image": record["portrait_asset"],
    }:
        raise SystemExit(f"ERROR: portrait front matter identity/path drift for {person_id}")

print("Founder-confirmed Vereinsführung portrait identity mapping PASS: 8/8")

#!/usr/bin/env python3
"""Fail-safe validator for ESC issue #37 initial content seed."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDITOR = ROOT / "content" / ".orp-editor"

EXPECTED = {
    "areas": "orp:git-seed:esc:areas:nachwuchs",
    "blocks": "orp:git-seed:esc:blocks:nachwuchs-overview",
    "pages": "orp:git-seed:esc:pages:nachwuchs",
}

FOUNDER_TEXT = (
    "Der Nachwuchsbereich bündelt die Mannschaften U20 bis U7.\n\n"
    "Mannschaften\nU20\nU17\nU15\nU13\nU11\nU9\nU7\n\n"
    "Einstieg ins Eislaufen\n"
    "Die Eislaufschule ist das Einstiegs- und Anfängerangebot des ESC. "
    "Sie ist keine Mannschaft und bleibt als eigener Bereich geführt."
)


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_bound_record(kind: str, record_id: str) -> dict:
    filename = hashlib.sha256(record_id.encode("utf-8")).hexdigest() + ".json"
    path = EDITOR / kind / filename
    if not path.is_file():
        fail(f"missing bound {kind} record {filename}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("record_id") != record_id:
        fail(f"record_id mismatch in {path}")
    return data


def main() -> None:
    records = {kind: load_bound_record(kind, rid) for kind, rid in EXPECTED.items()}

    if records["areas"].get("summary") != "Der Nachwuchsbereich bündelt die Mannschaften U20 bis U7.":
        fail("Nachwuchs area summary drifted from verified intake")
    if records["blocks"].get("body") != FOUNDER_TEXT:
        fail("Nachwuchs block body drifted from verified Founder text")
    if records["pages"].get("body") != FOUNDER_TEXT:
        fail("Nachwuchs page body drifted from verified Founder text")

    for kind, data in records.items():
        if data.get("status") != "draft":
            fail(f"{kind} seed must remain draft")
        for field in ("hero_asset_key", "image_asset_key", "video_url"):
            if data.get(field):
                fail(f"{kind} invents forbidden optional field {field}")
        serialized = json.dumps(data, ensure_ascii=False)
        if "http://" in serialized or "https://" in serialized:
            fail(f"{kind} contains an external URL")
        if "hockeydata" in serialized.lower() or "gamepitch" in serialized.lower():
            fail(f"{kind} contains protected provider binding")

    page = (ROOT / "content" / "nachwuchs" / "_index.md").read_text(encoding="utf-8")
    required = [
        "Der Nachwuchsbereich bündelt die Mannschaften U20 bis U7.",
        "[U20](/u20/)", "[U17](/u17/)", "[U15](/u15/)",
        "[U13](/u13/)", "[U11](/u11/)", "[U9](/u9/)", "[U7](/u7/)",
        "Die Eislaufschule ist das Einstiegs- und Anfängerangebot des ESC.",
    ]
    for text in required:
        if text not in page:
            fail(f"canonical Nachwuchs page missing verified text: {text}")

    hockey = ROOT / "content" / "river-rats" / "hockeydata.json"
    if not hockey.is_file():
        fail("protected River Rats HockeyData configuration missing")

    print("ESC initial content seed validation: PASS")
    print("Validated: filename/record-id binding, verified Nachwuchs text, draft state,")
    print("no external URLs/asset keys/provider bindings in new records, HockeyData presence.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import tempfile

from enforce_news_retention import expiry_for, filter_home


assert expiry_for(date(2025, 8, 26), 12) == date(2026, 8, 26)
assert expiry_for(date(2024, 2, 29), 12) == date(2025, 2, 28)
assert expiry_for(date(2025, 12, 31), 12) == date(2026, 12, 31)

fixture = {
    "news_groups": [{
        "title": "Test",
        "items": [
            {"title": "expired", "path": "/aktuelles/2025-08-26-expired/"},
            {"title": "retained", "path": "/aktuelles/2025-08-27-retained/"},
        ],
        "homepage_items": [
            {"title": "expired", "path": "/aktuelles/2025-08-26-expired/"},
            {"title": "retained", "path": "/aktuelles/2025-08-27-retained/"},
        ],
    }]
}
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "home.json"
    source = json.dumps(fixture, ensure_ascii=False, indent=2) + "\n"
    path.write_text(source, encoding="utf-8")
    assert filter_home(path, date(2026, 8, 26), 12) == 2
    projected = json.loads(path.read_text(encoding="utf-8"))
    assert [row["title"] for row in projected["news_groups"][0]["items"]] == ["retained"]
    assert [row["title"] for row in projected["news_groups"][0]["homepage_items"]] == ["retained"]
    assert source == json.dumps(fixture, ensure_ascii=False, indent=2) + "\n"

print("12-month news retention boundary and source-preserving projection validated")

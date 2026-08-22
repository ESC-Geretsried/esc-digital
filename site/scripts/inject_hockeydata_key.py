#!/usr/bin/env python3
import json
import os
from pathlib import Path

root = Path(__file__).resolve().parents[2]
page = root / "site" / "public" / "river-rats" / "index.html"
text = page.read_text(encoding="utf-8")
key = os.environ.get("HOCKEYDATA_API_KEY", "").strip()
value = key if key else "VOID"
# JSON-escape the value because it is embedded inside data-hd-widget-options.
escaped = json.dumps(value)[1:-1]
text = text.replace("__HOCKEYDATA_API_KEY__", escaped)
page.write_text(text, encoding="utf-8")
print("HockeyData widget key injected" if key else "HockeyData widget key unavailable; built with VOID fallback")

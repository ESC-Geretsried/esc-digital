#!/usr/bin/env python3
import json
from pathlib import Path


root = Path(__file__).resolve().parents[2]
data = json.loads((root / "content" / "home" / "announcements.json").read_text(encoding="utf-8"))
template = (root / "site" / "src" / "layouts" / "_default" / "baseof.html").read_text(encoding="utf-8")
legacy_template = (root / "site" / "src" / "layouts" / "baseof.html").read_text(encoding="utf-8")
css = (root / "site" / "src" / "assets" / "css" / "announcement.css").read_text(encoding="utf-8")

assert data["rotation"] == "sequential-slow"
assert data["reduced_motion"] == "first-message-static"
assert isinstance(data["messages"], list) and data["messages"]
assert len({item["id"] for item in data["messages"]}) == len(data["messages"])
assert len({item["order"] for item in data["messages"]}) == len(data["messages"])

first = sorted((item for item in data["messages"] if item.get("active")), key=lambda item: item["order"])[0]
assert first["url"] == "https://esc-geretsried.github.io/bestellung/"
assert first["new_tab"] is True

assert template == legacy_template
assert 'announcement-ticker__track is-rotating' in template
assert '--announcement-duration: {{ mul (len $announcements) 56 }}s' in template
assert template.count('class="announcement-ticker__sequence"') == 2
assert '{{ range (sort $announcements "order") }}' in template
assert '{{ if .url }}' in template and '{{ else }}<span' in template
assert 'target="_blank" rel="noopener noreferrer"' in template
assert 'tabindex="-1"' in template
assert "animation: announcement-sequence var(--announcement-duration, 56s) linear infinite" in css
assert "to { transform: translateX(-50%); }" in css
assert "@media (prefers-reduced-motion: reduce)" in css
assert ".announcement-ticker__track { animation: none; }" in css

print("AnnouncementTicker validated: slow continuous sequence, multiple-message renderer, optional links, safe external target, and static reduced-motion fallback")

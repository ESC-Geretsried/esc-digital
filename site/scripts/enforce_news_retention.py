#!/usr/bin/env python3
from datetime import date, datetime
from pathlib import Path
import re
import shutil

root = Path(__file__).resolve().parents[2]
public_news = root / "site" / "public" / "aktuelles"

DATE_PREFIX = re.compile(r"^(\d{4}-\d{2}-\d{2})-")


def expiry_for(published: date) -> date:
    try:
        return published.replace(year=published.year + 2)
    except ValueError:
        # 29 February -> last valid day in February two years later.
        return published.replace(year=published.year + 2, day=28)


def main() -> None:
    if not public_news.exists():
        print("News retention: no public aktuelles directory present")
        return

    today = date.today()
    removed = 0
    checked = 0

    for entry in sorted(public_news.iterdir()):
        if not entry.is_dir():
            continue
        match = DATE_PREFIX.match(entry.name)
        if not match:
            continue

        published = datetime.strptime(match.group(1), "%Y-%m-%d").date()
        checked += 1
        if today >= expiry_for(published):
            shutil.rmtree(entry)
            removed += 1

    print(f"News retention: checked {checked} dated public items, removed {removed} item(s) at >=24 months")


if __name__ == "__main__":
    main()

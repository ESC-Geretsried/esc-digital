#!/usr/bin/env python3
"""Apply the public-news window without mutating canonical Git sources."""
from __future__ import annotations

import argparse
import calendar
from datetime import date, datetime
import json
import os
from pathlib import Path
import re
import shutil
from zoneinfo import ZoneInfo

root = Path(__file__).resolve().parents[2]
public_news = root / "site" / "public" / "aktuelles"
policy_path = root / "config" / "news-retention.json"

DATE_PREFIX = re.compile(r"^(\d{4}-\d{2}-\d{2})-")


def load_policy() -> dict:
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    if policy.get("public_window_months") != 12:
        raise SystemExit("ERROR: public news retention must be exactly 12 months")
    if policy.get("source_retention") != "retain-canonical-and-import-source-in-git":
        raise SystemExit("ERROR: news source-retention guarantee changed")
    return policy


def as_of_date(policy: dict) -> date:
    explicit = os.environ.get("NEWS_RETENTION_AS_OF", "").strip()
    if explicit:
        return datetime.strptime(explicit, "%Y-%m-%d").date()
    return datetime.now(ZoneInfo(policy["policy_timezone"])).date()


def expiry_for(published: date, months: int) -> date:
    month_index = published.year * 12 + published.month - 1 + months
    year, month_zero = divmod(month_index, 12)
    month = month_zero + 1
    day = min(published.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def publication_from_path(path: str) -> date | None:
    match = re.search(r"/(\d{4}-\d{2}-\d{2})-", path)
    return datetime.strptime(match.group(1), "%Y-%m-%d").date() if match else None


def filter_home(path: Path, today: date, months: int) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    removed = 0
    for group in data.get("news_groups", []):
        kept = []
        for item in group.get("items", []):
            published = publication_from_path(item.get("path", ""))
            if published is None:
                kept.append(item)
                continue
            if today >= expiry_for(published, months):
                removed += 1
            else:
                kept.append(item)
        group["items"] = kept
        if not kept and not group.get("empty_text"):
            group["empty_text"] = "Noch keine Meldungen innerhalb der öffentlichen 12-Monats-Ausgabe."
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return removed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--filter-staged-home", type=Path)
    args = parser.parse_args()
    policy = load_policy()
    today = as_of_date(policy)
    months = int(policy["public_window_months"])

    if args.filter_staged_home:
        removed = filter_home(args.filter_staged_home, today, months)
        print(f"News retention: removed {removed} expired homepage item(s) from staged public data as of {today}")
        return

    if not public_news.exists():
        print("News retention: no public aktuelles directory present")
        return

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
        if today >= expiry_for(published, months):
            shutil.rmtree(entry)
            removed += 1

    removed_teasers = 0
    news_index = public_news / "index.html"
    if news_index.is_file():
        html = news_index.read_text(encoding="utf-8")
        article_re = re.compile(r"<article\b.*?</article>", flags=re.S)

        def keep_or_drop(match: re.Match[str]) -> str:
            nonlocal removed_teasers
            article = match.group(0)
            published = publication_from_path(article)
            if published is not None and today >= expiry_for(published, months):
                removed_teasers += 1
                return ""
            return article

        html = article_re.sub(keep_or_drop, html)
        news_index.write_text(html, encoding="utf-8")

    print(f"News retention: checked {checked} dated public items, removed {removed} article(s) and {removed_teasers} index teaser(s) at >=12 months as of {today}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Create a self-contained public snapshot from the ESC WordPress site.

The snapshot is a demo publication adapter: it reads public WordPress HTML,
keeps SharePoint-rendered tables and PDF links, and replaces public Hockeydata
widget placeholders with build-time HTML. No credentials are written to the
artifact.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen


UA = "ESC-Digital-static-demo/1.0"


def fetch(url: str) -> tuple[bytes, str]:
    req = Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urlopen(req, timeout=30) as response:
        return response.read(), response.headers.get_content_type()


def clean_url(url: str, base: str) -> str:
    absolute = urljoin(base, url)
    parts = urlsplit(absolute)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))


def local_path(url: str, output: Path) -> Path:
    path = urlsplit(url).path or "/"
    if path.endswith("/"):
        return output / path.lstrip("/") / "index.html"
    suffix = Path(path).suffix.lower()
    if suffix in {".html", ".htm"}:
        return output / path.lstrip("/")
    return output / path.lstrip("/")


def esc(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def scalar(value: object) -> str:
    if isinstance(value, dict):
        for key in ("value", "text", "html", "longname", "shortname", "name"):
            if value.get(key) is not None:
                return scalar(value[key])
        # Hockeydata has used both flat and nested team objects over time.
        # Resolve the first meaningful display value without copying the raw
        # provider payload into the public artifact.
        for nested in value.values():
            resolved = scalar(nested)
            if resolved:
                return resolved
        return ""
    return "" if value is None else str(value)


def first(row: dict, keys: tuple[str, ...]) -> str:
    for key in keys:
        value = scalar(row.get(key))
        if value:
            return value
    return ""


def hockey_table(payload: dict, standings: bool = False) -> str:
    rows = ((payload.get("data") or {}).get("rows") or [])
    if not rows:
        return '<p class="snapshot-empty">Aktuell liegen keine Daten vor.</p>'
    if standings:
        headers = ("Rang", "Team", "Sp", "Pkt")
        cells = lambda row: (first(row, ("rank", "tableRank", "position")),
                             first(row, ("team", "teamLongname", "teamShortname", "teamName")),
                             first(row, ("games", "gamesPlayed", "played")),
                             first(row, ("points", "pts")))
    else:
        headers = ("Datum", "Zeit", "Heim", "Gast", "Ergebnis")
        def cells(row: dict) -> tuple[str, ...]:
            date = first(row, ("date", "gameDate", "scheduledDate", "gameDay"))
            time = first(row, ("time", "gameTime", "scheduledTime"))
            return (date, time,
                    first(row, ("home", "homeTeamLongname", "homeTeamName", "homeTeam")),
                    first(row, ("away", "awayTeamLongname", "awayTeamName", "awayTeam", "guestTeam")),
                    first(row, ("result", "score", "gameScore", "scoreText")) or "–")
    head = "".join(f"<th scope=\"col\">{esc(item)}</th>" for item in headers)
    body = "".join("<tr>" + "".join(f"<td>{esc(value)}</td>" for value in cells(row)) + "</tr>"
                    for row in rows if isinstance(row, dict))
    return f'<div class="static-data-table"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def api_table(api_key: str, endpoint: str, params: dict[str, str], standings: bool) -> str:
    query = "&".join(f"{key}={urlencode(value)}" for key, value in {"apiKey": api_key, **params}.items())
    raw, _ = fetch(endpoint + "?" + query)
    payload = json.loads(raw.decode("utf-8"))
    if payload.get("statusId") not in (None, 0, 1):
        raise RuntimeError("Hockeydata returned an error status")
    return hockey_table(payload, standings)


def urlencode(value: str) -> str:
    from urllib.parse import quote
    return quote(str(value), safe="")


def replace_hockeydata(page: str, api_key: str) -> str:
    pattern = re.compile(r'<div[^>]+data-esc-gamepitch="(?P<data>[^"]+)"[^>]*>\s*</div>', re.I)

    def repl(match: re.Match[str]) -> str:
        config = json.loads(html.unescape(match.group("data")))
        name = config.get("widgetName", "")
        options = config.get("widgetOptions", {})
        params = {"sport": str(options.get("sport", "icehockey")),
                  "divisionId": str(options.get("divisionId", 21620)),
                  "lang": "de", "referer": "2026.esc-geretsried.de"}
        team_id = options.get("teamId")
        if team_id:
            params["teamId"] = str(team_id)
        if name.endswith("Standings"):
            content = api_table(api_key, "https://api.hockeydata.net/data/ebel/Standings", params, True)
            title = "Tabelle"
        elif name.endswith("Schedule"):
            content = api_table(api_key, "https://api.hockeydata.net/data/ebel/Schedule", params, False)
            title = "Spielplan"
        else:
            content = '<p class="snapshot-empty">Keine statische Datenansicht verfügbar.</p>'
            title = "Spiele"
        return f'<section class="static-data-block"><h2>{title}</h2>{content}</section>'

    return pattern.sub(repl, page)


def rewrite_and_links(page: str, source_url: str, host: str, output: Path, queue: deque[str]) -> str:
    attr = re.compile(r'(?P<prefix>\b(?:href|src)=([\"\']))(?P<url>.*?)(?P<quote>[\"\'])', re.I)

    def repl(match: re.Match[str]) -> str:
        raw = html.unescape(match.group("url"))
        if raw.startswith(("#", "data:", "mailto:", "tel:", "javascript:")):
            return match.group(0)
        absolute = clean_url(raw, source_url)
        parts = urlsplit(absolute)
        if parts.netloc != host:
            return match.group(0)
        target = local_path(absolute, output)
        path = parts.path.lower()
        if not parts.query and not path.startswith(("/wp-", "/feed", "/comments")):
            queue.append(absolute)
        target.parent.mkdir(parents=True, exist_ok=True)
        rel = Path("/") / target.relative_to(output)
        return f'{match.group("prefix")}{html.escape(str(rel), quote=True)}{match.group("quote")}'

    return attr.sub(repl, page)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="https://2026.esc-geretsried.de/")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--hockeydata-key", required=True)
    args = parser.parse_args()
    if not args.hockeydata_key.strip():
        raise SystemExit("ERROR: Hockeydata key is required for a static snapshot")
    source = args.source.rstrip("/") + "/"
    host = urlsplit(source).netloc
    args.output.mkdir(parents=True, exist_ok=True)
    for child in args.output.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    sitemap = clean_url(urljoin(source, "wp-sitemap.xml"), source)
    seed = [source]
    try:
        raw, _ = fetch(sitemap)
        seed.extend(re.findall(r"<loc>(.*?)</loc>", raw.decode("utf-8", "ignore")))
    except Exception:
        pass
    queue: deque[str] = deque(dict.fromkeys(seed))
    seen: set[str] = set()
    while queue and len(seen) < 300:
        url = queue.popleft()
        if url in seen or urlsplit(url).netloc != host:
            continue
        seen.add(url)
        try:
            raw, content_type = fetch(url)
        except Exception as exc:
            print(f"WARN: could not fetch {url}: {exc}", file=sys.stderr)
            continue
        target = local_path(url, args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        if content_type == "text/html" or target.suffix in {".html", ".htm", ""}:
            page = raw.decode("utf-8", "replace")
            page = replace_hockeydata(page, args.hockeydata_key)
            # Remove provider scripts and styles after widget data is embedded.
            page = re.sub(r'<script[^>]+(?:hockeydata|gamepitch)[^>]*>.*?</script>', "", page, flags=re.I | re.S)
            page = re.sub(r'<link[^>]+(?:hockeydata|gamepitch)[^>]*>', "", page, flags=re.I)
            page = rewrite_and_links(page, url, host, args.output, queue)
            target = target if target.suffix in {".html", ".htm"} else target / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(page, encoding="utf-8")
        else:
            target.write_bytes(raw)
    if queue:
        print("WARNING: static snapshot reached the 300-page safety limit", file=sys.stderr)
    if not (args.output / "index.html").exists():
        raise SystemExit("ERROR: static snapshot did not contain a homepage")
    print(f"STATIC_DEMO_SNAPSHOT: {len(seen)} public URLs captured")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

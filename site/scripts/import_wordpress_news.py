#!/usr/bin/env python3
"""Import published WordPress posts into the static ESC build output.

This is deliberately a build-time adapter. It never writes to the repository
and it never leaves WordPress URLs or a runtime API dependency in the public
artifact.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import ssl
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_API = "https://2026.esc-geretsried.de/wp-json/wp/v2"
FLASH_TERMS = {"flashnews", "flash-news", "flash news", "flash_news"}
ALLOWED_TAGS = {"a", "br", "em", "h2", "h3", "h4", "li", "ol", "p", "strong", "ul"}
SKIP_TAGS = {"script", "style", "iframe", "object", "embed", "form", "svg"}


def request_json(url: str, timeout: int = 20) -> tuple[object, dict[str, str]]:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "ESC-Digital-static-build/1.0"})
    with urlopen(request, timeout=timeout, context=ssl.create_default_context()) as response:
        headers = {key.lower(): value for key, value in response.headers.items()}
        return json.loads(response.read().decode("utf-8")), headers


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip()


class ContentSanitizer(HTMLParser):
    def __init__(self, public_root: Path, media_root: Path, media_cache: dict[str, str]) -> None:
        super().__init__(convert_charrefs=True)
        self.public_root = public_root
        self.media_root = media_root
        self.media_cache = media_cache
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in SKIP_TAGS:
            self.skip_depth += 1
            return
        if self.skip_depth or tag not in ALLOWED_TAGS:
            return
        attrs = dict(attrs_list)
        if tag == "a" and attrs.get("href"):
            href = attrs["href"]
            if urlparse(href).scheme not in {"", "http", "https", "mailto", "tel"}:
                return
            self.parts.append(f'<a href="{escape(href, quote=True)}">')
        elif tag == "br":
            self.parts.append("<br>")
        else:
            self.parts.append(f"<{tag}>")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
        elif not self.skip_depth and tag in ALLOWED_TAGS and tag != "br":
            self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(escape(data))

    def html(self) -> str:
        return "".join(self.parts).strip()


def slugify(value: str) -> str:
    value = value.lower().replace("ß", "ss")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "meldung"


def date_parts(value: str) -> tuple[str, str]:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.date().isoformat(), parsed.strftime("%d.%m.%Y")


def download_media(url: str, public_root: Path, media_root: Path, cache: dict[str, str]) -> str | None:
    if not url or url in cache:
        return cache.get(url)
    parsed = urlparse(url)
    suffix = Path(parsed.path).suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        suffix = ".jpg"
    name = f"{len(cache) + 1:04d}-{slugify(Path(parsed.path).stem)}{suffix}"
    target = media_root / name
    try:
        request = Request(url, headers={"User-Agent": "ESC-Digital-static-build/1.0"})
        with urlopen(request, timeout=25, context=ssl.create_default_context()) as response:
            data = response.read()
        if len(data) > 12 * 1024 * 1024:
            return None
        target.write_bytes(data)
    except Exception as exc:  # pragma: no cover - network failures are reported to CI
        print(f"WARNING: WordPress image could not be downloaded: {url} ({exc})")
        return None
    public_path = "/images/news/" + name
    cache[url] = public_path
    return public_path


def sanitize_content(raw: str, public_root: Path, media_root: Path, cache: dict[str, str]) -> str:
    # Images are intentionally removed from the sanitizer input here and added
    # as local assets by the featured-image path. Text remains safe and stable.
    raw = re.sub(r"<img\b[^>]*>", "", raw, flags=re.I)
    parser = ContentSanitizer(public_root, media_root, cache)
    parser.feed(raw)
    return parser.html()


def is_flash(post: dict, categories: dict[int, str]) -> bool:
    names = {categories.get(int(item), "").strip().lower() for item in post.get("categories", [])}
    title = clean_text(post.get("title", {}).get("rendered", "")).lower()
    return bool(names & FLASH_TERMS) or "flash-news" in title or title.startswith("flashnews")


def card(post: dict, path: str, date_display: str, category: str, summary: str) -> str:
    title = escape(clean_text(post.get("title", {}).get("rendered", "")))
    href = escape(path, quote=True)
    category_html = f'<span class="news-card__category">{escape(category)}</span>' if category else ""
    return (f'<article class="card card--wordpress" data-wordpress-news="{escape(str(post["id"]), quote=True)}">'
            f'<div class="card-body"><time datetime="{escape(post["date"][:10])}">{date_display}</time>'
            f'{category_html}<h2><a href="{href}">{title}</a></h2><p>{escape(summary)}</p>'
            f'<a class="more" href="{href}">Weiterlesen →</a></div></article>')


def article_shell(shell_source: Path, title: str, date_display: str, category: str, body: str, image: str | None) -> str:
    raw = shell_source.read_text(encoding="utf-8")
    main_match = re.search(r'<main\s+id=(?:"main-content"|main-content)(?:\s[^>]*)?>(.*?)</main>', raw, flags=re.S)
    if not main_match:
        raise RuntimeError("generated homepage main shell is missing")
    article = (f'<article class="article article--wordpress"><div class="shell article-shell">'
               f'<p class="eyebrow">{escape(category or "Aktuelles")}</p>'
               f'<h1>{escape(title)}</h1><time>{escape(date_display)}</time>')
    if image:
        article += f'<figure class="article__image"><img src="{escape(image, quote=True)}" alt="" loading="eager"></figure>'
    article += f'<div class="prose">{body}</div></div></article>'
    return raw[:main_match.start()] + '<main id="main-content">' + article + '</main>' + raw[main_match.end():]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default=DEFAULT_API)
    parser.add_argument("--public", default="site/public", type=Path)
    parser.add_argument("--max-posts", default=100, type=int)
    args = parser.parse_args()
    public = args.public.resolve()
    media_root = public / "images" / "news"
    media_root.mkdir(parents=True, exist_ok=True)
    categories_raw, _ = request_json(args.api.rstrip("/") + "/categories?per_page=100")
    categories = {int(item["id"]): str(item["name"]) for item in categories_raw if isinstance(item, dict)}
    posts, _ = request_json(args.api.rstrip("/") + f"/posts?status=publish&per_page={args.max_posts}&orderby=date&order=desc&_embed=1")
    if not isinstance(posts, list):
        raise RuntimeError("WordPress posts response is not a list")
    shell = public / "index.html"
    index = public / "aktuelles" / "index.html"
    if not shell.is_file() or not index.is_file():
        raise RuntimeError("generated ESC shell or aktuelles page is missing")
    cache: dict[str, str] = {}
    cards: list[str] = []
    imported = 0
    for post in posts:
        if not isinstance(post, dict) or is_flash(post, categories):
            continue
        title = clean_text(post.get("title", {}).get("rendered", ""))
        if not title or not post.get("date"):
            continue
        date_iso, date_display = date_parts(post["date"])
        category = next((categories.get(int(item), "") for item in post.get("categories", [])), "")
        path = f"/aktuelles/{date_iso}-{slugify(title)}/"
        embedded = post.get("_embedded", {})
        media = embedded.get("wp:featuredmedia", []) if isinstance(embedded, dict) else []
        image_url = media[0].get("source_url", "") if media and isinstance(media[0], dict) else ""
        image = download_media(image_url, public, media_root, cache)
        content = post.get("content", {}).get("rendered", "")
        body = sanitize_content(content, public, media_root, cache)
        summary = clean_text(post.get("excerpt", {}).get("rendered", "")) or clean_text(content)[:220]
        cards.append(card(post, path, date_display, category, summary))
        out = public / path.strip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(article_shell(shell, title, date_display, category, body, image), encoding="utf-8")
        imported += 1
    html = index.read_text(encoding="utf-8")
    marker = re.compile(r'<!-- wordpress-news:start -->.*?<!-- wordpress-news:end -->', flags=re.S)
    block = "<!-- wordpress-news:start -->" + "".join(cards) + "<!-- wordpress-news:end -->"
    if marker.search(html):
        html = marker.sub(block, html, count=1)
    elif "<div class=cards>" in html:
        html = html.replace("<div class=cards>", "<div class=cards>" + block, 1)
    elif '<div class="cards">' in html:
        html = html.replace('<div class="cards">', '<div class="cards">' + block, 1)
    else:
        raise RuntimeError("aktuelles card container is missing")
    index.write_text(html, encoding="utf-8")
    print(f"Imported {imported} published WordPress news item(s); Flash-News excluded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

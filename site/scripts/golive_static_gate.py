#!/usr/bin/env python3
"""Fail-closed static Go-Live checks for the generated ESC site.

Scope is intentionally narrow under the Go-Live feature freeze:
- internal links/assets must resolve inside the generated artifact;
- generated pages must carry basic document-language/title semantics;
- images must expose an alt attribute;
- links and buttons must have a discernible accessible name.

No network requests, provider calls or production writes are performed.
"""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

SKIP_SCHEMES = {"http", "https", "mailto", "tel", "sms", "javascript", "data"}

class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_lang: str | None = None
        self.title_depth = 0
        self.title_text: list[str] = []
        self.links: list[tuple[str, str, str]] = []
        self.assets: list[tuple[str, str]] = []
        self.missing_alt: list[str] = []
        self._interactive: list[dict[str, object]] = []
        self.unnamed_interactive: list[str] = []

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = dict(attrs_list)
        if tag == "html" and self.html_lang is None:
            self.html_lang = (attrs.get("lang") or "").strip()
        elif tag == "title":
            self.title_depth += 1
        elif tag == "img":
            if "alt" not in attrs:
                self.missing_alt.append(attrs.get("src") or "<img without src>")
            src = (attrs.get("src") or "").strip()
            if src:
                self.assets.append(("img", src))
        elif tag in {"script", "source"}:
            attr = "src" if tag == "script" else "srcset"
            value = (attrs.get(attr) or "").strip()
            if value:
                if attr == "srcset":
                    for candidate in value.split(","):
                        url = candidate.strip().split(" ", 1)[0]
                        if url:
                            self.assets.append((tag, url))
                else:
                    self.assets.append((tag, value))
        elif tag == "link":
            href = (attrs.get("href") or "").strip()
            if href and (attrs.get("rel") or "").lower() in {"stylesheet", "icon", "preload", "modulepreload"}:
                self.assets.append(("link", href))

        if tag in {"a", "button"}:
            self._interactive.append({
                "tag": tag,
                "href": (attrs.get("href") or "").strip(),
                "aria": (attrs.get("aria-label") or "").strip(),
                "title": (attrs.get("title") or "").strip(),
                "text": [],
                "img_alt": [],
            })
        elif tag == "img" and self._interactive:
            alt = (attrs.get("alt") or "").strip()
            if alt:
                self._interactive[-1]["img_alt"].append(alt)  # type: ignore[index]

        if tag == "a":
            href = (attrs.get("href") or "").strip()
            if href:
                self.links.append((href, (attrs.get("aria-label") or "").strip(), (attrs.get("title") or "").strip()))

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title_text.append(data)
        if self._interactive:
            self._interactive[-1]["text"].append(data)  # type: ignore[index]

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self.title_depth:
            self.title_depth -= 1
        if tag in {"a", "button"} and self._interactive:
            item = self._interactive.pop()
            if item["tag"] != tag:
                return
            pieces = [item["aria"], item["title"]]
            pieces.extend(item["text"])  # type: ignore[arg-type]
            pieces.extend(item["img_alt"])  # type: ignore[arg-type]
            name = " ".join(" ".join(str(p).split()) for p in pieces if str(p).strip()).strip()
            if not name:
                href = item["href"] or "<no href>"
                self.unnamed_interactive.append(f"{tag} {href}")

def artifact_path(public_root: Path, page_file: Path, raw_url: str, base_path: str) -> Path | None:
    parsed = urlsplit(raw_url)
    if parsed.scheme.lower() in SKIP_SCHEMES or parsed.netloc:
        return None
    path = unquote(parsed.path)
    if not path or path.startswith("#"):
        return None
    normalized_base = "/" + base_path.strip("/") if base_path.strip("/") else ""
    if normalized_base and (path == normalized_base or path.startswith(normalized_base + "/")):
        path = path[len(normalized_base):] or "/"
    if path.startswith("/"):
        rel = PurePosixPath(path.lstrip("/"))
    else:
        page_rel = page_file.relative_to(public_root)
        page_dir = PurePosixPath(page_rel.parent.as_posix())
        rel = page_dir / PurePosixPath(path)
    parts: list[str] = []
    for part in rel.parts:
        if part in {"", "."}:
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    candidate = public_root.joinpath(*parts)
    if path.endswith("/") or not candidate.suffix:
        candidate = candidate / "index.html"
    return candidate

def validate(public_root: Path, base_path: str) -> list[str]:
    errors: list[str] = []
    pages = sorted(public_root.rglob("*.html"))
    if not pages:
        return [f"no generated HTML found under {public_root}"]
    for page in pages:
        parser = PageParser()
        parser.feed(page.read_text(encoding="utf-8"))
        rel = page.relative_to(public_root).as_posix()
        if not parser.html_lang:
            errors.append(f"{rel}: missing html lang")
        if not " ".join(parser.title_text).strip():
            errors.append(f"{rel}: missing non-empty title")
        for src in parser.missing_alt:
            errors.append(f"{rel}: image missing alt attribute: {src}")
        for item in parser.unnamed_interactive:
            errors.append(f"{rel}: interactive element has no accessible name: {item}")
        urls = [href for href, _, _ in parser.links]
        urls.extend(url for _, url in parser.assets)
        for raw_url in urls:
            target = artifact_path(public_root, page, raw_url, base_path)
            if target is not None and not target.exists():
                errors.append(f"{rel}: unresolved internal reference {raw_url!r} -> {target.relative_to(public_root)}")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("public_root", nargs="?", default="site/public")
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    public_root = Path(args.public_root).resolve()
    errors = validate(public_root, args.base_path)
    if errors:
        print("Go-Live static gate FAILED")
        for error in errors:
            print(f"ERROR: {error}")
        return 2
    print("Go-Live static gate passed: internal references resolve and basic accessibility semantics are present")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

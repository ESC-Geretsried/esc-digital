#!/usr/bin/env python3
"""Fail when internal delivery/provenance language reaches the public artifact."""

from __future__ import annotations

import argparse
import re
import unicodedata
from html.parser import HTMLParser
from pathlib import Path


FORBIDDEN = re.compile(
    r"(?i)(?<![\w])(?:"
    r"git(?:hub)?|repository|repo|pull[ -]request|pr|commit\w*|"
    r"migration\w*|migrier\w*|intake\w*|source|snapshot\w*|int|"
    r"preview\w*|transition\w*|transitional\w*|provenance|provenienz|"
    r"founder(?:-provided|-quelle)?|orp\s+editor|legacy(?:-pfad)?|"
    r"versionier\w*|kanonisch\w*|canonical|m2(?:-[\w-]+)?|mvp(?:-[\w-]+)?|"
    r"projektverlauf|produktivstart|in\s+dieser\s+stufe"
    r")(?![\w])"
)

SKIP_CONTENT_TAGS = {"script", "style", "template", "loc", "guid"}
PUBLIC_ATTRIBUTES = {"alt", "aria-label", "title", "placeholder"}


class PublicText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_stack: list[str] = []
        self.chunks: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attrs = dict(attrs_list)
        if tag in SKIP_CONTENT_TAGS or (tag == "link" and not attrs):
            self.skip_stack.append(tag)
        if self.skip_stack:
            return
        line, _ = self.getpos()
        for name in PUBLIC_ATTRIBUTES:
            value = attrs.get(name)
            if value:
                self.chunks.append((f"{name} at line {line}", value))
        if tag == "meta":
            key = (attrs.get("name") or attrs.get("property") or "").lower()
            if key in {"description", "og:title", "og:description", "twitter:title", "twitter:description"}:
                value = attrs.get("content")
                if value:
                    self.chunks.append((f"meta {key} at line {line}", value))

    def handle_startendtag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs_list)
        if self.skip_stack and self.skip_stack[-1] == tag.lower():
            self.skip_stack.pop()

    def handle_endtag(self, tag: str) -> None:
        if self.skip_stack and self.skip_stack[-1] == tag.lower():
            self.skip_stack.pop()

    def handle_data(self, data: str) -> None:
        if self.skip_stack or not data.strip():
            return
        line, _ = self.getpos()
        self.chunks.append((f"text at line {line}", data))


def normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split())


def validate(public_root: Path) -> list[str]:
    errors: list[str] = []
    files = sorted(public_root.rglob("*.html")) + sorted(public_root.rglob("*.xml"))
    if not files:
        return [f"no public HTML or XML found below {public_root}"]
    for path in files:
        parser = PublicText()
        parser.feed(path.read_text(encoding="utf-8"))
        for surface, raw in parser.chunks:
            text = normalize(raw)
            match = FORBIDDEN.search(text)
            if match:
                context_start = max(0, match.start() - 80)
                context_end = min(len(text), match.end() + 80)
                context = text[context_start:context_end]
                rel = path.relative_to(public_root).as_posix()
                errors.append(f"{rel}: {surface}: forbidden {match.group(0)!r} in {context!r}")
    return errors


def main() -> int:
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("public_root", nargs="?", default="site/public")
    args = args_parser.parse_args()
    public_root = Path(args.public_root).resolve()
    errors = validate(public_root)
    if errors:
        print("Public-copy leak gate FAILED")
        for error in errors:
            print(f"ERROR: {error}")
        return 2
    print("Public-copy leak gate passed: no internal delivery or provenance language is publicly rendered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

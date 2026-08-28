#!/usr/bin/env python3
"""Validate, generate and enforce the ESC OWML v1 contract using stdlib only."""

from __future__ import annotations

import argparse
import hashlib
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
from datetime import date, datetime
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OWML = ROOT / "owml" / "v1"
GENERATED = OWML / "generated"
VERSION = "1.0.0"
TEAM_ROUTES = {
    "/river-rats/", "/river-rats-herren/", "/river-rats-damen/",
    "/u20/", "/u17/", "/u15/", "/u13/", "/u11/", "/u9/", "/u7/",
}
EXTERNAL_COMPETITION_ROUTES = {
    "/river-rats-damen/", "/u20/", "/u17/", "/u15/", "/u13/",
}
NO_STANDINGS = {"/u11/", "/u9/", "/u7/"}
ARCHITECTURE_FIELDS = {
    "owml", "owml_version", "pattern", "pattern_id", "nodes", "sections",
    "node_order", "node_type", "navigation", "anchors", "renderer",
    "component", "layout", "data_binding",
}


class OWMLFailure(RuntimeError):
    pass


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise OWMLFailure(f"cannot read valid JSON: {path.relative_to(ROOT)}: {exc}") from exc


def canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def route_id(route: str) -> str:
    if route == "/":
        return "esc.home"
    return "esc." + route.strip("/").replace("/", ".").replace("_", "-")


def content_routes() -> set[str]:
    routes = {"/"}
    for path in (ROOT / "content").rglob("*.md"):
        rel = path.relative_to(ROOT / "content")
        if rel.parts[0] == ".orp-editor" or path.name == "README.md":
            continue
        if path.name == "_index.md":
            parent = rel.parent.as_posix()
            routes.add("/" if parent == "." else f"/{parent}/")
        else:
            routes.add(f"/{rel.with_suffix('').as_posix()}/")
    manifest = read_json(ROOT / "docs" / "operations" / "esc-int-pages-manifest.json")
    routes.update(item["path"] for item in manifest["pages"])
    routes.add("/foerderverein/")  # Binding independent route from INV-004 reconciliation.
    return routes


def source_for(route: str) -> str:
    if route == "/":
        return "content/_index.md"
    candidate = ROOT / "content" / route.strip("/") / "_index.md"
    if candidate.is_file():
        return candidate.relative_to(ROOT).as_posix()
    if route == "/foerderverein/":
        return "content/verein/foerderverein/_index.md"
    return "imports/esc-int-pages" + route + "index.html"


def pattern_for(route: str) -> str:
    if route == "/": return "homepage"
    if route == "/aktuelles/": return "news-index"
    if route.startswith("/aktuelles/"): return "article"
    if route in {"/river-rats/", "/river-rats-herren/"}: return "team-page-river-rats"
    if route in EXTERNAL_COMPETITION_ROUTES: return "team-page-external-competition"
    if route in TEAM_ROUTES: return "team-page"
    fixed = {
        "/sponsoren/": "sponsor",
        "/verein/geschaeftsstelle/": "contact-office",
        "/mitgliedschaft/": "membership",
        "/foerderverein/": "donation-supporters",
        "/verein/foerderverein/": "donation-supporters",
        "/verein/vereinsfuehrung/": "board",
        "/eislaufschule/": "skating-school",
        "/eiskunstlauf/": "figure-skating",
        "/inklusion/": "inclusion",
        "/verein/": "club",
        "/nachwuchs/": "youth-index",
        "/impressum/": "legal",
        "/datenschutz/": "legal",
        "/dauerkarten/": "service",
    }
    return fixed.get(route, "generic-section")


def bootstrap_pages() -> dict:
    pages = []
    for route in sorted(content_routes()):
        page = {
            "id": route_id(route),
            "pattern": pattern_for(route),
            "publication": "active",
            "route": route,
            "source": source_for(route),
        }
        if route in {"/river-rats-herren/", "/verein/foerderverein/"}:
            page["publication"] = "redirect"
            page["redirect_to"] = "/river-rats/" if route == "/river-rats-herren/" else "/foerderverein/"
        if route in NO_STANDINGS:
            page["disabled_nodes"] = ["standings"]
            page["variant"] = "manual-youth-without-standings"
        elif route == "/river-rats/":
            page["variant"] = "protected-hockeydata-plus-editorial-supplements"
        elif route in EXTERNAL_COMPETITION_ROUTES:
            page["variant"] = "external-deb-online-action-only"
        if route == "/u15/":
            page["notes"] = ["Founder target uses one optional external DEB.ONLINE action; empty omits it."]
        if route == "/verein/foerderverein/":
            page["notes"] = ["Legacy route remains covered; canonical independent target is /foerderverein/."]
        pages.append(page)
    return {"owml_version": VERSION, "tenant": "esc", "pages": pages}


def load_models():
    catalog = read_json(OWML / "node-catalog.json")
    patterns_doc = read_json(OWML / "patterns.json")
    pages_doc = read_json(OWML / "pages.json")
    policy = read_json(OWML / "editor-policy.json")
    return catalog, patterns_doc, pages_doc, policy


def exact_object(value, *, required: set[str], allowed: set[str], context: str) -> None:
    if not isinstance(value, dict):
        raise OWMLFailure(f"schema {context} must be an object")
    missing = required - value.keys()
    unknown = value.keys() - allowed
    if missing or unknown:
        raise OWMLFailure(f"schema {context} keys invalid; missing={sorted(missing)}, unknown={sorted(unknown)}")


def validate_homepage_content_contract(patterns: dict) -> None:
    homepage_invariants = set(patterns["homepage"]["invariants"])
    required_invariants = {
        "youth-hero-daily-image-static-nachwuchs-link",
        "announcement-sequential-slow",
        "reduced-motion-static-announcement",
    }
    if not required_invariants <= homepage_invariants:
        raise OWMLFailure(f"homepage behavior invariants missing: {sorted(required_invariants - homepage_invariants)}")

    heroes = read_json(ROOT / "content" / "home" / "heroes.json")
    youth = next((slide for slide in heroes.get("slides", []) if slide.get("id") == "nachwuchs"), None)
    expected_images = [f"images/teams/{team}-team.jpg" for team in ("u7", "u9", "u11", "u13", "u15", "u17", "u20")]
    if not youth or youth.get("daily_images") != expected_images:
        raise OWMLFailure("homepage youth hero Monday-Sunday image contract drift")
    if youth.get("cta_path") != "/nachwuchs/" or "daily_paths" in youth:
        raise OWMLFailure("homepage youth hero may rotate only its image; link must stay /nachwuchs/")

    announcements = read_json(ROOT / "content" / "home" / "announcements.json")
    if announcements.get("rotation") != "sequential-slow":
        raise OWMLFailure("homepage announcement rotation must be sequential-slow")
    if announcements.get("reduced_motion") != "first-message-static":
        raise OWMLFailure("homepage announcement reduced-motion fallback must be first-message-static")
    messages = announcements.get("messages", [])
    if not isinstance(messages, list) or not messages:
        raise OWMLFailure("homepage announcement messages must be a non-empty ordered list")
    ids = [message.get("id") for message in messages]
    orders = [message.get("order") for message in messages]
    if any(not item for item in ids) or len(ids) != len(set(ids)) or len(orders) != len(set(orders)):
        raise OWMLFailure("homepage announcement ids and order values must be unique")
    for message in messages:
        if not message.get("url") and message.get("new_tab"):
            raise OWMLFailure(f"linkless announcement cannot request a new tab: {message.get('id')}")
        if str(message.get("url", "")).startswith(("http://", "https://")) and message.get("new_tab") is not True:
            raise OWMLFailure(f"external announcement must open in a new tab: {message.get('id')}")


def validate() -> tuple[dict, dict, dict, dict]:
    catalog, patterns_doc, pages_doc, policy = load_models()
    schema = read_json(OWML / "schema" / "owml-site.schema.json")
    player_schema = read_json(OWML / "schema" / "player.schema.json")
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema" or schema.get("properties", {}).get("owml_version", {}).get("const") != VERSION:
        raise OWMLFailure("OWML JSON Schema identity/version is invalid")
    if set(player_schema.get("required", [])) != {"position_code", "number", "name"}:
        raise OWMLFailure("common Player schema required fields drift")
    if player_schema.get("properties", {}).get("position_code", {}).get("enum") != ["T", "V", "S"]:
        raise OWMLFailure("common Player position enum drift")
    if player_schema.get("x-info-automation") is not False:
        raise OWMLFailure("common Player info must not be automatically calculated")
    if player_schema.get("x-placeholder-asset-status") != "OPEN: Founder binary/path not yet present in Git":
        raise OWMLFailure("Player placeholder OPEN boundary drift")
    exact_object(patterns_doc, required={"owml_version", "tenant", "patterns"}, allowed={"owml_version", "tenant", "patterns"}, context="patterns document")
    exact_object(pages_doc, required={"owml_version", "tenant", "pages"}, allowed={"owml_version", "tenant", "pages"}, context="pages document")
    if patterns_doc.get("tenant") != "esc" or pages_doc.get("tenant") != "esc":
        raise OWMLFailure("schema tenant must be esc")
    for name, doc in (("catalog", catalog), ("patterns", patterns_doc), ("pages", pages_doc), ("editor policy", policy)):
        if doc.get("owml_version") != VERSION:
            raise OWMLFailure(f"{name} must use OWML {VERSION}")
    if catalog.get("unknown_node_policy") != "fail-closed":
        raise OWMLFailure("unknown node policy must be fail-closed")
    node_types = {}
    for node in catalog.get("nodes", []):
        node_type = node.get("type")
        if not node_type or node_type in node_types:
            raise OWMLFailure(f"duplicate or empty node type: {node_type}")
        renderer = ROOT / node.get("renderer", "")
        if not renderer.is_file():
            raise OWMLFailure(f"renderer missing for {node_type}: {renderer}")
        node_types[node_type] = node
    patterns = {}
    for pattern in patterns_doc.get("patterns", []):
        exact_object(pattern, required={"id", "title", "nodes", "invariants"}, allowed={"id", "title", "description", "nodes", "invariants"}, context=f"pattern {pattern.get('id')}")
        pattern_id = pattern.get("id")
        if not pattern_id or pattern_id in patterns:
            raise OWMLFailure(f"duplicate or empty pattern: {pattern_id}")
        ids = []
        for node in pattern.get("nodes", []):
            exact_object(node, required={"id", "type", "slot", "required"}, allowed={"id", "type", "slot", "required", "anchor", "binding", "condition", "fallback", "editor_mutable"}, context=f"node {pattern_id}.{node.get('id')}")
            if node.get("type") not in node_types:
                raise OWMLFailure(f"unknown node type {node.get('type')} in {pattern_id}")
            if not isinstance(node.get("required"), bool):
                raise OWMLFailure(f"node required flag must be boolean: {pattern_id}.{node.get('id')}")
            if node.get("binding") and node["binding"] not in set(node_types[node["type"]].get("bindings", [])):
                raise OWMLFailure(f"binding {node['binding']} is not allowed for {node['type']}")
            ids.append(node.get("id"))
        if len(ids) != len(set(ids)) or any(not item for item in ids):
            raise OWMLFailure(f"duplicate or empty node id in {pattern_id}")
        expected_prefix = ["announcements", "header"] if pattern_id == "homepage" else ["header"]
        if ids[:len(expected_prefix)] != expected_prefix or ids[-1] != "footer":
            raise OWMLFailure(f"pattern {pattern_id} has invalid chrome boundary/order")
        patterns[pattern_id] = pattern
    required_patterns = {
        "homepage", "team-page", "team-page-river-rats",
        "team-page-external-competition", "news-index", "article", "event", "sponsor",
        "contact-office", "membership", "donation-supporters", "board",
        "skating-school", "figure-skating", "inclusion",
    }
    missing_patterns = required_patterns - patterns.keys()
    if missing_patterns:
        raise OWMLFailure(f"required patterns missing: {sorted(missing_patterns)}")
    validate_homepage_content_contract(patterns)
    pages = {}
    ids = set()
    for page in pages_doc.get("pages", []):
        exact_object(page, required={"id", "route", "pattern", "source", "publication"}, allowed={"id", "route", "pattern", "source", "publication", "variant", "disabled_nodes", "notes", "redirect_to"}, context=f"page {page.get('route')}")
        route, page_id = page.get("route"), page.get("id")
        if not route or route in pages or page_id in ids:
            raise OWMLFailure(f"duplicate/empty route or id: {route} / {page_id}")
        if page.get("pattern") not in patterns:
            raise OWMLFailure(f"unknown pattern for {route}: {page.get('pattern')}")
        if page.get("publication") not in {"active", "source-only", "redirect"}:
            raise OWMLFailure(f"invalid publication state for {route}")
        if page.get("publication") == "redirect" and page.get("redirect_to") not in content_routes():
            raise OWMLFailure(f"invalid redirect target for {route}: {page.get('redirect_to')}")
        pattern_node_ids = {node["id"] for node in patterns[page["pattern"]]["nodes"]}
        if set(page.get("disabled_nodes", [])) - pattern_node_ids:
            raise OWMLFailure(f"unknown disabled node for {route}")
        if page.get("source", "").startswith(("content/", "imports/")) and not (ROOT / page["source"]).exists():
            raise OWMLFailure(f"source missing for {route}: {page['source']}")
        pages[route] = page
        ids.add(page_id)
    expected = content_routes()
    if set(pages) != expected:
        raise OWMLFailure(f"route coverage drift; missing={sorted(expected-set(pages))}, extra={sorted(set(pages)-expected)}")
    if not policy.get("structure_lock") or not ARCHITECTURE_FIELDS.issubset(set(policy.get("architecture_only_fields", []))):
        raise OWMLFailure("editor policy does not fail closed for all architecture fields")
    observed = read_json(OWML / "pilots" / "u15.observed.json")
    if observed.get("status") != "observed-not-authoritative" or observed.get("route") != "/u15/":
        raise OWMLFailure("U15 observed pilot boundary is invalid")
    recovery = read_json(OWML / "recovery-manifest.json")
    if recovery.get("owml_version") != VERSION or recovery.get("expected_deployment") != "NONE":
        raise OWMLFailure("OWML recovery manifest version/deployment boundary is invalid")
    if recovery.get("secrets_stored_in_git") is not False or recovery.get("png_required") is not False:
        raise OWMLFailure("OWML recovery manifest violates secrets/PNG boundary")
    missing_recovery = [relative for relative in recovery.get("required_inputs", []) if not (ROOT / relative).is_file()]
    if missing_recovery:
        raise OWMLFailure(f"OWML recovery inputs missing: {missing_recovery}")
    return catalog, patterns, pages, policy


def expanded_nodes(patterns: dict, page: dict) -> list[dict]:
    disabled = set(page.get("disabled_nodes", []))
    return [node for node in patterns[page["pattern"]]["nodes"] if node["id"] not in disabled]


def runtime_document(patterns: dict, pages: dict) -> dict:
    routes = {}
    for route, page in sorted(pages.items()):
        nodes = expanded_nodes(patterns, page)
        routes[route] = {
            "anchors": [node["anchor"] for node in nodes if node.get("anchor")],
            "instance": page["id"],
            "nodes": [node["id"] for node in nodes],
            "pattern": page["pattern"],
            "publication": page["publication"],
        }
    return {"owml_version": VERSION, "tenant": "esc", "unknown_route_policy": "fail-closed", "routes": routes}


def generated_documents(patterns: dict, pages: dict) -> dict[Path, str]:
    runtime = runtime_document(patterns, pages)
    pattern_counts = {key: 0 for key in patterns}
    for page in pages.values():
        pattern_counts[page["pattern"]] += 1
    markdown = ["# ESC OWML v1 Pattern Library", "", "Generated deterministically from canonical OWML JSON. Do not edit.", ""]
    for pattern_id, pattern in sorted(patterns.items()):
        markdown += [f"## {pattern['title']} (`{pattern_id}`)", "", pattern.get("description", ""), "", "Nodes: " + " → ".join(node["id"] for node in pattern["nodes"]), "", f"Assigned pages: {pattern_counts[pattern_id]}", ""]
    d2 = ["direction: right", 'site: "ESC OWML v1" {', "  shape: package"]
    for pattern_id in sorted(patterns):
        d2.append(f'  {pattern_id.replace("-", "_")}: "{pattern_id} ({pattern_counts[pattern_id]})"')
    d2.append("}")
    for route, page in sorted(pages.items()):
        route_key = "page_" + hashlib.sha256(route.encode()).hexdigest()[:10]
        d2.append(f'{route_key}: "{route}"')
        d2.append(f'{route_key} -> site.{page["pattern"].replace("-", "_")}')
    d2_text = "\n".join(d2) + "\n"
    row_height = 30
    height = 90 + row_height * len(patterns)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" viewBox="0 0 900 {height}">', '<rect width="100%" height="100%" fill="#f5f7fa"/>', '<text x="32" y="42" font-family="system-ui" font-size="24" font-weight="700">ESC OWML v1 – Pattern coverage</text>']
    for index, (pattern_id, pattern) in enumerate(sorted(patterns.items())):
        y = 72 + index * row_height
        svg += [f'<rect x="30" y="{y}" width="840" height="24" rx="5" fill="#ffffff" stroke="#234"/>', f'<text x="42" y="{y+17}" font-family="system-ui" font-size="13">{escape(pattern["title"])} · {escape(pattern_id)} · {pattern_counts[pattern_id]} page(s)</text>']
    svg.append("</svg>\n")
    observed = read_json(OWML / "pilots" / "u15.observed.json")
    target_nodes = [node["id"] for node in expanded_nodes(patterns, pages["/u15/"])]
    observed_nodes = [node["id"] for node in observed["nodes"]]
    missing = [node for node in target_nodes if node not in observed_nodes]
    pilot_d2 = "direction: right\nobserved: \"U15 observed\\n" + " -> ".join(observed_nodes) + "\"\ntarget: \"U15 binding target\\n" + " -> ".join(target_nodes) + "\"\nobserved -> target: \"drift: " + ", ".join(missing) + "\"\n"
    pilot_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="250" viewBox="0 0 1200 250">
<rect width="100%" height="100%" fill="#f5f7fa"/><text x="30" y="35" font-family="system-ui" font-size="24" font-weight="700">U15 observed vs binding OWML target</text>
<rect x="30" y="60" width="1140" height="62" rx="8" fill="#fff" stroke="#7a8795"/><text x="48" y="84" font-family="system-ui" font-size="14" font-weight="700">OBSERVED 2026-08-27</text><text x="48" y="108" font-family="system-ui" font-size="13">{escape(' → '.join(observed_nodes))}</text>
<rect x="30" y="145" width="1140" height="72" rx="8" fill="#fff8e1" stroke="#9a6b00"/><text x="48" y="169" font-family="system-ui" font-size="14" font-weight="700">BINDING TARGET</text><text x="48" y="193" font-family="system-ui" font-size="13">{escape(' → '.join(target_nodes))}</text><text x="48" y="211" font-family="system-ui" font-size="12" fill="#8a2d21">Missing in observed: {escape(', '.join(missing))}; external DEB.ONLINE action is omitted while URL is empty.</text>
</svg>
'''
    test_manifest = {
        "owml_version": VERSION,
        "generated": True,
        "routes": [{"route": route, **runtime["routes"][route]} for route in sorted(runtime["routes"])],
        "tests": ["schema-and-contract", "ids-and-refs", "invariants", "renderer-coverage", "deterministic-generation", "routes-and-anchors", "basic-accessibility", "runtime-drift"],
    }
    return {
        GENERATED / "patterns.md": "\n".join(markdown).rstrip() + "\n",
        GENERATED / "site.d2": d2_text,
        GENERATED / "site.svg": "".join(svg),
        GENERATED / "u15-observed-target.d2": pilot_d2,
        GENERATED / "u15-observed-target.svg": pilot_svg,
        GENERATED / "runtime-routes.json": canonical_json(runtime),
        GENERATED / "test-manifest.json": canonical_json(test_manifest),
    }


def generate(check: bool) -> None:
    _, patterns, pages, _ = validate()
    documents = generated_documents(patterns, pages)
    mismatches = []
    for path, expected in documents.items():
        if check:
            actual = path.read_text(encoding="utf-8") if path.is_file() else None
            if actual != expected:
                mismatches.append(path.relative_to(ROOT).as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
    if mismatches:
        raise OWMLFailure("generated artifacts differ: " + ", ".join(mismatches))


def article_retained(route: str) -> bool:
    match = re.match(r"^/aktuelles/(\d{4})-(\d{2})-(\d{2})-", route)
    if not match:
        return True
    published = date(*(int(part) for part in match.groups()))
    explicit_as_of = (os.environ.get("OWML_AS_OF_DATE") or os.environ.get("NEWS_RETENTION_AS_OF") or "").strip()
    if explicit_as_of:
        as_of = date.fromisoformat(explicit_as_of)
    else:
        policy = read_json(ROOT / "config" / "news-retention.json")
        as_of = datetime.now(ZoneInfo(policy["policy_timezone"])).date()
    try:
        boundary = published.replace(year=published.year + 1)
    except ValueError:
        boundary = published.replace(year=published.year + 1, day=28)
    return as_of < boundary


def route_path(public: Path, route: str) -> Path:
    return public / "index.html" if route == "/" else public / route.strip("/") / "index.html"


def bind_runtime(public: Path) -> None:
    _, patterns, pages, _ = validate()
    runtime = runtime_document(patterns, pages)["routes"]
    covered_files = set()
    for route, binding in runtime.items():
        if binding["publication"] == "source-only" or not article_retained(route):
            continue
        path = route_path(public, route)
        if not path.is_file():
            raise OWMLFailure(f"published OWML route missing from build: {route}")
        if binding["publication"] == "redirect":
            target = pages[route]["redirect_to"]
            base_path = urlsplit(os.environ.get("HUGO_BASEURL", "/")).path.rstrip("/")
            public_target = f"{base_path}{target}" if base_path else target
            html = (
                '<!doctype html><html lang="de"><head><meta charset="utf-8">'
                '<meta name="robots" content="noindex"><title>Weiterleitung</title>'
                f'<link rel="canonical" href="{escape(public_target, quote=True)}">'
                f'<meta http-equiv="refresh" content="0; url={escape(public_target, quote=True)}">'
                f'</head><body><main id="main-content" data-owml-version="{VERSION}" '
                f'data-owml-instance="{binding["instance"]}" data-owml-pattern="{binding["pattern"]}">'
                f'<h1>Weiterleitung</h1><p><a href="{escape(public_target, quote=True)}">Zur aktuellen Seite</a></p>'
                '</main></body></html>\n'
            )
            path.write_text(html, encoding="utf-8")
            covered_files.add(path.resolve())
            continue
        html = path.read_text(encoding="utf-8")
        main_match = re.search(r'<main\s+id=(?:"main-content"|main-content)', html)
        if not main_match:
            raise OWMLFailure(f"runtime main landmark missing: {route}")
        attrs = f' data-owml-version="{VERSION}" data-owml-instance="{binding["instance"]}" data-owml-pattern="{binding["pattern"]}"'
        html = re.sub(r' data-owml-(?:version|instance|pattern)="[^"]*"', "", html)
        main_match = re.search(r'<main\s+id=(?:"main-content"|main-content)', html)
        html = html[:main_match.end()] + attrs + html[main_match.end():]
        path.write_text(html, encoding="utf-8")
        covered_files.add(path.resolve())
    unknown = []
    for path in public.rglob("index.html"):
        if path.resolve() not in covered_files:
            unknown.append(path.relative_to(public).as_posix())
    if unknown:
        raise OWMLFailure("generated routes without active OWML instance: " + ", ".join(sorted(unknown)))


class StructureParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set(); self.hrefs = []; self.h1 = 0; self.main = 0; self.lang = False
        self.images_without_alt = 0
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"): self.ids.add(values["id"])
        if tag == "a" and values.get("href"): self.hrefs.append(values["href"])
        if tag == "h1": self.h1 += 1
        if tag == "main": self.main += 1
        if tag == "html" and values.get("lang"): self.lang = True
        if tag == "img" and "alt" not in values: self.images_without_alt += 1


def drift(public: Path) -> None:
    _, patterns, pages, _ = validate()
    failures = []
    for route, page in sorted(pages.items()):
        if page["publication"] != "active" or not article_retained(route):
            continue
        path = route_path(public, route)
        if not path.is_file():
            failures.append(f"{route}: missing output"); continue
        html = path.read_text(encoding="utf-8")
        required_marker = f'data-owml-instance="{page["id"]}" data-owml-pattern="{page["pattern"]}"'
        if required_marker not in html:
            failures.append(f"{route}: OWML runtime binding missing")
        parser = StructureParser(); parser.feed(html)
        if parser.main != 1 or parser.h1 != 1 or not parser.lang:
            failures.append(f"{route}: accessibility landmarks main={parser.main} h1={parser.h1} lang={parser.lang}")
        if parser.images_without_alt:
            failures.append(f"{route}: {parser.images_without_alt} image(s) lack alt")
        missing_anchors = [node["anchor"] for node in expanded_nodes(patterns, page) if node.get("required", True) and node.get("anchor") and node["anchor"] not in parser.ids]
        if missing_anchors:
            failures.append(f"{route}: missing OWML anchors {missing_anchors}")
        broken_local = sorted({href[1:] for href in parser.hrefs if href.startswith("#") and href[1:] not in parser.ids})
        if broken_local:
            failures.append(f"{route}: broken local anchors {broken_local}")
    if failures:
        raise OWMLFailure("runtime drift:\n- " + "\n- ".join(failures))


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("bootstrap-pages")
    generate_parser = sub.add_parser("generate"); generate_parser.add_argument("--check", action="store_true")
    for command in ("bind-runtime", "drift"):
        item = sub.add_parser(command); item.add_argument("--public", type=Path, default=ROOT / "site" / "public")
    args = parser.parse_args()
    try:
        if args.command == "bootstrap-pages":
            path = OWML / "pages.json"; path.write_text(canonical_json(bootstrap_pages()), encoding="utf-8")
        elif args.command == "validate": validate()
        elif args.command == "generate": generate(args.check)
        elif args.command == "bind-runtime": bind_runtime(args.public)
        elif args.command == "drift": drift(args.public)
    except OWMLFailure as exc:
        print(f"OWML_ERROR: {exc}", file=sys.stderr); return 2
    print(f"OWML_{args.command.upper().replace('-', '_')}: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

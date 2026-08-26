#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import urlparse
import re
import sys

root = Path(__file__).resolve().parents[2]
public = root / 'site' / 'public'
imports = root / 'imports' / 'esc-int-pages'
baseurl = sys.argv[1] if len(sys.argv) > 1 else '/'
prefix = urlparse(baseurl).path or '/'
if not prefix.startswith('/'):
    prefix = '/' + prefix
if not prefix.endswith('/'):
    prefix += '/'

homepage_path = public / 'index.html'
home = homepage_path.read_text(encoding='utf-8')
main_open = re.search(r'<main\s+id=(?:"main-content"|main-content)>', home)
if not main_open:
    raise SystemExit('ERROR: generated ESC shell main marker missing')
pre = home[:main_open.start()]
rest = home[main_open.end():]
if '</main>' not in rest:
    raise SystemExit('ERROR: generated ESC shell main closing marker missing')
_, post = rest.split('</main>', 1)
open_marker = '<main id="main-content">'

# Canonical ESC pages are now owned by structured tenant content and must never
# be overwritten by the transitional rendered esc-int snapshot.
excluded_top_level = {
    'sponsoren',
    'river-rats',
    'river-rats-damen',
    'nachwuchs',
    'u20',
    'u17',
    'u15',
    'u13',
    'u11',
    'u9',
    'u7',
    'eislaufschule',
    'eiskunstlauf',
    'inklusion',
    'verein',
    'mitgliedschaft',
}
count = 0


def rewrite_root_urls(html: str) -> str:
    if prefix == '/':
        return html
    for attr in ('href', 'src'):
        html = html.replace(f'{attr}=/', f'{attr}={prefix}')
        html = html.replace(f'{attr}="/', f'{attr}="{prefix}')
        html = html.replace(f"{attr}='/", f"{attr}='{prefix}")
    return html

for src in sorted(imports.rglob('index.html')):
    rel = src.relative_to(imports)
    parts = rel.parts[:-1]
    if not parts:
        continue
    if parts[0] in excluded_top_level:
        continue

    raw = src.read_text(encoding='utf-8')
    match = re.search(r'<main id=main-content>(.*)</main><footer', raw, flags=re.S)
    if not match:
        match = re.search(r'<main id="main-content">(.*)</main><footer', raw, flags=re.S)
    if not match:
        raise SystemExit(f'ERROR: main content not found in {src}')

    imported_main = rewrite_root_urls(match.group(1))
    page = pre + open_marker + imported_main + '</main>' + post

    title = re.search(r'<title>(.*?)</title>', raw, flags=re.S)
    if title:
        page = re.sub(r'<title>.*?</title>', '<title>' + title.group(1) + '</title>', page, count=1, flags=re.S)

    out = public.joinpath(*parts, 'index.html')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding='utf-8')
    count += 1

# The transitional snapshot may contain teaser cards for preview/test articles
# that are not part of the approved public artifact. Never publish a teaser to
# a missing local article. This operates only on generated output; imported
# source material remains unchanged for provenance/recovery.
news_index = public / 'aktuelles' / 'index.html'
if news_index.is_file():
    html = news_index.read_text(encoding='utf-8')
    removed = 0

    def target_exists(href: str) -> bool:
        path = urlparse(href).path
        normalized_prefix = prefix.rstrip('/')
        if normalized_prefix and normalized_prefix != '/' and (path == normalized_prefix or path.startswith(normalized_prefix + '/')):
            path = path[len(normalized_prefix):] or '/'
        if not path.startswith('/aktuelles/'):
            return True
        rel = path.lstrip('/')
        target = public / rel
        if path.endswith('/') or not target.suffix:
            target = target / 'index.html'
        return target.is_file()

    article_re = re.compile(r'<article\s+class=card>.*?</article>', flags=re.S)

    def keep_or_drop(match: re.Match[str]) -> str:
        nonlocal_removed = 0
        article = match.group(0)
        hrefs = re.findall(r'href=(?:"([^"]+)"|\'([^\']+)\'|([^\s>]+))', article)
        flat = [next((part for part in groups if part), '') for groups in hrefs]
        if any(href.startswith(prefix + 'aktuelles/') or href.startswith('/aktuelles/') for href in flat):
            if any(not target_exists(href) for href in flat):
                return ''
        return article

    before = len(article_re.findall(html))
    html = article_re.sub(keep_or_drop, html)
    after = len(article_re.findall(html))
    removed = before - after
    news_index.write_text(html, encoding='utf-8')
    if removed:
        print(f'Removed {removed} unresolved transitional news teaser(s) from generated output')

print(f'Rendered {count} transitional esc-int pages without overwriting canonical ESC routes')

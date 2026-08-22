#!/usr/bin/env python3
from html import escape
from pathlib import Path
from urllib.parse import urlparse
import json
import re
import sys

root = Path(__file__).resolve().parents[2]
public = root / 'site' / 'public'
sponsors = json.loads((root / 'content' / 'sponsors' / 'sponsors.json').read_text(encoding='utf-8'))
page_data = json.loads((root / 'content' / 'sponsors' / 'page.json').read_text(encoding='utf-8'))
baseurl = sys.argv[1] if len(sys.argv) > 1 else '/'
prefix = urlparse(baseurl).path or '/'
if not prefix.startswith('/'):
    prefix = '/' + prefix
if not prefix.endswith('/'):
    prefix += '/'

home = (public / 'index.html').read_text(encoding='utf-8')
main_open = re.search(r'<main\s+id=(?:"main-content"|main-content)>', home)
if not main_open:
    raise SystemExit('ERROR: generated ESC shell main marker missing for sponsors page')
pre = home[:main_open.start()]
rest = home[main_open.end():]
if '</main>' not in rest:
    raise SystemExit('ERROR: generated ESC shell main closing marker missing for sponsors page')
_, post = rest.split('</main>', 1)

cards = []
for sponsor in sorted((s for s in sponsors['sponsors'] if s.get('visible')), key=lambda s: s.get('order', 0)):
    name = escape(sponsor['name'])
    logo = prefix + 'sponsors/assets/' + escape(Path(sponsor['logo']).name, quote=True)
    inner = f'<span class="sponsor-tile__logo"><img src="{logo}" alt="{name}" loading="lazy"></span><strong>{name}</strong>'
    if sponsor.get('url'):
        url = escape(sponsor['url'], quote=True)
        cards.append(f'<a class="sponsor-tile" href="{url}" target="_blank" rel="noopener noreferrer" aria-label="{name} – Partnerwebsite in neuem Tab öffnen">{inner}</a>')
    else:
        cards.append(f'<div class="sponsor-tile sponsor-tile--static" aria-label="{name}">{inner}</div>')

contact = page_data['contact']
phone_tel = ''.join(ch for ch in contact['phone'] if ch.isdigit() or ch == '+')
main = f'''<main id="main-content">
<header class="page-hero page-hero--sponsors"><div class="shell">
<p class="eyebrow">ESC River Rats Geretsried</p>
<h1>{escape(page_data['title'])}</h1><p>{escape(page_data['description'])}</p>
</div></header>
<section class="content-section sponsors-page"><div class="shell">
<div class="sponsors-intro"><p>{escape(page_data['intro'])}</p>
<p><strong>Ansprechpartner Sponsoring:</strong> {escape(contact['name'])}<br>
<strong>E-Mail:</strong> <a href="mailto:{escape(contact['email'], quote=True)}">{escape(contact['email'])}</a><br>
<strong>Telefon:</strong> <a href="tel:{escape(phone_tel, quote=True)}">{escape(contact['phone'])}</a></p></div>
<div class="sponsors-grid" aria-label="Sponsoren des ESC River Rats Geretsried">{''.join(cards)}</div>
</div></section></main>'''

out = public / 'sponsoren' / 'index.html'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(pre + main + post, encoding='utf-8')
print(f'Rendered internal sponsors page from {len(cards)} canonical sponsor records')

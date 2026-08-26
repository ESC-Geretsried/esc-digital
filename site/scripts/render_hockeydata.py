#!/usr/bin/env python3
from pathlib import Path
from html import escape
import json
import re

root = Path(__file__).resolve().parents[2]
public = root / "site" / "public"
page_path = public / "river-rats" / "index.html"
home_path = public / "index.html"
config_path = root / "content" / "river-rats" / "hockeydata.json"
team_path = root / "content" / "river-rats" / "team.json"

if not home_path.exists():
    raise SystemExit(f"ERROR: homepage shell missing: {home_path}")

home = home_path.read_text(encoding="utf-8")
main_open = re.search(r'<main\s+id=(?:"main-content"|main-content)>', home)
if not main_open:
    raise SystemExit("ERROR: homepage main marker missing")
rest = home[main_open.end():]
if "</main>" not in rest:
    raise SystemExit("ERROR: homepage main closing marker missing")
pre = home[:main_open.start()]
_, post = rest.split("</main>", 1)

cfg = json.loads(config_path.read_text(encoding="utf-8"))
team = json.loads(team_path.read_text(encoding="utf-8"))
team_id = cfg["team_id"]
sport = cfg["sport"]
phase = cfg["active_phase"]
permalink = phase["division_permalink"]
label = phase["label"]

def player_card(row):
    image = str(row.get("image", "")).strip()
    media = f'<img src="{escape(image, quote=True)}" alt="{escape(row["name"], quote=True)}" loading="lazy">' if image else '<span>Foto folgt</span>'
    return (
        '<article class="player-card"><div class="player-card__image">' + media + '</div>'
        '<div class="player-card__body"><span class="player-card__number">#' + escape(str(row.get("number", ""))) + '</span>'
        '<h4>' + escape(row["name"]) + '</h4><div class="player-meta"><span>' + escape(str(row.get("nationality", ""))) + '</span>'
        '<span>Schläger: ' + escape(str(row.get("handedness", ""))) + '</span></div></div></article>'
    )

roster_html = []
for group in ("Tor", "Verteidigung", "Sturm"):
    cards = "".join(player_card(row) for row in team["roster"] if row.get("group") == group)
    roster_html.append(f'<div class="roster-group"><h3>{escape(group)}</h3><div class="roster-grid">{cards}</div></div>')

staff_html = "".join(
    f'<article class="staff-card"><strong>{escape(row["name"])}</strong><span>{escape(row["role"])}</span></article>'
    for row in team["staff"]
)
news_html = "".join(
    f'<article class="team-news-card"><time datetime="{escape(row["date"], quote=True)}">{escape(row["date"])}</time>'
    f'<h3><a href="{escape(row["path"], quote=True)}">{escape(row["title"])}</a></h3>'
    f'<a href="{escape(row["path"], quote=True)}">Weiterlesen →</a></article>'
    for row in team["news"]
)

main = f'''<main id="main-content">
<section class="team-hero" style="background-image:url('/{escape(team['hero_image'], quote=True)}')" aria-labelledby="team-title">
  <div class="shell team-hero__content">
    <p class="eyebrow">{escape(team['eyebrow'])}</p>
    <h1 id="team-title">{escape(team['title'])}</h1>
    <p class="team-hero__tagline">{escape(team['tagline'])}</p>
    <div class="team-hero__next"><strong>Nächstes Spiel</strong><div data-hd-widget="hockeydata.los.GameSlider" data-hd-widget-options='{{"apiKey":"__HOCKEYDATA_API_KEY__","divisionId":"{permalink}","sport":"{sport}","teamId":{team_id},"gamesPerGroup":1,"showDivisionName":false}}'></div></div>
  </div>
</section>
<nav class="team-local-nav" aria-label="Bereiche River Rats"><div class="shell team-local-nav__inner"><a href="#uebersicht">Übersicht</a><a href="#teamfoto">Teamfoto</a><a href="#mannschaft">Mannschaft</a><a href="#news">News</a><a href="#spielplan">Spielplan</a><a href="#tabelle">Tabelle</a><a href="#ergebnisse">Ergebnisse</a></div></nav>
<section class="team-section" id="uebersicht"><div class="shell"><p class="eyebrow">Übersicht</p><h2>River Rats</h2><p class="team-overview">{escape(team['overview'])}</p><p>Alle wichtigen Inhalte zur Mannschaft bleiben auf dieser Seite: Teamfoto, Kader, Betreuung, aktuelle Meldungen und der Spielbetrieb.</p></div></section>
<section class="team-section team-section--soft" id="teamfoto"><div class="shell"><p class="eyebrow">Teamfoto</p><h2>River Rats 2026/27</h2><figure class="team-photo"><img src="/{escape(team['team_photo'], quote=True)}" alt="Teamfoto River Rats" loading="lazy"></figure></div></section>
<section class="team-section" id="mannschaft"><div class="shell"><p class="eyebrow">Mannschaft</p><h2>Aktueller Kader</h2>{''.join(roster_html)}<div class="roster-group"><h3>Trainer & Team hinter dem Team</h3><div class="staff-grid">{staff_html}</div></div><p class="team-source-note">Namen und Kaderstand nach der in Git gesicherten ESC-Referenz. Spielerfotos werden nur verwendet, soweit eine veröffentlichte Quelle vorhanden ist.</p></div></section>
<section class="team-section team-section--soft" id="news"><div class="shell"><p class="eyebrow">News</p><h2>Aktuelles von den River Rats</h2><div class="news-grid">{news_html}</div><p><a class="button" href="/aktuelles/">Alle News</a></p></div></section>
<section class="team-section" id="spielplan"><div class="shell"><p class="eyebrow">Spielplan</p><h2>River Rats 2026/27</h2><div class="team-hd-card team-hd-card--wide"><div data-hd-widget="hockeydata.los.Schedule" data-hd-widget-options='{{"apiKey":"__HOCKEYDATA_API_KEY__","divisionId":"{permalink}","sport":"{sport}","teamId":{team_id}}}'></div></div><p class="team-source-note">Ligaspiele kommen aus HockeyData/GamePitch. Vorbereitung, Freundschaftsspiele, Turniere und weitere Zusatztermine können ergänzend über den ORP Editor gepflegt werden.</p></div></section>
<section class="team-section team-section--soft" id="tabelle"><div class="shell"><p class="eyebrow">{escape(label)}</p><h2>Tabelle</h2><div class="team-hd-card team-hd-card--wide"><div data-hd-widget="hockeydata.los.Standings" data-hd-widget-options='{{"apiKey":"__HOCKEYDATA_API_KEY__","divisionId":"{permalink}","sport":"{sport}","columnSet":"default"}}'></div></div></div></section>
<section class="team-section" id="ergebnisse"><div class="shell"><p class="eyebrow">Ergebnisse</p><h2>Spiele & Resultate</h2><div class="team-hd-card team-hd-card--wide"><div data-hd-widget="hockeydata.los.Schedule" data-hd-widget-options='{{"apiKey":"__HOCKEYDATA_API_KEY__","divisionId":"{permalink}","sport":"{sport}","teamId":{team_id}}}'></div></div><p class="team-source-note">Abgeschlossene Begegnungen und Resultate werden aus derselben geschützten HockeyData-Anbindung geladen.</p></div></section>
<link rel="stylesheet" href="https://api.hockeydata.net/css/?los_gameslider&los_schedule&los_standings"><script src="https://code.jquery.com/jquery-3.7.1.min.js"></script><script src="https://api.hockeydata.net/js/?los_icehockey"></script>
</main>'''

html = pre + main + post
html = re.sub(r'<title>.*?</title>', '<title>River Rats | ESC River Rats Geretsried</title>', html, count=1, flags=re.S)
page_path.parent.mkdir(parents=True, exist_ok=True)
page_path.write_text(html, encoding="utf-8")
print(f"Rendered full River Rats team page with HockeyData for team {team_id} / {permalink}")

#!/usr/bin/env python3
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[2]
public = root / "site" / "public"
page_path = public / "river-rats" / "index.html"
home_path = public / "index.html"
config_path = root / "content" / "river-rats" / "hockeydata.json"

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
team_id = cfg["team_id"]
sport = cfg["sport"]
phase = cfg["active_phase"]
permalink = phase["division_permalink"]
label = phase["label"]

main = f'''<main id="main-content">
<header class="page-head"><div class="shell"><p class="eyebrow">ESC River Rats Geretsried</p><h1>River Rats</h1><p>Erste Mannschaft des ESC River Rats Geretsried.</p></div></header>
<section class="hockeydata-section" aria-labelledby="river-rats-spielbetrieb">
  <div class="shell">
    <div class="hockeydata-intro"><div><h2 id="river-rats-spielbetrieb">Spielbetrieb 2026/27</h2><p>{label} · Datenquelle HockeyData/GamePitch</p></div></div>
    <div class="hockeydata-grid">
      <article class="hockeydata-card">
        <h3>Nächstes Spiel / aktuelle Begegnungen</h3>
        <div data-hd-widget="hockeydata.los.GameSlider" data-hd-widget-options='{{"apiKey":"__HOCKEYDATA_API_KEY__","divisionId":"{permalink}","sport":"{sport}","teamId":{team_id},"gamesPerGroup":1,"showDivisionName":false}}'></div>
      </article>
      <article class="hockeydata-card">
        <h3>Tabelle</h3>
        <div data-hd-widget="hockeydata.los.Standings" data-hd-widget-options='{{"apiKey":"__HOCKEYDATA_API_KEY__","divisionId":"{permalink}","sport":"{sport}","columnSet":"default"}}'></div>
      </article>
      <article class="hockeydata-card hockeydata-card--wide">
        <h3>Spielplan River Rats</h3>
        <div data-hd-widget="hockeydata.los.Schedule" data-hd-widget-options='{{"apiKey":"__HOCKEYDATA_API_KEY__","divisionId":"{permalink}","sport":"{sport}","teamId":{team_id}}}'></div>
      </article>
    </div>
    <p class="hockeydata-note">Ligaspiele und Ergebnisse werden aus HockeyData geladen. Vorbereitung, Freundschaftsspiele und weitere Zusatzspiele werden künftig ergänzend über den ORP Editor gepflegt.</p>
  </div>
</section>
<link rel="stylesheet" href="https://api.hockeydata.net/css/?los_gameslider&los_schedule&los_standings">
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://api.hockeydata.net/js/?los_icehockey"></script>
</main>'''

html = pre + main + post
html = re.sub(r'<title>.*?</title>', '<title>River Rats | ESC River Rats Geretsried</title>', html, count=1, flags=re.S)
page_path.parent.mkdir(parents=True, exist_ok=True)
page_path.write_text(html, encoding="utf-8")
print(f"Rendered canonical River Rats HockeyData page for team {team_id} / {permalink}")

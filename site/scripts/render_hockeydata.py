#!/usr/bin/env python3
from pathlib import Path
import json

root = Path(__file__).resolve().parents[2]
page_path = root / "site" / "public" / "river-rats" / "index.html"
config_path = root / "content" / "river-rats" / "hockeydata.json"

if not page_path.exists():
    raise SystemExit(f"ERROR: River Rats output missing: {page_path}")

html = page_path.read_text(encoding="utf-8")
if 'data-hd-widget="hockeydata.los.GameSlider"' in html:
    print("HockeyData block already present; no injection required")
    raise SystemExit(0)

cfg = json.loads(config_path.read_text(encoding="utf-8"))
team_id = cfg["team_id"]
sport = cfg["sport"]
phase = cfg["active_phase"]
permalink = phase["division_permalink"]
label = phase["label"]

block = f'''\n<section class="hockeydata-section" aria-labelledby="river-rats-spielbetrieb">
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
<script src="https://api.hockeydata.net/js/?los_icehockey"></script>\n'''

marker = "</main>"
if marker not in html:
    raise SystemExit("ERROR: River Rats page has no </main> marker")
html = html.replace(marker, block + marker, 1)
page_path.write_text(html, encoding="utf-8")
print(f"Rendered HockeyData block for team {team_id} / {permalink}")

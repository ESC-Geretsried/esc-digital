# ESC Content Migration Intake

Stand: 2026-08-26  
ESC base: `942426e1a6a3a8bf6e35cd99ecf06feab668b420`  
ORP reference: `74bf59dd92cd5c84bc8f8eea5ba7bcd6af9a7184`

| Gate | Ready | Blocker |
|---|---:|---|
| Initial technical seed | **YES** | keine; ausschließlich verifizierte/source-derived Inhalte seeden, ungeklärte Bestandteile fail-safe auslassen |
| Editor acceptance | **NO** | offene reale Acceptance-Defekte #34 und #35 |
| Final PROD go-live | **NO** | #34/#35, Impressum, Datenschutz, Bestellseite und vollständiges Eiskunstlauf-News-Inventar |

Diese Spezifikation ist ausschließlich Analyse und Übergabevertrag. Sie erzeugt keine Content-/Editor-Records, lädt keine Binärdateien hoch, ändert keine Providerbindung und löst kein Deployment oder Merge aus. Git bleibt System of Record.

## Durch HQ aufgelöste Entscheidungen

- River Rats nutzt exakt die kanonische Teamnavigation. Zusätzlicher Founder-/Excel-Tab-Inhalt überschreibt sie nicht.
- Förderverein ist eine eigene Hauptseite und ein eigener Scope unter `/foerderverein/`; der Altpfad ist nur Migrationsquelle.
- U11-Teamfoto ist durch aktualisierte Excel plus alte U11-Seite **VERIFIZIERT**.
- Damenfoto ist Founder-bestätigt **VERIFIZIERT**; `rename_planned=true`, Bildinhalt unverändert, Provenance erhalten.
- Historische News werden ausschließlich für River Rats, Eiskunstlauf und U13 migriert; alle anderen sind **NICHT MIGRIEREN**.
- `Aufbau Teamseiten alte Website` bleibt Migrationsinventar, kein Layoutvertrag. Teamfoto steht direkt nach **ÜBERSICHT**; U11/U9/U7 haben keine Tabelle.

## Readiness- und Fail-safe-Regel

Der Initial Seed darf verifizierte Inhalte umsetzen. Ungeklärte Inhalte, Links, Downloads oder Assets werden nicht erfunden und können zunächst ausgelassen oder – nur bei ausdrücklicher Autorisierung – als Draft/unveröffentlicht vorbereitet werden. Das allein blockiert den gesamten Initial Seed nicht.

Bei Sponsoren mit ungeklärtem Link trifft dieser Intake keine Veröffentlichungsentscheidung: Der Link darf nicht veröffentlicht werden. Der Sponsor wird bis zur Fachentscheidung ausgelassen oder nur nach expliziter Freigabe unveröffentlicht/linklos vorbereitet. Pana bleibt dedupliziert; 47 eindeutige Sponsorobjekte bleiben Lieferbasis.

Impressum und Datenschutz dürfen als source-derived Draft/INT vorbereitet werden. PROD-Go-Live bleibt bis zur erforderlichen fachlichen/rechtlichen und technischen Verifikation gesperrt.

## Reale Editor-Acceptance-Defekte

- Issue #34 `Fehlende Berechtigung`: verständliche, nicht-technische Access-Denied-Endansicht fehlt. **GO-LIVE-BLOCKER — EDITOR PILOT**.
- Issue #35 `Mannschaften bearbeiten`: Fehlerfeedback verschwindet; laut Issue-Kommentar zusätzlich bei News, Seiten, Staff/Betreuer und Spielern. Korrekte Trennung: **IMPLEMENTED / AUTOMATED TESTS PASS / REAL ACCEPTANCE DEFECT OPEN**. **GO-LIVE-BLOCKER — EDITOR PILOT**.

Die Issues bleiben offen. Automatisierte Implementierungsfakten ersetzen keine reale menschliche Acceptance.

## Verhältnis zu PR #33

PR #33 auf Head `f163825748e05bdc25b2272920360ea75ee3b4e4` ist Candidate, HQ-reviewed, weiterhin ungemergt und wartet auf visuelle Acceptance. Er enthält River-Rats-Teamseite, Editor-Initialstand, HockeyData-Schutz, Homepage-Hero-Bestand, Europe/Berlin-Nachwuchsrotation und Content-Purity-Fix. PR #36 dupliziert diese Implementierung nicht. Die spätere U11-Reconciliation benötigt einen eigenen freigegebenen Implementierungsschritt.

## Lieferdateien

| Datei | Zweck |
|---|---|
| `migration-spec.v1.json` | Kanonische maschinenlesbare Gesamtspezifikation und getrennte Readiness-Gates |
| `pages.csv` | Seiten-/Bereichsmatrix mit Source, Content, Medien, Daten, Scope und Ausschlüssen |
| `teams.csv` | Team-Zielstruktur und Bestandsinventar |
| `sport-data.csv` | Provider-/Link-/manuelle Sportdatenregeln |
| `media-downloads.csv` | Medien-/Download-Inventar und Provenance |
| `sponsors.csv` | 47 deduplizierte Sponsoren samt Link-Fail-safe |
| `news.csv` | Harte News-Migrationsgrenze und bekannte Kandidaten |
| `legal.csv` | Impressum und Datenschutz A-I mit Ziel-Anwendbarkeit |
| `social-video.csv` | Gelieferte Handles/Links ohne URL-Raten |
| `acceptance.csv` | Sechs Acceptance-Kontexte plus reale Defekte #34/#35 |
| `open-points.csv` | Offene Punkte mit getrennten Gate-Klassen |
| `resolved-decisions.csv` | Durch HQ aufgelöste Entscheidungen |
| `migration-spec.schema.json` | JSON-Schema für Integritätsprüfung |

## Umfang

- Seiten: 22; VERIFIZIERT 9; ZU VERIFIZIEREN 10; FEHLT 2; WIDERSPRUCH 1.
- Teams: 9; alle Zielstrukturen verifiziert.
- Sportdaten-Zuordnungen: 9.
- Medien-/Download-Zeilen: 18.
- Sponsoren: 47 eindeutige Zeilen aus 48 Bildvorkommen.
- Acceptance-Matrix: 8 Zeilen, davon sechs Scopes und zwei reale Defekte.
- Offene Punkte: 12; kein Punkt blockiert den Initial Technical Seed.

## Noch zu verifizieren

- Eiskunstlauf-News-Einzelinventar; Bestellseite; Josef-Mayr-Link und zehn weitere Sponsorziele; Sponsoring-Ansprechpartner; vollständige Social-URLs; Downloads; zeitabhängige Vereinsangaben; Impressum; Datenschutz.
- Ungeklärte optionale Inhalte dürfen beim Initial Seed ausgelassen werden. Die in `open-points.csv` ausgewiesenen Gate-Klassen sind verbindlich.

## Validierung

Im Repository-Root ausführen:

```bash
python3 scripts/validate_esc_content_migration_intake.py
```

Der Validator führt Intake-Regeln, JSON-Schema-Subset, CSV/JSON-Konsistenz, Status-/Gate-Widerspruchsprüfungen und Secret-Scan aus.

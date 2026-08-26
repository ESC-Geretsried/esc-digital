# ESC Content Migration Intake

Status: **IMPLEMENTATION READY: NO**  
Stand: 2026-08-26  
ESC base: `942426e1a6a3a8bf6e35cd99ecf06feab668b420`  
ORP reference: `74bf59dd92cd5c84bc8f8eea5ba7bcd6af9a7184`

Diese Spezifikation ist ausschließlich Analyse und Übergabevertrag. Sie erzeugt keine Content-/Editor-Records, lädt keine Binärdateien hoch, ändert keine Providerbindung und löst kein Deployment oder Merge aus. Git bleibt System of Record.

## Kanonische Entscheidungen

- `Aufbau NEUE Vereinsseite` ist die verbindliche Vereinsseitenstruktur.
- `Aufbau Teamseiten alte Website` ist nur Migrationsinventar; alte Layouts werden nicht nachgebaut.
- Teamfoto steht direkt nach **ÜBERSICHT**. U11/U9/U7 haben keine Tabelle.
- River Rats bleibt das einzige HockeyData/GamePitch-Team; Provider/API/League Binding ist geschützt.
- Förderverein ist eine eigene Hauptseite und ein eigener Scope unter `/foerderverein/`.
- Historische News werden nur für River Rats, Eiskunstlauf und U13 migriert.
- Video V1 sind strukturierte externe Links; keine Binary-Uploads oder beliebigen iframes/scripts.
- Binärdaten bleiben außerhalb Git; diese Lieferung enthält nur Referenzen, Hashes und Provenance.

## Lieferdateien

| Datei | Zweck |
|---|---|
| `migration-spec.v1.json` | Kanonische maschinenlesbare Gesamtspezifikation |
| `pages.csv` | Seiten-/Bereichsmatrix mit Source, Content, Medien, Daten, Scope und Ausschlüssen |
| `teams.csv` | Team-Zielstruktur und Bestandsinventar |
| `sport-data.csv` | Provider-/Link-/manuelle Sportdatenregeln |
| `media-downloads.csv` | Medien-/Download-Inventar und Provenance |
| `sponsors.csv` | 47 deduplizierte Sponsoren aus DOCX-Bildern und Relationships |
| `news.csv` | Harte News-Migrationsgrenze und bekannte Kandidaten |
| `legal.csv` | Impressum und Datenschutz A-I mit Ziel-Anwendbarkeit |
| `social-video.csv` | Gelieferte Handles/Links ohne URL-Raten |
| `acceptance.csv` | Bestätigte Acceptance-Kontexte; keine Entra-Mutation |
| `open-points.csv` | Blocker, Widersprüche und Verantwortlichkeit |
| `migration-spec.schema.json` | Minimales JSON-Schema für Integritätsprüfung |

## Umfang

- Seiten: 22; VERIFIZIERT 8; ZU VERIFIZIEREN 9; FEHLT 2; WIDERSPRUCH 3.
- Teams: 9.
- Sportdaten-Zuordnungen: 9.
- Medien-/Download-Zeilen: 18.
- Sponsoren: 47 eindeutige Zeilen aus 48 Bildvorkommen; Pana ist im DOCX doppelt und wurde quellengetreu dedupliziert.
- Acceptance-Kontexte: 6.

## Entscheidende offene Punkte

1. River-Rats-Zusatztab versus kanonische Teamnavigation sowie die unvollständig spezifizierte Bestellseite.
2. Förderverein-Zielroute `/foerderverein/` versus aktueller ESC-Pfad unter Verein.
3. Josef-Mayr-DOCX-Link zeigt auf die ESC-Homepage; keine Ersatz-URL wurde geraten.
4. Eiskunstlauf-News müssen vor Implementierung einzeln vollständig inventarisiert werden.
5. Social-Handles benötigen bestätigte vollständige offizielle URLs.
6. Impressum und Datenschutz brauchen unmittelbar vor Go-Live fachlich/rechtliche Freigabe und technischen Zielabgleich.
7. Öffentlicher Sponsoring-Kontakt und zeitabhängige Vereins-/Teamrollen müssen bestätigt werden.

## U11 und Damenfoto

Die aktualisierte Excel ordnet `Geretsried_25-266.jpg` U11 zu; die alte U11-Seite bestätigt dieselbe Teamzuordnung. U11 ist daher **VERIFIZIERT** und darf nach Implementierungsfreigabe in die tägliche Nachwuchsrotation aufgenommen werden. Das Damenfoto ist gemäß ausdrücklicher Founder-Angabe **VERIFIZIERT**; der irreführende Dateiname wird bei kontrollierter Ablage kanonisch umbenannt, ohne den Bildinhalt zu verändern.

## Validierung

Im Repository-Root ausführen:

```bash
python3 scripts/validate_esc_content_migration_intake.py
```

Der Validator prüft Statusklassen, Mindestseiten, exakte Teamstruktur, Sportdaten-Grenzen, die News-Grenze, Sponsor-Eindeutigkeit/Relationships, U11/Damen-Befund, Acceptance-Kontexte und die Mutationssperren.

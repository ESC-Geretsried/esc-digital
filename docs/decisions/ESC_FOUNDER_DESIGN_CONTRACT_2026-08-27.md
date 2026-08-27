# ESC Founder Design Contract — 2026-08-27

Status: FOUNDER-CONFIRMED / BINDING TARGET AFTER MERGE  
Scope: `ESC-Geretsried/esc-digital` reference implementation  
Canonical architecture: OWML JSON / Website AST in `owml/v1/`

## Delivery boundary

This repository record persists the 2026-08-27 evening decisions. It is not a
PROD authorization and does not claim Preview acceptance. Existing Preview vs
PROD, branch/PR/CI and no-secret boundaries remain unchanged.

## Founder review and design input

Founder-facing OWML review always includes a Page Wireframe by default. OWML
JSON remains canonical and D2 remains optional. Founder and Hannes may provide
natural-language design or HockeyData requirements; HQ translates to OWML and
Page Wireframe, Founder approves, then Codex implements through Git, CI and
Preview. Natural-language input does not bypass governance and Hannes needs no
JSON/CSS work or secret access. Semantic values project to website, editor and
validation; purely visual CSS does not create editor fields.

## Homepage target

`AnnouncementTicker -> GlobalHeader -> HeroRotation -> PrimaryEntrances -> News
-> SportAreas -> ClubAreas -> SponsorTicker -> Footer`

PrimaryEntrances are River Rats, Nachwuchs and Mitglied werden. SponsorTicker
remains on the Homepage.

The AnnouncementTicker supports multiple slow sequential messages with
optional links. Its first message is exactly
`DAUERKARTE   Dauerkarten Saison 2026/2027 – jetzt hier verbindlich bestellen`
and links to `https://esc-geretsried.github.io/bestellung/` in a new tab.
Reduced-motion uses a static fallback.

The global desktop header follows the accepted `/u15/` target on all normal
public pages, mobile stays compact, and the entries are River Rats, Nachwuchs,
Damen, Eiskunstlauf, Inklusionssport, Verein, Förderverein and Mitglied werden.

## HeroRotation

| Slide | Claim | Target | Git asset |
|---|---|---|---|
| River Rats | `Eishockey. Gemeinschaft. Geretsried.` | `/river-rats/` | `images/hero/hero-01-bewegung.jpeg` only |
| Damen | `Gemeinsam auf dem Eis.` | `/river-rats-damen/` | `images/teams/damen-team.jpg` |
| Nachwuchs | `Die Zukunft der River Rats.` | daily team target | daily team asset |
| Eislaufschule | `Die ersten Schritte auf dem Eis.` | `/eislaufschule/` | `images/teams/eislaufschule-2025-2026.png` |
| Eiskunstlauf | `Bewegung. Präzision. Ausdruck.` | `/eiskunstlauf/` | `images/teams/eiskunstlauf.jpeg` |
| Inklusionssport | `Gemeinsam Sport erleben.` | `/inklusion/` | `images/teams/inklusion.jpg` |

Nachwuchs uses Europe/Berlin weekday mapping: Monday U7, Tuesday U9,
Wednesday U11, Thursday U13, Friday U15, Saturday U17 and Sunday U20. Image and
click target change together. All listed paths exist in this Git tree; no
pixel/face identification was used.

## Team sports presentation

- River Rats remains HockeyData. The graphical next-game widget is removed
  from the Hero. A verified next home game may appear as a text-only block
  immediately below with date, time and opponent, no logos; otherwise hidden.
  Schedule/standings/results logos remain small and consistent.
- Damen and U13/U15/U17/U20 have no internal schedule/table/results
  presentation. Each has one optional editor-maintained DEB.ONLINE URL rendered
  as `SPIELPLAN & TABELLE` in a new tab. Empty hides it. No URL is invented.
- U7/U9/U11 retain their separate current rules.

The OWML patterns in this branch persist this target. Runtime/editor completion
and Preview acceptance remain separate work unless implemented and tested by
the same change.

## Common player model and placeholder

Required: position `T`/`V`/`S`, number, name. Optional: photo reference, shoots,
RODI for River Rats/Damen/U13-U20, and editorial Info. Empty Info is not shown
and is not calculated. The photo slot always renders the real assigned photo or
the canonical hockey-player placeholder while source data keeps photo empty.

`OPEN`: the Founder-provided placeholder binary/path is not present in current
Git and cannot be safely reconstructed from chat. Do not invent or substitute
it.

## Vereinsführung mapping

`content/verein/vereinsfuehrung/portrait-map.json` is the explicit identity
mapping. It binds stable `person_id` values to exact portrait paths and
checksums for Thomas Gania, Markus Janka, Jens Neuhaus, Stefan Heindl, Sabrina
Kruck, Ulla Köhler, Melanie Vollbrecht and Romy Schiek. Validation compares IDs,
paths, front matter, files, manifest and hashes. It never uses order or face
recognition.

## Routing and OWML status

Canonical routes remain lower-case. `/U15` and `/vereinsfuehrung/` remain QA
proposals/open because no separate persisted approval was found; they are not
made binding here.

OWML is ORP-created and is not an official external standard. IDEA-0002 is a
BACKLOG evaluation only and authorizes no architecture replacement.

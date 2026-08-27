# OWML implementation and migration report

Status: implemented on this branch; Preview/PROD acceptance is separate.

## Coverage

The canonical page catalog covers the union of current Git content routes, the
preserved imported-page manifest and the binding independent
`/foerderverein/` route. It currently contains 50 page instances. The governed
library includes Homepage, Team Page, News Index, Article, Event, Sponsor,
Contact/Geschäftsstelle, Membership, Donation/Förderverein, Board/
Vereinsführung, Eislaufschule, Eiskunstlauf, Inklusion, Verein, Nachwuchs,
Legal, Service and Generic Section.

`/river-rats-herren/` and `/verein/foerderverein/` remain covered compatibility
redirects. The canonical independent Förderverein route is `/foerderverein/`.

## U15 observed vs target

The 2026-08-27 observation contained Header, photo Hero, local navigation,
Übersicht, Teamfoto, Kader, Kontakte and Footer. Against binding INV-002 it
lacked News, Spielplan, Tabelle and Ergebnisse and did not provide the semantic
next-game Hero slot.

The target instance now uses the common Team Page pattern. Because no verified
next game, schedule, table or results facts are present in Git, these slots use
stable factual empty states. No date, opponent, result, table or provider link
is invented. Teamfoto remains both approved Hero media and a separate section.
Contacts remain a supplementary semantic slot after the binding primary order.

## Runtime and editor boundary

The final build adapter stamps every output route with its OWML version,
instance and pattern only after all renderers have finished. Any emitted page
without a catalog instance fails. Drift checks exact required anchors, one main
landmark, one H1, document language and image alt attributes. River Rats keeps
the protected HockeyData binding; U7/U9/U11 omit standings.

Normal editorial configuration is explicitly content/approved-slot only. OWML
version, pattern, nodes, order, navigation, route and renderer remain
architecture workflow fields. The ORP editor rejects structural payloads and
existing page route/type changes server-side.

## Recovery

`owml/v1/recovery-manifest.json` identifies canonical inputs and regenerable
outputs. The normal CI build is the rebuild gate and asserts no deployment.
SVG is canonical; PNG is optional because no portable rasterizer is needed to
reconstruct or verify the architecture.

## Open data, not implementation drift

- non-River-Rats next-game, schedule, standings and results facts/official URLs
  remain absent until verified editorial or official-source data is supplied;
- U7/U9/U11 intentionally have no standings slot;
- live Preview visual/functional acceptance remains open;
- PROD deployment/cutover remains unauthorized.

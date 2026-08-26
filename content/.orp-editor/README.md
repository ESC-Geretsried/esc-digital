# ORP Editor pilot records

This directory contains structured editor records consumed by the ORP
`GitContentProvider`. It is not a second editorial source.

## Existing River Rats pilot

The four River Rats records are the existing draft-only projection from ESC
`main`. Issue #37 does not expand or rewrite them. River Rats/HockeyData remains
owned by draft PR #33 and is deliberately not duplicated here.

Bound source digests (existing pilot, SHA-256):

- `content/river-rats/_index.md`: `a0d6f9ac81b02b0d80454154537582556072b77495749790f1dbd54337038184`
- `content/river-rats/team.json`: `8fe4e218fdbcfbda1a9efdefb3befcf25a78f25120ec2949c0b769592c220772`
- `content/river-rats/hockeydata.json`: `4e6240ec91ead4414dacf9728b0edce03a3fdac87114c0ab0a79ba0bedbe05c4`
- `content/navigation.json`: `11bfb6cff1090749155a15d1b8f4edd934a5c08d8d7b72ba2225fbd23a17565e`

## Issue #37 verified initial seed

Tranche 1 seeds `nachwuchs`: one Area, one overview Block and one Page record.
The visible canonical page uses the exact Founder text carried by migration-intake
PR #36, row `nachwuchs` in `docs/content-migration/initial-intake/pages.csv` at
`bc817f887f42f4c1f8cfa3b68a2d65bd895b0f1a` (`status=VERIFIZIERT`).

Bound implementation source:

- intake commit: `bc817f887f42f4c1f8cfa3b68a2d65bd895b0f1a`
- intake row: `pages.csv` / `nachwuchs`
- canonical rendered source: `content/nachwuchs/_index.md`
- canonical source SHA-256 after seed: `e970900574ac4598f3d125d7acf9d5e97339ecf58aa256009b6e9bc72d45c3b3`

## Issue #37 tranche 2

Tranche 2 adds draft Area, overview Block, Page and Team records for the scopes
`damen`, `u17`, `u15`, `u11`, `u9` and `u7`, because PR #36 marks those page
scopes `VERIFIZIERT`. The team-section vocabulary and table/no-table boundary are
bound to `teams.csv`. No people, contacts, roster facts, provider URLs, league
facts or asset keys are added. `u20` and `u13` remain omitted here because their
`pages.csv` rows are still `ZU VERIFIZIEREN`, despite the team-structure inventory.

Damen uses the source-derived overview sentence already present in the repository
INT snapshot. The youth pages intentionally persist only the verified canonical
section structure until factual page copy is separately verified.

Bound tranche-2 sources:

- intake commit: `bc817f887f42f4c1f8cfa3b68a2d65bd895b0f1a`
- intake rows: `pages.csv` / `damen,u17,u15,u11,u9,u7`
- team rules: `teams.csv` / matching team keys
- Damen source snapshot: `imports/esc-int-pages/river-rats-damen/index.html`
- `content/damen/_index.md`: `399f6819cea16e51d8a5cb38ace2f500dec52f8332e6503d2b23f0702a0441f5`
- `content/u17/_index.md`: `c54d3303bd1f907806a3685e214958bab9854ffb229e1a5dfd3a32810ef59d63`
- `content/u15/_index.md`: `b422d8d62d1dca17be02509bc21c1802e3530e4001517802f9305f98880626f6`
- `content/u11/_index.md`: `8cadd1d06c47fb59f426a8ca4f48d03167d9d3997568eb7ad20e23db180c7362`
- `content/u9/_index.md`: `58c5691af543b6533775b96e77c58fa94c82298ff4f3573c10c625eaa0488117`
- `content/u7/_index.md`: `40d8759e6b4babe2388cfcfc6caf032362b815960d0a3afb2235c22e0a0cab8c`

Fail-safe exclusions across both tranches: no unresolved people, contacts,
opening hours, social URLs, downloads, external sport-data URLs, provider
bindings, legal text, invented asset keys or unauthorized historical news.
Eiskunstlauf historical news remains omitted because the intake marks its
individual inventory incomplete.

U11 photo reconciliation is not applied on this branch because the homepage
rotation implementation that can consume it is still owned by unmerged draft
PR #33. The verified evidence remains in PR #36 (`Geretsried_25-266.jpg`) for a
later integration step after branch reconciliation.

Any later refresh requires a new source-digest check and reviewed mapping diff.

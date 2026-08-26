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

The first additional source-pure seed is `nachwuchs`: one Area, one overview
Block and one Page record. The visible canonical page is updated from the exact
Founder text carried by migration-intake PR #36, row `nachwuchs` in
`docs/content-migration/initial-intake/pages.csv` at
`bc817f887f42f4c1f8cfa3b68a2d65bd895b0f1a` (`status=VERIFIZIERT`).

Bound implementation source:

- intake commit: `bc817f887f42f4c1f8cfa3b68a2d65bd895b0f1a`
- intake row: `pages.csv` / `nachwuchs`
- canonical rendered source: `content/nachwuchs/_index.md`
- canonical source SHA-256 after seed: `e970900574ac4598f3d125d7acf9d5e97339ecf58aa256009b6e9bc72d45c3b3`

Fail-safe exclusions in this seed: no people, contacts, opening hours, social
URLs, downloads, external sport-data URLs, provider bindings, legal text,
asset keys or historical news are added. Eiskunstlauf historical news remains
omitted because the intake marks its individual inventory incomplete.

U11 photo reconciliation is not applied on this branch because the homepage
rotation implementation that can consume it is still owned by unmerged draft
PR #33. The verified evidence remains in PR #36 (`Geretsried_25-266.jpg`,
updated Founder Excel plus matching old U11 page) for a separately reviewable
reconciliation after branch integration.

Any later refresh requires a new source-digest check and reviewed mapping diff.

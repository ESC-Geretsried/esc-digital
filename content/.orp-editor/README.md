# ORP Editor records

This directory contains structured editor records consumed by the ORP
`GitContentProvider`. It is a reviewable projection of canonical ESC sources,
not a second editorial source.

## River Rats pilot

The original draft-only River Rats pilot consists of one Area, one overview
Block, one Page and one base Team. Its records and the protected HockeyData
configuration are unchanged by Issue #37. The separate Draft PR #33 owns the
River Rats roster, staff, news, team-page and homepage-rotation implementation.

Bound source digests (SHA-256):

- `content/river-rats/_index.md`: `a0d6f9ac81b02b0d80454154537582556072b77495749790f1dbd54337038184`
- `content/river-rats/team.json`: `8fe4e218fdbcfbda1a9efdefb3befcf25a78f25120ec2949c0b769592c220772`
- `content/river-rats/hockeydata.json`: `4e6240ec91ead4414dacf9728b0edce03a3fdac87114c0ab0a79ba0bedbe05c4`
- `content/navigation.json`: `11bfb6cff1090749155a15d1b8f4edd934a5c08d8d7b72ba2225fbd23a17565e`

## Issue #37 initial seed

The initial seed adds draft records for `damen`, `nachwuchs`, `u20`, `u17`,
`u15`, `u13`, `u11`, `u9` and `u7`. It contains only source-derived overview
text, deterministic internal links and the verified official sport-source URLs
from intake PR #36. U11, U9 and U7 remain manual and have no league provider or
table. Manual preparation, friendly and tournament fixtures remain available
through the existing editor schedule model.

No player, staff, contact, historical-news, asset, download, provider or secret
record is introduced. U13 historical news remains unseeded while its candidates
are `ZU VERIFIZIEREN`; Eiskunstlauf news remains unseeded while its complete
inventory is `FEHLT`.

`initial-seed-manifest.v1.json` binds every used source digest, scope, official
URL, record count and fail-safe omission. The U11 photo reconciliation is not
performed: `Geretsried_25-266.jpg` is verified by intake, but the exact binary is
not present in canonical Git and PR #33 owns the supported homepage rotation.

Validate from the repository root:

```bash
python3 scripts/validate_esc_content_migration_intake.py
python3 scripts/validate_esc_initial_content_seed.py
```

Any later refresh requires a new source-digest check and a reviewed mapping
diff. Existing canonical source files must remain unchanged.

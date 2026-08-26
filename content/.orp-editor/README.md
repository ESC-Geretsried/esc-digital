# ORP Editor pilot records

This directory contains structured editor records consumed by the ORP
`GitContentProvider`. It is not a second editorial source: these River Rats
pilot records project the actual editorial starting state on PR #33, based on
ESC `main` at `942426e1a6a3a8bf6e35cd99ecf06feab668b420`.

Included records are one Area, one overview Block, one Page, one Team, 16
Players, nine Staff records and four News records for scope `river-rats`.
HockeyData/GamePitch league facts, provider/API/league bindings, standings and
results are deliberately not copied into editor-owned records. Supplemental
fixtures remain separate ORP Editor records when an editor creates them.

The existing historical Git images and verified public player-image references
remain the current page sources. No Binary Assets V1 record or asset key is
invented: `hero_asset_key`, `team_photo_asset_key` and player/staff
`photo_asset_key` stay empty until an approved Binary Assets V1 mapping exists.
The public page continues to use the existing Git hero/team photo references.

Bound source digests (SHA-256):

- `content/river-rats/_index.md`: `ebd2855fa5dddd44b23735213d334bab8df726640cf847cf4c58e787a314010e`
- `content/river-rats/team.json`: `a7e471d6f2e8aaffbe24141e447ff6ba5ac98606ec8ddf9a934c76ad3ea57bbb`
- `content/river-rats/hockeydata.json`: `5b98d43e5f6116541aec24171c3e3470bf9d874804f2cbf13c9bf49a58fc3bdc`
- `content/navigation.json`: `7100d875a33dff08a6304922145a6d566519cdac92b0cb25df9c4f26881749d1`

Any later refresh requires a new source-digest check and reviewed mapping diff.

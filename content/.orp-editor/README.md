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

## River Rats roster display rule

SOLL: the River Rats team page displays every verified roster and staff record
from `content/river-rats/team.json`. Player cards expose jersey number, name,
position/group, nationality and shooting hand, and use a player image only when
the canonical source record contains an unambiguous published image reference.
Players without such a reference remain visible with a neutral no-photo state.
Staff exposes verified name and role only.

IST at this PR: 16 players and nine staff records are the canonical River Rats
roster projection. Ten of the 16 player rows contain a verified published image
reference; six do not. The existing Git team photo remains the team-photo source.

PRODUCT DECISION: team frontends do not display body height or weight. Generic
editor schema fields such as `height_cm` and `weight_kg` are retained and are not
destructively migrated or removed. This ESC PR enforces the decision only for
the River Rats frontend and validator; it does not claim that ORP Core has
already canonicalized the rule.

CENTRAL ORP CANONICALIZATION REQUIRED: persist the product/design rule in the
ORP Platform repository for all sport/team modules: height and weight may exist
in provider or generic schema data, but must not be exposed by team frontend
components. Preserve provider neutrality and avoid schema-breaking deletion.

EVIDENCE: `content/river-rats/team.json` on this PR, with source metadata and the
existing 16-player / nine-staff editor validation. Missing data DELTA: no
verified player photo reference exists for Benedikt Goldschmidt, Michael
Kristic, Anton Egle, Sebastian Heininger, Gunārs Skvorcovs or Oliver Ott beyond
what the canonical file records; no replacement image may be inferred.

Bound source digests (SHA-256) from the initial PR #33 seed:

- `content/river-rats/_index.md`: `ebd2855fa5dddd44b23735213d334bab8df726640cf847cf4c58e787a314010e`
- `content/river-rats/team.json`: `a7e471d6f2e8aaffbe24141e447ff6ba5ac98606ec8ddf9a934c76ad3ea57bbb`
- `content/river-rats/hockeydata.json`: `5b98d43e5f6116541aec24171c3e3470bf9d874804f2cbf13c9bf49a58fc3bdc`
- `content/navigation.json`: `7100d875a33dff08a6304922145a6d566519cdac92b0cb25df9c4f26881749d1`

Any later refresh requires a new source-digest check and reviewed mapping diff.

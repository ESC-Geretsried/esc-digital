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
roster projection. Eleven of the 16 player rows contain a verified published
image reference; five do not. The existing Git team photo remains the team-photo
source.

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
Kristic, Anton Egle, Sebastian Heininger or Gunārs Skvorcovs in the canonical
file; no replacement image may be inferred.

Bound source digests (SHA-256) from the initial PR #33 seed:

- `content/river-rats/_index.md`: `ebd2855fa5dddd44b23735213d334bab8df726640cf847cf4c58e787a314010e`
- `content/river-rats/team.json`: `a7e471d6f2e8aaffbe24141e447ff6ba5ac98606ec8ddf9a934c76ad3ea57bbb`
- `content/river-rats/hockeydata.json`: `5b98d43e5f6116541aec24171c3e3470bf9d874804f2cbf13c9bf49a58fc3bdc`
- `content/navigation.json`: `7100d875a33dff08a6304922145a6d566519cdac92b0cb25df9c4f26881749d1`

Any later refresh requires a new source-digest check and reviewed mapping diff.

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

U11 photo reconciliation is implemented on the consolidated preview branch.
The verified source is PR #36 / migration intake `Geretsried_25-266.jpg`.
The canonical tenant copy is `images/teams/u11-team.jpg` with SHA-256
`5b7c979a8f2c4aa7b738a9e859353f6a0252e762a11e76b5755d710bd1779c3a`.
U11 is protected as a canonical route, displays the verified team photo directly
after the overview, and participates in the Europe/Berlin daily youth hero rotation.

Any later refresh requires a new source-digest check and reviewed mapping diff.

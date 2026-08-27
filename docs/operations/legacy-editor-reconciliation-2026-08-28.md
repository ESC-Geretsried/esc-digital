# Legacy editor reconciliation, 2026-08-28

## Scope and safety boundary

This review reconciles the twelve commits preserved by draft PR #56 on
`orp/editor/esc/942426e1a6a3a8bf6e35cd99ecf06feab668b420` against canonical ESC
`main` at `81bdc1bdde9a5093ecc3be0e1f2172662786c872`.

The legacy branch is 12 commits ahead of and 50 commits behind `main`, with
merge base `942426e1a6a3a8bf6e35cd99ecf06feab668b420`. It is preservation evidence,
not an integration source. No commit was cherry-picked, merged, or rebased.
Each payload was reviewed against the current Git-only content contract, the
Founder-provided source records, OWML, and the current canonical content.

## Commit-by-commit assessment

| Commit | Payload | Classification | Reconciliation decision |
| --- | --- | --- | --- |
| `52cd479ee73ba322515690316b4cee3ffe9f7956` | Replaces the River Rats page body with `.` and adds editor audit metadata. | Conflicting/outdated; page content replaced on current `main`. | Do not carry forward. Current `main` contains the meaningful, source-bound body and summary. The actor hash and legacy timestamps do not justify degrading the copy. |
| `3985db683b92fd3d78c19b8a6ad7b41502853494` | Advances only the review/source timestamps of the same `.` page state. | Conflicting/outdated metadata. | Do not carry forward. It describes an invalid intermediate page state. |
| `ca5e3c4018fa98a6352b284f93fb0768ac0313dd` | Advances only the review/source timestamps again. | Conflicting/outdated metadata. | Do not carry forward. It has no independent editorial payload. |
| `8d9392836630497b272c5c2285c6132946208412` | Advances only the review/source timestamps again. | Conflicting/outdated metadata. | Do not carry forward. It has no independent editorial payload. |
| `bd4012c735395aae03915251e31c264712ec66a1` | Creates player `Hannes`, birth year 1900, jersey 63, weight 150, with joke/free-text values such as `Weit drüber` and `Besser neben dem eis`. | Pure test/seed data. | Do not carry forward. It is not supported by the Founder roster or the verified River Rats source, and it violates the source-pure roster boundary. |
| `7e7e05f5a9a1909cc4b9b08ead059045d428e52b` | Creates `TestNEws` with `TEaser der Testnews` and `ohne Inhalt`. | Pure test/seed data. | Do not carry forward. It is explicitly test-labelled, unverified, and not valid public copy. |
| `602fc72939fc61b67ab4829aac2d611f7b09399c` | Adds an expiry and changes timestamps on `TestNEws`. | Pure test/seed data. | Do not carry forward. It only mutates the preceding test record. |
| `3da6803da6944304e20c5245a0c5318a1118dbc6` | Changes timestamps/actor metadata on the legacy `.` River Rats page state. | Conflicting/outdated metadata; page content replaced on current `main`. | Do not carry forward. It has no independent editorial payload. |
| `62f2479ef89cbe4ea02fc2102087d6e59f687e4c` | Creates an incomplete draft fixture, `Blues 1` vs. `River Rats`, without competition or venue. | Pure test/seed data; unsupported by the current provider boundary. | Do not carry forward. HockeyData/GamePitch remains authoritative for league facts, while editor-created supplemental fixtures require verified editorial intent. |
| `cdf66ae356aa76aec4c8217da6eb28d240bbb4e4` | Creates staff member Alwin Albert as Manager and adds an email address. | Valid name/role already replaced by current `main`; unverified contact detail conflicts with the source-pure contract. | Do not duplicate. Current `main` already has canonical Staff record `orp:esc-main:staff:river-rats:alwin-albert` with verified name, role, ordering, and image evidence. Do not carry the email because the current contract exposes verified name and role only and excludes unresolved contacts. |
| `46acd3a1a493509f47c87aa0d81e0192285667e7` | Creates draft event `Weißwurst Essen` with event key `ww`, empty description, and free-text venue `ICE Stüberl`. | Pure test/seed data; structurally outside the current canonical Git-only projection. | Do not carry forward. No authorized source evidence or current canonical Events collection supports publication. |
| `6e7163dbd115b235745eabfd732af253afdebd7f` | Creates a People record for Alwin Albert/Manager. | Valid identity semantics already replaced by canonical Staff; conflicting/obsolete entity projection. | Do not duplicate. Current `main` deliberately models the verified River Rats role as Staff, and the current editor projection has no canonical People collection. |

## Reconciled result

No legacy content file is copied to current `main`.

The only independently credible legacy facts are Alwin Albert's name and Manager
role, and both are already present in the canonical Staff record on `main` with
stronger source and image provenance. The legacy email is not imported. The
River Rats page has already been replaced with better copy. The remaining
records are clearly test/seed data or lack the source evidence required by the
current Founder/Git-only contracts.

This is therefore a semantic zero-content reconciliation, not an empty review:
it explicitly prevents seven legacy paths from overwriting or duplicating the
current canonical estate while preserving PR #56 as immutable review evidence.
No valid, source-supported editorial content identified in the twelve commits is
lost.

## Verification

The reconciliation branch passed the repository-local equivalents of the
required CI gates:

- OWML validate, generated-output check, drift check, and five unit tests;
- content-migration intake, initial seed, Founder roster projection, and
  Git-only completion validators;
- River Rats Editor state, news retention, hero rotation, portrait checksums,
  and portrait mapping validation;
- canonical Hugo build, static validation, routing/accessibility smoke gate,
  HockeyData VOID fallback, and public-copy leak gate;
- GitHub Pages base-path build and `/esc-digital/` homepage routing checks;
- recovery manifest: all 13 required inputs and seven regenerable outputs
  present, expected deployment `NONE`, and no secrets stored in Git.

The local builds emitted only upstream Hugo deprecation warnings for
`languageCode` and `.Site.Data`. No deployment command was run.

## Re-bind gate

PR #56 must remain open only for preservation/review and must not be merged.
The Editor re-bind may be prepared only after the reconciliation PR is green,
reviewed, and merged into canonical `main`. Before changing the binding, verify
the then-current `main` SHA, rerun the repository's full local/CI gates, and bind
the Editor to a new branch derived from that exact SHA. This review does not
authorize a runtime write, Preview/PROD deployment, or direct push to `main`.

`SAFE REBIND READY: NO` until the reconciliation PR is green, reviewed, and
merged and the canonical `main` SHA is re-verified.

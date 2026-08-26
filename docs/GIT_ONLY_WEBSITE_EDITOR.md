# ESC Git-only Website/Editor profile

Status: preview implementation profile, 2026-08-26.

## Binding boundary for this repository

Git is the System of Record for ESC website content, ORP Editor records and
website/media assets. The deterministic site build consumes only versioned
repository inputs plus explicitly documented non-secret build parameters.
SharePoint is not a required content, media, build or publishing dependency.

Microsoft Entra remains the runtime identity provider. Entra app roles and
server-side scope checks remain the authorization boundary; this change does
not replace authentication, weaken RBAC or copy user/group membership into Git.

The ESC Editor runtime selects the ORP Git provider with the established
provider boundary:

```text
ORP_EDITOR_PROVIDER=git
ORP_EDITOR_GIT_REPO=<controlled ESC repository checkout>
ORP_EDITOR_IDENTITY_NAMESPACE=tenant:esc
```

The Git-forge adapter may be used as a separately reviewed implementation for
structured JSON writes. It does not add binary upload, PR, merge, deployment or
PROD authority. In this ESC profile, verified team/staff photos are immutable
Git assets with versioned paths and checksums; no SharePoint media library is
required to build or display them.

## Founder roster projection

`docs/content-migration/founder-team-rosters-2025-2026.md` is the durable source
record. `scripts/sync_founder_team_rosters.py` deterministically projects its
eight sections into:

- `content/teams/<team-key>/team.json` for the website;
- canonical team page sources under `content/`;
- `content/.orp-editor/` Area, Team, Page, Player and Staff records.

Names, number duplicates, position codes, ordering and contact group wording
are preserved. The projection does not silently correct or infer data. Records
remain `draft`; the branch is a preview candidate, not a PROD publication.

## Public news retention

`config/news-retention.json` binds an exact 12-calendar-month public window in
`Europe/Berlin`. At the anniversary boundary, expired homepage references and
generated public article directories are removed from the build artifact.
Canonical content, imported source snapshots and Git history are not deleted.

For reproducible tests, `NEWS_RETENTION_AS_OF=YYYY-MM-DD` fixes the policy date.
Without it, builds use the current date in the configured policy timezone.

## Safety and release boundary

The normal flow remains `branch -> PR -> CI -> preview review`. This profile
does not authorize a `main` merge, preview publish outside configured CI, PROD
deployment, DNS change, secret write or identity/role mutation.

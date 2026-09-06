# ESC Official Records

Status: ESC REFERENCE IMPLEMENTATION / AUTHORITATIVE RECORD INDEX

This directory is the Git-backed index for official ESC organizational documents, forms, policies and processes. It follows the proposed ORP Official Records & Processes Contract.

## Rules

- Git is the approved-version System of Record once a record package is merged.
- Original source artifacts outrank derived Markdown, D2 and JSON representations.
- `ai/*.md` and `ai/*.d2` are machine-readable derived representations for humans, automation and future AI modules.
- Derived representations must never silently change the meaning of an approved source.
- Draft, superseded or conflicting records must not be treated as current normative authority.
- Submitted member/person data does not belong here.

## Current bootstrap records

| record_id | title | class | authority state | official source |
|---|---|---|---|---|
| `esc-membership-application` | Beitrittserklärung / Änderungsmeldung | form | APPROVED CURRENT TEMPLATE; submission note partly superseded | https://www.esc-geretsried.de/static/225f3452b00217a764bf6ef83b3b57fe/ESC-River-Rats-Beitrittserklrung-v19.pdf |
| `esc-satzung` | Satzung | governance | APPROVED / CURRENT per Founder confirmation 2026-08-23 | https://www.esc-geretsried.de/static/f9c7dafb886e14f3dbbe2f87fbef3506/Satzung.pdf |
| `esc-geschaeftsordnung` | Geschäftsordnung v26 | governance/process | APPROVED / CURRENT per Founder confirmation 2026-08-23 | https://www.esc-geretsried.de/static/61a58ee5555030d715fba4fb1f3a4935/250501_ESC-River-Rats-Geschaeftsordnung-v26.pdf |
| `esc-leitbild` | Leitbild ESC River Rats Geretsried e.V. | guideline | APPROVED / CURRENT per Founder confirmation 2026-08-23 | https://www.esc-geretsried.de/static/1c4517c93c91bcec1f65fa2ccd064ad8/Leitbild-ESC-Geretsried.pdf |

The current official publication collection is https://www.esc-geretsried.de/downloads/ .

## Known authority conflict

The 2018 membership form states that applications cannot be accepted by email. The current Satzung permits a fully completed and signed written admission application by letter or email to the Geschäftsstelle. The current Satzung therefore controls the submission process; the old form remains authoritative for its form fields/mandate structure until replaced, but its no-email operational note must not be used as current process authority.

Original PDF bytes are not yet stored in this branch. Their official URLs are recorded as provenance. Storing immutable approved source bytes with cryptographic hashes is the target state and should be performed through the controlled record-ingestion workflow when available.

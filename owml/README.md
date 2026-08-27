# ESC OWML v1 reference profile

This directory is the canonical website-architecture source for ESC Digital.
It implements the ORP Website Modeling Language `1.0.0` decision for every
existing and new page. Content remains under `content/`; OWML governs semantic
page structure, order, route coverage, allowed bindings and renderer coverage.

Canonical inputs:

- `v1/patterns.json` — governed pattern library;
- `v1/pages.json` — one instance assignment for every current route;
- `v1/node-catalog.json` — allowed node types and renderer bindings;
- `v1/editor-policy.json` — content-slot and structure-lock boundary;
- `v1/pilots/u15.observed.json` — non-authoritative observed pilot evidence;
- `v1/schema/owml-site.schema.json` — JSON Schema contract;
- `v1/recovery-manifest.json` — rebuild inputs and no-deployment boundary.

`v1/generated/` contains deterministic D2, SVG, Markdown, runtime-route and test
views. Edit canonical JSON, then run `python3 scripts/owml.py generate`. CI runs
the check form and fails when generated artifacts differ.

The build runs `validate -> generated==expected -> render -> bind-runtime ->
drift`. Unknown node types, missing renderers, uncovered emitted routes, missing
anchors and basic structural accessibility errors fail closed. SVG is the
canonical visual output; PNG is optional and intentionally not a build or
recovery dependency.

No command in this profile deploys PROD.

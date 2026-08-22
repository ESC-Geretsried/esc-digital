# ESC Digital Website Source

Status: M2 source/build baseline

`site/` is the canonical source/build area for the ESC website. Root-level HTML/CSS/JS currently present in the repository is preserved transition output and is not the long-term authoring model.

## Principles

- Source-first: generated output must be reproducible from versioned source and non-secret configuration.
- Static-first: the public website should require no application server for normal page delivery.
- Performance-first: minimize client JavaScript and runtime dependencies.
- Content without AI dependency: editors and publishing must remain operable without an AI provider.
- Provider-neutral deployment: Netlify or another static host may implement delivery, but hosting state is not canonical.
- No secrets in source or generated output.
- The frozen visual reference remains `ESC-Geretsried/esc-design-reference`; it is an acceptance reference, not a dependency.

## Baseline structure

- `src/` — website source templates/components/styles/assets owned by ESC Digital.
- `public/` — generated static output; not authoritative source.
- `scripts/` — deterministic local/CI build and validation helpers.

## Build contract

A future implementation must provide a deterministic command that transforms versioned inputs into `site/public/` and a validation command that fails on broken internal links/assets and other defined acceptance violations.

The concrete site generator/framework is intentionally **not selected by this baseline**. Selecting or replacing a framework is an implementation decision and must preserve the contract above.

## Transition gate

Do not delete the historical generated root website until a new build can be produced and reviewed independently and the frozen design reference remains reachable.

# ESC Digital

`ESC-Geretsried/esc-digital` is the canonical ESC tenant/product repository.

## Scope

This repository may contain ESC-specific:

- website source, content and assets;
- modules and digital functions;
- integrations and adapters;
- tenant configuration;
- operational support code and runbooks;
- validation and deployment configuration for ESC-owned digital services.

## Boundary to ORP

Reusable ORP Core, ORP governance and cross-tenant platform capabilities remain in `open-reference-platform/platform`.

An ESC-specific function may start here when it is genuinely tenant-specific. If it becomes generically reusable, it must be deliberately reviewed and, where appropriate, extracted/generalized into ORP before other tenants depend on it.

## System of Record

Git is the System of Record for the repository content. Provider runtimes, CI, hosting, identity and AI integrations are implementations/adapters and must remain replaceable.

## Current transition state

The repository was renamed from `esc-website-dev` on 2026-08-22. The pre-transition generated Hugo snapshot is preserved independently in:

- branch `legacy/esc-website-dev-design-2026-08`;
- public visual reference repository `ESC-Geretsried/esc-design-reference`.

The legacy generated files still present at repository root are transition material and are not the intended final source layout.

## Intended top-level layout

- `site/` — website source and build inputs
- `content/` — canonical publishable/editorial content where applicable
- `modules/` — ESC-specific functional modules
- `integrations/` — ESC-specific provider/system adapters
- `config/` — non-secret tenant configuration
- `ops/` — ESC operational documentation and automation support
- `tests/` — repository-level tests and acceptance checks
- `docs/` — repository-local architecture and contributor documentation

No secret, token, private key, recovery code or production credential belongs in this repository.

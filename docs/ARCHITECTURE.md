# ESC Digital Architecture Boundary

Status: M2 skeleton / transition baseline

## Canonical website model

OWML `1.0.0` under `owml/` is the canonical semantic website architecture for
every ESC route. Hugo, Python renderers, editor configuration, navigation and
generated diagrams are subordinate adapters. Unknown nodes/routes and final
runtime drift fail closed. This is the ESC reference profile of the ORP Website
Module contract and does not make ESC-specific patterns ORP Core.

## Repository role

`esc-digital` is the ESC-owned tenant/product repository. It is intentionally broader than the website, but it is not ORP Core.

## Allowed here

ESC-specific website source/content/assets, tenant configuration, club-specific modules, integrations, operational automation support, tests and deployment configuration.

## Not allowed here by default

- ORP governance or canonical ORP decision records;
- reusable cross-tenant platform capabilities that should live in ORP;
- secrets or recovery material;
- unmanaged copies of provider state treated as canonical without an explicit migration decision.

## Promotion path for reusable functionality

`ESC need -> ESC-specific implementation -> review for generic reuse -> ORP extraction/generalization if justified -> versioned/released ORP capability -> ESC consumes released capability`

No functionality becomes ORP Core merely because ESC implemented it first.

## Transition safety

The historical generated site is already preserved outside the active development path. During M2, root-level generated output must not be destructively removed from `main` until the new source/build path is independently reviewable and the public reference remains available.

## Security boundary

The repository is currently public. Until the approved visibility transition is completed, do not add non-public tenant material, operational secrets, private configuration, personal data or sensitive internal runbooks.

Changing repository visibility, Pages configuration, DNS or production deployment is a separate gated operation.

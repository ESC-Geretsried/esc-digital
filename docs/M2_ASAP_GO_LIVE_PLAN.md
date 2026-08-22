# M2 ASAP Go-Live Plan

Status: BINDING ESC DELIVERY PLAN
Date: 2026-08-22
Scope: ESC reference implementation only; ORP remains the generic platform/core.

## Objective

Reach technical ESC website go-live as quickly as possible without turning the transitional `esc-int` rendered HTML snapshot into the long-term content architecture.

## Binding boundaries

- `esc-digital` navy/gold/white CI remains authoritative.
- The accepted sponsor ticker appearance and timing remain unchanged unless explicitly reopened.
- Git remains system of record for ESC website content/assets and reproducible configuration.
- ORP remains Core + Modules + Reference Implementations. ESC must not become ORP Core by convention or coupling.
- The website and editorial workflow must remain usable without AI.
- No PROD/DNS/www change without explicit approval.

## Replan decision

The work invested in `esc-int` is retained as source material for:

- information architecture,
- menu/page structure,
- module definitions,
- editorial concepts,
- sponsor logic,
- team/area organization,
- proven visual/content patterns,
- already imported and verified media/assets.

The frozen rendered HTML import from `esc-int` is transitional evidence/bootstrap only. It is not the target authoring or publishing model.

## Target content flow

`existing ESC sources -> controlled initial import -> structured ESC tenant content in Git -> ORP Editor -> deterministic website build/publish`

The ORP Editor shall edit structured tenant content; it shall not require editors to maintain HTML, YAML, JSON, Git commands, or provider-specific deployment details.

## M2 exit criteria

M2 is complete when all of the following are true:

1. The full approved ESC menu/page skeleton exists as canonical pages in `esc-digital` and builds without 404s.
2. Hero/media slots exist for all relevant team/area pages and the accepted homepage hero rotation remains functional.
3. Sponsors are canonical structured data with local tenant assets and an internal sponsors page.
4. News has a structured content model and canonical routes.
5. Initial content can be imported from approved existing ESC sources into the structured model without making the source website a runtime dependency.
6. The same structured records are suitable for initial seeding into the ESC ORP Editor.
7. GitHub Pages preview passes routing, link, mobile smoke and build validation.
8. The remaining page/news selection for launch is explicitly classified as APPROVED FOR GO-LIVE, DRAFT/REVIEW, or DEFERRED.

## Delivery sequence

### M2-A — Canonical page skeleton

Create real canonical content nodes/routes for all approved menu destinations. Pages may initially contain minimal placeholders, but each menu item must resolve inside the current site base path and later on the custom domain.

No generated HTML snapshot may be required for route existence.

### M2-B — Structured content model

Normalize the reusable content types needed for ESC:

- page,
- news article,
- team/area page,
- hero/media reference,
- sponsor,
- navigation metadata,
- publication state.

Use tenant content/configuration, not ESC-specific core code, wherever variation is content/configurable.

### M2-C — Initial content extraction/import

Use approved source material from the current ESC website and verified `esc-int` work to prefill the structured records.

Rules:

- preserve source/provenance,
- do not invent missing content,
- mark unresolved data explicitly,
- copy approved assets into the ESC repository rather than hotlinking for runtime,
- exclude obvious test/obsolete content unless explicitly approved.

### M2-D — ORP Editor seed

Prepare an initial tenant seed/import so the ESC editorial team opens the ORP Editor with the page structure and approved initial content already present.

Editorial users should primarily review, adjust, publish/unpublish, maintain news, images and sponsors rather than rebuild the site structure manually.

### M2-E — Go-live content gate

Founder/editorial review identifies exactly which pages/news go live. Non-approved material remains draft/deferred and does not block technical completion of the rest of the site.

## Go-live priority

Priority is technical go-live readiness ASAP. Avoid non-blocking work before launch, including:

- generic feature expansion not required by ESC launch,
- PWA polish,
- AI Ops,
- broad multi-provider enhancements beyond existing provider boundaries,
- editor convenience features that do not reduce launch risk or editorial workload materially.

## Post-go-live sequence

After launch:

1. final hardening,
2. editorial workflow refinement,
3. reusable ORP module extraction/generalization where justified by the ESC reference implementation,
4. AI-assisted Ops only behind the provider-neutral ORP boundary and with Git/backup-held knowledge.

## Non-goals

- making `esc-int` a runtime dependency,
- making Netlify, GitHub Pages, M365, ChatGPT or any other provider an ORP Core dependency,
- copying ESC-specific role/team names into universal ORP Core,
- requiring AI for editorial operation,
- silently changing the accepted ESC visual CI.

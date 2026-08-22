# ESC Digital M2 Gap Map

Status: IMPLEMENTATION CONTROL / 2026-08-23
Source of requirements: ORP consolidated specification `docs/decisions/esc-m2-content-editor-consolidated-spec.md` in `open-reference-platform/platform` main.

## Verified current baseline

- `esc-digital` remains the future ESC website repository; no PROD/DNS/www cutover is authorized here.
- Canonical content skeleton exists for River Rats, women, youth, Eislaufschule, figure skating, Inklusion, Verein, sponsors and home.
- Existing build validates both root/custom-domain and GitHub Pages base-path variants.
- Internal sponsors page is generated from 37 canonical sponsor records/logos.
- Transitional `esc-int` pages remain available for not-yet-canonicalized content without overwriting protected canonical top-level routes.
- Existing homepage has imported home modules and a 14-image hero/team asset pool.
- HockeyData/GamePitch integration for River Rats is merged on main after passing root build, root validation, Pages build and Pages routing validation.

## Already present — preserve and build on

1. ESC Digital navy/gold/white CI and current perceived performance.
2. GitHub Pages preview/build mechanism and base-path routing tests.
3. Canonical page skeleton for major existing areas.
4. Canonical sponsor dataset, local logo assets, native sponsor page and sponsor band foundations.
5. Imported ESC image/hero asset pool.
6. Transitional `esc-int` content snapshot for controlled migration only.
7. HockeyData River Rats provider configuration and rendered GameSlider/standings/schedule shell.
8. Start/logo Pages routing protection.

## Adapt next — M2-C critical path

1. **Photo-first Hero Gallery**
   - 0-4 heroes generically per team/area, ESC quality target >=1.
   - desktop/mobile focal point, order, active state, optional concise headline/CTA.
   - homepage curated max 6 slides; not every area hero automatically promoted.
   - preserve current fast loading; prioritize only first hero and defer others.

2. **Navigation + footer**
   - implement approved reduced hierarchy.
   - direct Förderverein footer link.
   - no public Fanshop item while draft.

3. **Canonical page migration**
   - replace transitional HTML for approved live areas with native structured content.
   - all editorial data shaped for ORP Editor instead of hardcoded templates.
   - Eislaufschule uses verified current source and supplied hero; obsolete COVID document excluded.

4. **News model + 24-month public retention**
   - one story can map to multiple areas/teams.
   - automatically exclude >24-month news from public output, homepage and sitemap.

5. **RODI external provider configuration**
   - only Damen/U20/U17/U15/U13.
   - iframe/embed only; no crawling/scraping.
   - multiple squads/competitions per age class.
   - editor-oriented 21-day human review metadata/workflow.

6. **U11/U9/U7 manual fixtures**
   - minimal game/tournament model, no table/result-history product.

7. **Tickets/prices/season cards**
   - structured editable price data.
   - clean external stadium-shop CTA.
   - native season-card page/order flow; legacy order remains until explicit retirement.

8. **People/roles + functional contacts**
   - shared contact references, public/internal separation.

9. **Documents**
   - versioned current document model; contextual links; exclude stale public docs.

10. **SEO/accessibility/performance/routing gates**
    - build into the same content path instead of post-launch cleanup.

## New capability — required before full Editor handoff

1. ORP media library and reusable hero/media references.
2. ORP people/role/scoped permission primitives.
3. Central News + Events + Venue models.
4. Price/ticketing/season-pass configuration model.
5. Versioned document register.
6. Shared privacy-minimal form/PDF engine for membership, cancellation, season ticket and Förderverein.
7. Season model and season-transition review.
8. Draft -> Preview -> Published workflow backed by Git, with granular history/restore.
9. Pre-publish validation and protected legal/price/form changes.
10. Lightweight operational health/status reporting.

These are generic ORP capabilities; ESC is the reference tenant, not justification for ESC-only ORP Core code.

## LATER / not Go-Live blocking

- full player/team/training/game-day management product (ORP issue #151)
- partner-operated Fanshop implementation
- complex search if not trivially provider-free
- sponsorship CRM
- internal resource/training calendar
- cross-device saved public form drafts/accounts
- AI/algorithmic homepage curation
- enterprise observability

## Open facts / verify before publication

- current authoritative admission prices
- current season-card prices/conditions
- current Förderverein annual contribution amount
- current team/person/contact facts at cutover
- current season-dependent RODI mappings and HockeyData phases at cutover
- final privacy/consent behavior of RODI iframe in the actual deployment
- final legal/privacy text against the actual runtime/provider set

## Go-Live blockers

- broken primary navigation/CTA routes
- failed form/PDF journeys for any process that is advertised as live
- materially degraded mobile hero/performance
- critical accessibility blockers
- unsafe/incorrect secret handling
- unverified active legal or price content
- public draft leakage
- PROD/DNS cutover without explicit founder approval

## Immediate implementation sequence

### Batch M2-C1 — public experience foundation

1. Hero Gallery data schema + photo-first renderer + homepage curation.
2. Approved main navigation/footer.
3. Canonical content schemas for areas/teams with reusable hero/contact/news references.
4. News schema with 24-month public retention filter.
5. CI gates for hero count/asset references, 24-month news leakage, navigation/404 and Pages base-path routing.

### Batch M2-C2 — sports/content integrations

1. RODI configuration/embed for Damen/U20/U17/U15/U13 and mobile fallback link.
2. U11/U9/U7 manual fixture schema/rendering.
3. Social/SpradeTV/ticket-provider links as structured configuration.
4. Structured prices/season cards.

### Batch M2-C3 — service/form foundation

1. Membership/cancellation/season-ticket/Förderverein common form schema.
2. Local validation, local email where approved, printable PDF where required.
3. Current documents/terms references and version markers.

### Batch M2-C4 — initial content migration + preview acceptance

1. Import only founder-approved/current content into canonical schemas.
2. Remove dependence on transitional esc-int HTML for live-approved routes.
3. Run mobile/desktop, accessibility, performance, routing, provider and form gates.
4. Configure `preview.esc-geretsried.de` only after the build is ready; no change to PROD/www.

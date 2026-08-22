# Sponsor content model

This directory is the canonical ESC Digital sponsor content source.

## Purpose

The same structured sponsor records must drive both the homepage sponsor ticker and the full sponsoring page. The data model is intentionally editor-friendly so a future ORP Editor can manage sponsor content without requiring Git or code knowledge.

## Fields

Each sponsor record contains:

- `id` — stable machine identifier; should not change when display text changes.
- `name` — public sponsor name.
- `url` — direct sponsor website URL, or `null` when no verified direct URL is available.
- `url_status` — provenance/verification state for the URL.
- `logo` — repository-relative logo asset path once a verified logo has been imported.
- `logo_status` — verification/import state for the logo.
- `visible` — whether the sponsor should be rendered.
- `order` — explicit presentation order, editable by Marketing.

## Link behavior

- If `url` is present, sponsor logo/name may link directly to the sponsor website.
- External sponsor links must open in a new browser tab/window and use `rel="noopener noreferrer"`.
- If `url` is `null`, the sponsor remains visible but has no external click action.
- The ticker/full component must always provide a separate `Alle Sponsoren` navigation item pointing to the ESC sponsoring page.

## Asset governance

Canonical sponsor logos belong in `content/sponsors/assets/` (or a later ORP-Editor-compatible media store committed into Git). Do not redraw, infer, scrape from unrelated sources, or substitute a logo. Import only a verified source asset.

The former `esc-int` flow may deliver sponsor data/assets, but the public ESC website must not depend on `esc-int` at runtime. After accepted import, ESC Digital Git is authoritative for the tenant content.

## Future ORP Editor

Marketing should be able to create/update sponsors, upload/change the logo, edit the direct URL, toggle visibility, and change ordering. The editor writes the structured record + asset to Git; build/publish then consumes this canonical state. This ESC implementation is a reference module and does not silently become ORP Core.

# River Rats player photo provenance

Status: verified local Git copies, 2026-08-26.

Eleven player cards in the canonical River Rats roster already carried an
unambiguous image URL from the official ESC Mannschaft page. The Git-only
completion copied exactly those eleven published JPEGs into
`content/river-rats/assets/players/` and retained each original URL as
`source_image` in `content/river-rats/team.json`.

`content/river-rats/player-photos.json` binds player name, official source URL,
repository path, public build path and SHA-256. Five roster entries without an
existing verified image reference remain deliberate no-photo states; no image
was guessed or substituted.

The build publishes only the local Git copies. The old ESC media host is
provenance evidence, not a runtime media dependency.

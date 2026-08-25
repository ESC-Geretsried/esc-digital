# ORP Editor pilot records

This directory contains structured editor records consumed by the ORP
`GitContentProvider`. It is not a second editorial source: the four River Rats
pilot records below are a narrow, draft-only projection of the canonical ESC
content at commit `156746bbd3a84d0247624786e3e4b01c0004cf03`.

Included records are exactly one Area, one overview Block, one Page and one
base Team for scope `river-rats`. Roster, staff, news, HockeyData fixtures,
results, standings, heroes, BL-010, U15, Vorstand and Rechtliches are not part
of this pilot projection. The Team uses `navigation_group=Sport` from the
current canonical navigation source.

Bound source digests (SHA-256):

- `content/river-rats/_index.md`: `a0d6f9ac81b02b0d80454154537582556072b77495749790f1dbd54337038184`
- `content/river-rats/team.json`: `8fe4e218fdbcfbda1a9efdefb3befcf25a78f25120ec2949c0b769592c220772`
- `content/river-rats/hockeydata.json`: `4e6240ec91ead4414dacf9728b0edce03a3fdac87114c0ab0a79ba0bedbe05c4`
- `content/navigation.json`: `11bfb6cff1090749155a15d1b8f4edd934a5c08d8d7b72ba2225fbd23a17565e`

The existing canonical source files remain unchanged. Any later refresh of
these records requires a new source-digest check and reviewed mapping diff.

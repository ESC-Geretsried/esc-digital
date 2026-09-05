# ESC demo: WordPress to static build

The demo branch `codex/wp-to-static-int-proof` builds the public ESC artifact
from the ESC repository. It reads published WordPress posts during the build,
excludes Flash-News, downloads featured images into the generated artifact and
publishes the resulting article pages under `/aktuelles/`.

The scheduled workflow checks the local time in `Europe/Berlin` and runs at:

`06:00`, `12:00`, `16:00`, `19:00`, `21:30`, `22:00`, `22:45`

The workflow is intentionally scheduled every 15 minutes because GitHub cron
uses UTC and daylight-saving changes must not shift the requested local times.
Only the seven listed local times perform a build.

## Demo configuration

Add these GitHub Actions secrets to `ESC-Geretsried/esc-digital` before the
first Netlify publish:

- `NETLIFY_AUTH_TOKEN` — deploy token for the existing demo site
- `NETLIFY_SITE_ID` — site ID for `orp-esc-int.netlify.app`
- `HOCKEYDATA_API_KEY` — optional for the current client widget; it is not
  stored in Git

The WordPress API defaults to:

`https://2026.esc-geretsried.de/wp-json/wp/v2`

The proof uses public published content only; no WordPress write access is
needed. A repository variable named `WP_API_BASE` can override the API base if
the WordPress domain changes.

## Current proof boundary

The WordPress adapter is implemented and tested against the public ESC API.
The existing ESC build still contains the current checked-in SharePoint
projection and client-side HockeyData widget. A separate build-time adapter is
required before those two sources can be advertised as fully automatic in the
static demo. No such credentials or API contract is invented here.

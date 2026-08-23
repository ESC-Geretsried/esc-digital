# ESC Preview Runtime

Status: BINDING for ESC GoLive preview

- Canonical preview host: `https://preview.esc-geretsried.de/`
- Hosting: Plesk
- Plesk document root: `/preview`
- Plesk system user: `svc-orp-deploy`
- TLS: Let's Encrypt for `preview.esc-geretsried.de`
- HTTP -> HTTPS redirect: enabled
- Source repository: `ESC-Geretsried/esc-digital`
- Plesk repository access: dedicated read-only GitHub deploy key
- Plesk does not provide Hugo; Plesk MUST NOT build the site.
- GitHub Actions builds and validates the static site.
- Validated static output is published to branch `preview-dist`.
- Plesk deploys only `preview-dist` to `/preview`.
- GitHub Pages is not the canonical ESC preview environment.
- Production remains `https://www.esc-geretsried.de/`; no production cutover without explicit approval.

## Safety

Never deploy the source branch (`main`) directly into `/preview`. The public webroot must contain only the validated static artifact.

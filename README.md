# FFC-EX-thelastchancesanctuary.com

The Last Chance Sanctuary — Brevard County, Florida no-kill cat shelter. FFC-supported static site (GitHub Pages).

Static, fully localized single-page capture of the former WordPress site (`thelastchancesanctuary.com`), migrated as part of the FFC Wave-1 WordPress-to-Pages program ([FFC-Cloudflare-Automation#702](https://github.com/FreeForCharity/FFC-Cloudflare-Automation/issues/702)).

## Hosting
- GitHub Pages, default URL: <https://freeforcharity.github.io/FFC-EX-thelastchancesanctuary.com/>
- Deploys from `.github/workflows/static.yml` on push to `main`. No custom domain / DNS at this stage.

## Migration notes
- The live site was a near-dormant WordPress (Twenty Seventeen theme). Only the landing page (`/`) was functional and rendered real content (shelter description; latest post from 2013). The secondary WordPress install under `/blog/` returned HTTP 500 and the `/about/` page held only unedited default WordPress placeholder text, so both were dropped (dormant-content precedent).
- The landing page's Twenty Seventeen theme assets (CSS/JS/fonts/images) are referenced from the apex host and were localized into this repo; zero external asset hosts remain.
- Broken navigation links to the defunct `/blog/` install (HTTP 500) were neutralized.
- Cloudflare Insights beacon and WordPress oEmbed/feed/XML-RPC artifacts were stripped.

## CI
- `static.yml` — deploys to Pages on push to `main`.
- `check-assets.yml` — fails if any asset loads from an external host.
- `linkcheck.yml` — lychee link check.

---
Supported by [Free For Charity](https://freeforcharity.org).

# Northstar Calculators V2

A static calculator site focused on US search intent and tested browser tools.

## Included
- Calculator pages with a curated indexable subset; unfinished tools remain withheld
- Topic category hubs
- Homepage search
- 4 trust/policy pages
- 404 page
- Purpose-built JavaScript engines and explicit availability controls
- Calculator titles, descriptions, formulas, worked examples and assumptions
- Related-calculator internal links
- JSON-LD WebPage schema
- Canonical tags
- sitemap.xml
- robots.txt
- Responsive CSS
- Keyword provenance and US research mappings with unknown metrics kept explicit
- GitHub Pages / Cloudflare Pages-ready `dist/`

## Deploy
The GitHub Pages workflow builds from source, optimizes the shared calculator
script, refreshes every affected content hash, and runs the calculation and
indexation checks before deployment. The optimizer is a build-time dependency;
no CDN, browser plugin or additional runtime request is introduced.

For an equivalent local production build:

```powershell
Push-Location tools/asset-optimizer
npm ci --ignore-scripts --no-fund --no-audit
Pop-Location
python build.py
node tools/asset-optimizer/test.cjs
node tools/asset-optimizer/optimize.cjs dist
python scripts/check_calculator_assets.py dist
```

`python build.py` alone remains a working unoptimized build. Keep the readable
calculator source in `build.py`; do not edit generated JavaScript. The optimizer
preserves global identifiers and property names and disables expression
compression. Its pinned dependency is isolated from other local Node tools.
Upload the final contents of `dist/` to your static host. The normal workflow
generates those files in CI; do not commit a local generated build for deployment.

The production workflow sets `PUBLIC_SITE_DOMAIN=https://nscalculators.com`
and an empty `PUBLIC_BASE_PATH`. For another host or project subdirectory,
set those environment variables before building; do not replace URLs across
generated files manually. Keep canonicals, sitemap URLs and asset paths aligned.

## SEO / quality rule
Do not add pages merely to increase URL count. Every new calculator should have:
1. A distinct search intent
2. A real formula or real lookup data
3. Useful inputs
4. Formula and assumptions
5. A worked example
6. Appropriate related links
7. Verification against authoritative sources where the topic is safety-, finance-, construction-, fitment- or code-sensitive

## Important
Google Ads competition in the JSON is an advertising signal, not organic keyword difficulty.

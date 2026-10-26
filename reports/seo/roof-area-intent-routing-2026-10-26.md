# Roof Square-Footage Intent Routing

Date: October 26, 2026. Existing URLs: `/square-footage-calculator/` and `/roof-pitch-calculator/`.

## Evidence and Scope

The archived US Trends related Rising queries include roof square footage calculator (+50%) and roofing square footage calculator (+40%). These are relative-interest signals, not monthly volumes, difficulty or a verified site query/page pair. The promised US historical Keyword Planner file is not yet available. This release improves existing task routing rather than adding a competing URL or asserting a traffic forecast.

Public production browser checks reproduced the supported positive geometry: 1,200 sq ft of horizontal projection at 6:12 gives a factor of sqrt(1.25), 1,341.6407864998738 sq ft of sloped surface and 13.416407864998739 roofing squares. The existing output table rounds area to one decimal (1,341.6 ft²); explanatory copy uses two decimals (1,341.64 sq ft). Rise/run and angle modes reproduce the same result. Increasing the rafter-overhang field changes linear rafter length but leaves entered plan area and sloped area unchanged.

## Changes

Added an original worked example and three contextual internal links: Square Footage to Roof Pitch, Roof Pitch to Square Footage and Roof Pitch to Area. Preserved the original irregular-room guide. Explanations distinguish roof horizontal projection from multiple interior floor areas, include applicable eaves in the measured projection, avoid doubling a complete gable projection and describe separate calculations for differing pitches. Complex intersecting projections require an appropriate takeoff.

Roofing squares are an area measure, not a bundle count. The [GAF shingle information](https://www.gaf.com/en-us/roofing-materials/residential-roofing-materials/shingles) supports the 100-square-foot definition and product-dependent shingle quantities. No universal bundles-per-square, materials order, cutting allowance, installed cost or structural suitability is inferred. Copy advises suitable plans/reliable measurements rather than climbing a roof.

No calculator engine, inputs, chart, CSS, theme, plugins, titles, meta descriptions, canonical, indexation policy or sitemap scope changed. This is not a full roof-input validation audit: existing input coercion and chart presentation remain separate follow-up concerns, and the positive examples do not certify invalid-input behavior or full quantity ordering.

## Verification

- 111 Python tests pass, including two new content/link/index-scope checks. All JavaScript suites pass, including 10 new positive roof geometry/mode scenario groups added to CI.
- Isolated full build validates 140,748 internal links. Indexation/schema gates pass: 285 calculator entries, 303 sitemap URLs, maximum crawl depth 3, 286 application objects, 297 breadcrumb trails and 1,165 breadcrumb targets.
- Bundle checks remain `f761017e92bcf8d7` for 4,903 calculator references and `066d4625bf637de9` for 5,027 stylesheet references.
- Local Playwright at 1366, 390 and 320 px verifies first-screen Square Footage Calculate controls, reciprocal navigation, the worked output across all three positive input modes, overhang scope, canonical/indexability, no page overflow and no JavaScript errors. Mobile screenshot inspected. Harness: ignored `doc-work/verify-roof-area-intent.cjs`; supports `--live` after deployment.

No Search Console submission, account change, spend or outreach. No ranking gain, field Core Web Vitals gain or measurable traffic effect is claimed; use settled US measurement windows before interpreting impact.

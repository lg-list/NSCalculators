# Concrete bag lookup and calculator examples

## Evidence and choice

The existing concrete volume URL already explained 45 approximate 80 lb bags per cubic yard and supported US/metric dimensions, round shapes, custom product yields, allowance and optional costs. A separate near-duplicate bag calculator would not add a new task. This change improves that existing page with server-rendered reference data and usable examples.

The archived public US Google Trends observation in `exports/us-construction-trends-2026-10-26.json` reports rising related terms `80lb bag of concrete` (+190%) and `80lb concrete bag` (+60%). These are relative changes, not monthly search volumes. The 80 lb coverage question is an editorial task inference from that bag/yield intent; it was not independently measured as an exact keyword. No fresh Search Console results or US Keyword Planner CSV were available for this release, and no traffic lift is claimed.

## Same-page implementation

- An HTML table compares approximate finished yields for 40/50/60/80/90 lb bags and whole bags for one cubic yard with zero or an illustrative 10% volume allowance.
- A second table converts the selected 80 lb / 0.60 cubic-foot yield to coverage at 2, 3, 4 and 6 inches: 3.6, 2.4, 1.8 and 1.2 square feet. These are arithmetic examples, not structural thickness recommendations.
- Each of nine rows loads its matching calculation. The nearby notice explains that this replaces inputs, selects US/slab measurements, resets allowance to zero and clears optional prices. Blank prices remain unknown rather than zero. Loading from metric/round mode does not reinterpret dimensions.
- A contextual square-footage link explains why depth and actual product yield are needed to obtain concrete bag quantity. It links to the coverage section, without creating a new URL to index.
- The static table, select presets and browser calculator share one yield definition. Decimal arithmetic rounds the static whole-bag counts; runtime tests check identical numerical outcomes.

## Source and arithmetic

Rechecked October 27: [QUIKRETE Concrete Mix No. 1101 data sheet](https://www.quikrete.com/pdfs/data_sheet-concrete%20mix%201101.pdf), revised October 2022, page 1. Listed yields are approximate and product-specific: 0.30 / 0.375 / 0.45 / 0.60 / 0.675 cubic feet respectively. Other mixes may differ; this is not a universal weight-to-volume conversion or a brand recommendation. The existing source link remains on the page.

One cubic yard is 27 cubic feet. `ceil(27/yield)` gives 90 / 72 / 60 / 45 / 40 bags. `ceil(27*1.10/yield)` gives 99 / 80 / 66 / 50 / 44 bags. Each one-yard button loads a 9 by 9 foot rectangle at 4 inches, with zero allowance. Coverage examples use a 1-foot width and length equal to `0.60*12/depth`, giving one labeled bag before allowance. Final bag counts round up once, after allowance.

## Verification

Reproduce with the isolated build and optimizer, `scripts/test_concrete.cjs`, the Python suite, all final-bundle JavaScript regressions, indexation/schema/asset contracts, then `node scripts/verify_concrete_reference_browser.cjs` (or `--live`). Browser checks block analytics and cover all nine examples at 1366, 390 and 320px, switching from metric/round inputs, unknown prices, invalid/Clear recovery, initial first-screen Calculate, internal routing and page overflow. Screenshots and machine-readable checks are saved under ignored `doc-work/`.

Local verification passed: 123 Python tests, 190 concrete scenarios and all existing JavaScript suites against the optimized bundle. Indexation remains 305 sitemap URLs / 287 indexable calculators with maximum crawl depth 3; 140,801 internal links resolve. The optimized shared calculator asset is 493,868 bytes (`e8b3bcbbad59637c`); CSS is `3c03ec86cfa61cff`. All 4,905 calculator-script and 5,027 stylesheet references pass the asset contracts. This small bundle increase is not evidence of a Core Web Vitals improvement.

No new pages, external submissions, outreach, paid services or account changes are part of this release. The 90-day traffic objective remains active and unproven.

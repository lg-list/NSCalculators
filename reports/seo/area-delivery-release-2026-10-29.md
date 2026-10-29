# Area Calculator delivery — October 29, 2026

Previous goal turn made progress: 401(k) delivery commit 03978c1ae3 deployed successfully in Pages run 40893409592; production mode tests, specialized response byte hash and a full-runtime control page passed. This turn applies the guarded approach to the existing Area page.

## Priority and changes

The latest completed US exact-query/page evidence records `area calculator` with 587 impressions, zero clicks and position 8.19 (September 28–October 25). This is observed site demand, not US monthly market volume. Its October 24–25 title/content treatment remains in observation until at least November 8. No title, H1, description, text, canonical or new landing page is introduced here.

The optimizer now uses an explicit two-route `engine-assets.json` registry shared with the Python asset checker. It checks the actual page's engine before specialization and requires exactly one runtime reference. All transformations and reference validation finish before writing outputs. Only Area and 401(k) receive their registered assets; other calculators keep the full runtime. Wrong routes, stale hashes and duplicated runtimes fail validation.

Area delivery: `calculator-area.js?v=4853cc0c36c5ce56`, 319,333 decoded bytes versus 500,087 full bytes (about 36% less). Python gzip level 9 measures 93,533 bytes; this local compression result is not a promise of a particular production encoding. 401(k) remains 315,146 bytes at unchanged hash `077a3aa5d1aeaa06`. Full bundle and CSS hashes remain unchanged. No asynchronously loaded functionality or loading UI is introduced.

## Validation

- 136 Python tests, including Area-specific required-runtime, hash and wrong-page rejection.
- Delivered Area asset: 64 geometric-boundary/stability checks; 9 output units, 7 section scenarios, 15 invalid totals, 3 reconciliations, 9 shapes and 10 invalid projections; 37 saved-snapshot/CSV/validation/download scenarios. These delivered-file checks are added to Pages CI.
- Promoted three existing browser suites into tracked scripts. At 1366, 390 and 320px, these cover every shape selector, full/partial circle perimeter, thin/invalid triangles, additions/deductions, mixed units, zero/invalid totals, section removal, original-measurement snapshots, actual CSV downloads, Clear, Enter and overflow. Each suite asserts no runtime errors; the sections suite verifies the selected asset fingerprint.
- The deployed 401(k) local browser regression is repeated to check registry generalization. Indexation/schema/full-bundle/CSS checks pass: 305 sitemap URLs and maximum depth 3.

No field CWV or LCP/INP gain is asserted. The supported benefit is a smaller script for the Area page; the prior paired 401(k) test showed transfer savings but no stable LCP/long-task improvement. Search impact requires a later completed window. After the exact Pages workflow succeeds, run all three Area suites on production and verify the asset version; preserve the title observation period. No spending, account changes, submissions or outreach.

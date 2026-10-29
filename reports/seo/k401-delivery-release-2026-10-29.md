# 401(k) specialized delivery release — October 29

Previous turn progressed an isolated prototype at e492dea19f, verified by successful Pages run 40892138082 and the production 401(k) browser suite. This release adds a guarded build selection for that one page, not the whole site.

## Delivered change

The optimizer specializes the unminified renderer's strict literal engine comparisons before conservative minification. Unminified input avoids confusing minifier-generated shadowed names with the outer parameter. Unknown conditions and nested functions are preserved; helper functions, event listeners and the main dispatcher remain. An AST preflight rejects parameter binding or mutation patterns. Unsupported source fails the build before asset writes, preserving the previously published site.

Only `/401k-calculator/` uses `calculator-401k.js`, fingerprint `077a3aa5d1aeaa06`. All other calculators retain the full `calculator.js` (`718d9bfce62c3877`). The new version checker rejects a stale specialized hash, a second runtime on that page, or a specialized runtime on any other page. The normal build still creates the original full asset. No runtime asynchronous fetch or loading state is introduced.

## Measurement

Raw paired local experiment: `exports/k401-delivery-comparison-2026-10-29.json`. Three fresh contexts per variant, alternating order by round, 390×844 mobile emulation, 4× CPU slowdown, 150ms latency, 1.6Mbps download and gzip responses from the same localhost server. Nonlocal requests are blocked. Initial projection and withdrawal-tab results are asserted in each run. This is a controlled lab transfer test, not a US regional test or field CWV measurement.

| Metric | Full control | Specialized |
|---|---:|---:|
| Decoded script bytes | 500087 | 315146 |
| Local gzip bytes | 141082 | 92602 |
| Script download duration median, ms | 944 | 691.9 |
| Observed LCP median, ms | 716 | 712 |
| Longest loading task median, ms | 188 | 190 |

The script is about 37% smaller decoded and 34% smaller in this gzip test. Download time decreased under the controlled throttle. LCP and long-task samples **do not demonstrate an improvement**; do not describe this as a field CWV pass or a faster result for every user. Encoding, edge latency and cache behavior differ in production. CSS is unchanged.

## Release verification

- 135 Python tests including specialized hash, route-scope and duplicate-runtime rejection.
- Optimizer preservation checks and transform fixtures including wrong engine, nested shadowing and parameter mutation rejection.
- 323 projection/withdrawal/validation scenarios plus 16 numerical and 10 invalid employer-match cases against the **delivered specialized file**; these same checks run in Pages CI.
- Local browser suite against the page-selected specialized asset at desktop, 390px and 320px: all three modes, default results, signed losses, invalid/blank fields, tax/age boundaries, shortfalls, zero, Clear and Enter. No runtime errors or horizontal overflow.
- Full indexation/schema/script/CSS checks pass; sitemap stays at 305 URLs, maximum click depth 3. Existing calculation, content, metadata and canonical behavior are preserved.

After the exact Pages workflow completes, rerun the same suite against production and verify the new asset URL and hash. Do not expand to other engines without their complete affected-mode tests and dependency guards. Search traffic effects require later completed Search Console windows. No paid activity, account modification, outreach or external submission.

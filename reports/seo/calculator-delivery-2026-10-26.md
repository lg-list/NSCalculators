# Shared Calculator Delivery Optimization

Date: October 26, 2026.

## Observed opportunity

Public Playwright at 390px found Area and Mortgage loading the shared `calculator.js` at 539,173 decoded bytes, with 142,014 transfer bytes in the sampled production browser responses. Homepage does not load this bundle: it has separate small search/scientific/home scripts, and its search index is not fetched before search interaction in this sample. Do not report the shared-calculator reduction as a homepage payload gain or infer field CWV from one lab visit.

## Implementation

Added build-time Terser 5.51.2 in an isolated `tools/asset-optimizer/` package and integrity-locked dependency tree. CI uses Node 20 and `npm ci --ignore-scripts --no-fund --no-audit`, then runs optimization after the existing Python build. Existing local `python build.py` remains a valid unoptimized build; the README documents the production-equivalent sequence. No runtime dependency, CDN, plugin change or additional browser request.

The [Terser API](https://terser.org/docs/api-reference/) provides separate compression and name-mangling options. Here expression compression is explicitly **false**; local variable shortening and compact printing provide most of the measured benefit. Top-level names and function names are retained, property mangling is disabled and this remains a classic script rather than an ES module. Formula source in `build.py` and embedded RMD data are unchanged. Source maps are not deployed.

The postprocessor computes a hash from actual optimized UTF-8 bytes and updates every generated calculator script URL, including project-subdirectory paths. Before writing, it rejects stale, duplicate, absent or unexpected version parameters/references. Existing whole-site asset verification then validates the final deployed bytes. Dependency failures or invariant/test failures stop CI before deployment rather than silently publishing another bundle. The generated output in tracked `dist/` is not edited or committed locally.

## Measured local output

| Measure | Original | Optimized |
| --- | ---: | ---: |
| Decoded bytes | 539,173 | 457,899 |
| Controlled gzip bytes, level 9 | 141,400 | 129,495 |
| Content hash | c3961a2e338de2b1 | 7dc4d81ff2016582 |

Decoded reduction: 81,274 bytes / 15.07%. Controlled gzip reduction: 11,905 bytes / 8.42%. Gzip sizes are same-tool local measurements, not claimed CDN response sizes or download-time savings. The browser/connection/CDN cache and compression affect actual timings.

## Validation

- New optimizer fixture tests check preserved globals/function names/property keys and numeric results, byte-derived hashes, nested/base paths, unrelated script preservation and fail-before-write stale/missing references.
- Reworked the existing keyboard test to execute the shipped bundle and verify the actual registered handler; it previously extracted a function by original whitespace and parameter spelling. All 34 behavior cases remain. This tests optimized and readable output without weakening keyboard requirements.
- All 111 Python tests and all JavaScript suites pass against the optimized deployment asset where applicable. Existing calculator-version, indexation, schema and stylesheet gates pass: 4,903 updated calculator references, unchanged 303 sitemap URLs / 285 indexable calculators, 286 applications, 297 breadcrumb trails, 1,165 breadcrumb targets and CSS `5679b9838daa7466`.
- Differential browser checks on 14 pages compare identical default, Calculate and Clear result/summary/table snapshots using readable versus optimized script: Area, Mortgage, Loan, Compound Interest, Fuel Cost, New vs Used Car, Personal Loan, Boat Loan, Ratio, Time Duration, Concrete, Flooring, Roof Pitch and RMD. No browser exceptions. Ignored harness: `doc-work/verify-optimized-delivery.cjs` with `--live` to verify actual response bytes/hash after deployment.
- Roof and Flooring functional browser harnesses pass at 1366, 390 and 320px with optimized JavaScript, including validation, Clear/Enter, optional fields, chart pixels and extreme-value wrapping. These are representative functional checks, not certification of every legacy calculator formula.

No canonical, URL, indexation, title/snippet, keyword mapping, theme, font or account changes. No external submissions, outreach or spend. There is no measured traffic gain or field LCP/INP/CLS claim. The shared bundle remains relatively large; engine-specific splitting is a separate opportunity requiring dependency and broader interaction checks, not represented as finished here.

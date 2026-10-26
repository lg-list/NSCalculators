# Roof Pitch Validation and Consistent Chart Units

Date: October 26, 2026. Existing route: `/roof-pitch-calculator/`.

## Why this work

The previous release connected existing Square Footage and Roof Pitch pages for archived US related roof-area intent. It explicitly left full input validation and chart correctness unaudited. Those relative Trends signals are not monthly volumes or a verified GSC query/page pair; no new keyword demand or traffic gain is claimed here.

Current production Playwright reproduction found three concrete errors:

- Pitch -6 was silently changed to 0:12 and shown as a valid 13 ft rafter result.
- Rise/run with zero run produced 720,000:12 and a 780,000 ft rafter rather than rejecting the input.
- Angle 90° was silently changed to 89.9° and shown as a valid 7,448.46 ft rafter estimate.

The old chart mixed three lengths in feet with a count of 100-square-foot roofing squares. Empty optional plan area became zero area and zero roofing squares. Clear left stale analysis visible.

## Changes and boundaries

Added pure `roofPitchAmounts` with explicit finite active-mode validation. Pitch/rise are nonnegative, measured run and horizontal rafter run are positive, angle is 0° inclusive through 90° exclusive, and overhang is nonnegative. No silent clamping or replacement of zero denominators. Unsupported numerical overflow/underflow or precision returns a correction message rather than an apparently valid finite or zero answer. `Math.hypot(1, slope)` avoids squaring overflow. These are numerical and geometric limits, not a code-approved roof pitch range.

Inactive measurement fields hide and disable and are excluded from the selected mode. Blank optional overhang means none; blank plan area means unknown/not entered, while an entered area must be positive. Pitch and rafter calculations remain available without roof area. Overhang still affects linear rafter length only; it does not enlarge entered plan area. Zero slope remains valid geometry without implying that a roofing product can be installed on it.

Invalid input and Clear clear prior cards/table/chart and show a correction. Valid edits restore results without reload. The chart compares horizontal run, rise and rafter length in feet only. Angle, slope, multiplier, area and roofing squares remain labeled in the table/cards. Very small/large supported values use scientific notation; angles just below 90° are not rounded to a misleading 90°. Scoped result-card wrapping addresses an observed 320px overflow without changing the theme, fonts, plugins, input layout or other pages' summary layout.

The formulas use tangent/arctangent and the right-triangle relation, consistent with [OpenStax inverse trigonometric functions](https://openstax.org/books/precalculus-2e/pages/6-3-inverse-trigonometric-functions). US rise-per-12 terminology is also used in [GAF's garage-roof discussion](https://www.gaf.com/en-us/blog/your-home/selecting-roofing-materials-for-your-garage-roof-6940d24c-a5a2-4eba-b42b-33e70a7d74df). This source review supports geometry/terminology, not a material suitability determination. The existing copy distinguishes common slope usage from rise/span pitch conventions.

No structural sizing, code check, cutting/bearing adjustments, hip/valley rafter solution, complex-roof takeoff or material order is added. Other construction calculators are not certified by this fix. No new URL, title/snippet, canonical, indexation scope, outreach, account change or submission.

## Verification

`scripts/test_roof_pitch.cjs` adds 88 groups covering independent 6:12 expectations, equivalent modes, flat/steep/tiny/large finite geometry, inactive invalid fields, invalid types/signs/denominators/90° angles, numerical limits, optional data, result rendering and length-only bars. The existing ten positive roof-area routing groups continue to pass. The new suite runs in GitHub Pages CI.

The ignored `doc-work/verify-roof-pitch.cjs` checks actual browser behavior at 1366, 390 and 320 px: Calculate in the first 844px viewport, negative/zero/90° correction, inactive disabled controls, optional unknown area, zero-pitch geometry, Clear recovery, Enter submission, chart pixels, extreme-value overflow and canonical/indexability. It supports `--live` after the exact deployment job succeeds. No measured search lift or field Core Web Vitals result is claimed.

All 111 Python tests and all JavaScript suites pass. Both the new functional browser harness and the prior reciprocal-routing harness pass locally at all three widths with no page errors. Reviewed mobile default, chart and near-vertical screenshots. The isolated build validates 140,748 internal links; indexation/schema gates retain 285 indexable calculators, 303 sitemap URLs, maximum depth 3, 286 application objects, 297 breadcrumb trails and 1,165 breadcrumb targets. Asset gates verify 4,903 calculator references against `e97f662039ee3a31` and 5,027 stylesheet references against `6c12feb86122c6b4`. Tracked `dist/` is not modified; CI generates the deployment from source.

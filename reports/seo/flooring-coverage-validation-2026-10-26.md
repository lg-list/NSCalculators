# Flooring Coverage, Package Rounding and Optional Costs

Date: October 26, 2026. Existing route: `/flooring-calculator/`.

## Priority and reproduced problems

The archived US construction research already identifies square-footage, vinyl, cost and laminate terms associated with flooring. Its quoted comparison average of 1 and separate related Top indexes are normalized interest, not monthly volume, growth rates or an estimate of traffic available to this site. US Keyword Planner data is still pending. This release audits an existing workflow and does not justify new material-specific URLs.

Public production Playwright reproduced zero box coverage being silently replaced by 0.001 sq ft and producing 264,000 boxes for the default project. A blank box price became $0, yielding an apparently complete $105 total based only on underlayment. Clear left the previous table visible. The chart also put dollar costs and square-foot coverage on one scale. Existing defaults otherwise reconcile: 20 x 12 = 240 sq ft, 10% flooring allowance = 264 sq ft, 11 boxes at 24 sq ft/$48 = $528, plus 3 rolls at 100 sq ft/$35 = $105, total $633.

## Implementation

- Pure `flooringAmounts` validates finite positive active dimensions/total area and package coverage, nonnegative extra area and entered prices, and independent 0%-100% flooring and roll allowances. It rejects unsupported numerical ranges and package counts outside 1-1 billion per included material rather than clamping to an apparently valid answer.
- Existing dimensions plus optional extra area remain. New Total square feet mode accepts a measured sum for multiple non-overlapping rooms without also counting one room's dimensions. Inactive measurement inputs hide, disable and are excluded; this is an input pathway, not a map or automatic room measurement.
- Whole boxes are rounded up after area and allowance are calculated, with a four-machine-epsilon near-integer correction for arithmetic noise. Tiny supported projects still need one box; a real excess in the boundary test still needs another. No intermediate area rounding feeds procurement counts.
- Separate underlayment is explicitly included/excluded in More Options. Its measured-area target plus its own allowance is independent of flooring waste and flooring box coverage. Disabled roll inputs cannot poison a flooring-only result. Defaults preserve the original $633 example; disabling rolls gives $528.
- Blank prices are unknown, explicit zero prices remain zero and a total requires all included prices. Separate line costs remain available when the complete total is unknown. No price fetching, current retail claims or full installation quote.
- The chart compares measured area, flooring allowance and box-rounding excess, all ft². Table distinguishes planned allowance, rounding remainder and total coverage beyond measured area; the latter is not guaranteed reusable spare material. Invalid edits/Clear replace stale analysis and hide the chart. Valid edits recover without reload.
- Original 250 sq ft example: 10% allowance gives 275, twelve 24 sq ft boxes give 288, comprising 25 allowance plus 13 rounding excess, or 38 beyond measured area. Added contextual Area/Square Footage links, corrected the multi-room instructions and clarified vinyl/laminate dependence on actual carton/layout instructions. No clone pages, title/snippet, canonical or indexation changes.
- One scoped summary-card wrapping rule addresses observed extreme-value content overflow at 320px. Theme, plugins, fonts and other pages' layouts are preserved.

The [Lowe's project planner](https://www.lowes.com/pdf/project-planner.pdf), reviewed October 26, describes carton-specific coverage and separately calculating underlayment packages from required area. It is an existing document, not a newly issued 2026 specification or affiliation. Our editable allowances do not certify attached-pad compatibility, moisture barriers, overlap, subfloor preparation, product warranties or installation. No universal vinyl/laminate waste percentage is asserted.

## Verification

- 111 Python tests and all JavaScript suites pass. New `scripts/test_flooring.cjs` has 156 groups including independent expected quantities/costs, 64 mode/allowance/coverage/inclusion combinations, optional prices, numerical boundaries, invalid inputs, active-field behavior, cleanup rendering and square-foot-only bars. It is added to Pages CI.
- Isolated build validates 140,750 internal links; indexation and schema gates retain 285 indexable calculators and 303 sitemap URLs, maximum depth 3, 286 application objects, 297 breadcrumb trails and 1,165 breadcrumb targets.
- Asset checks verify 4,903 calculator references against `c3961a2e338de2b1` and 5,027 stylesheet references against `5679b9838daa7466`. Tracked `dist/` is unchanged; CI builds from source.
- Local Playwright at 1366, 390 and 320px passes first-screen Calculate at 844px height, negative/zero inputs, direct area, blank versus zero price, roll inclusion/hidden controls, separate allowance, Clear recovery, Enter, chart pixels, canonical/indexability and page/card overflow. Default, open-options, chart and extreme-value screenshots were checked. Ignored harness `doc-work/verify-flooring.cjs` supports `--live` for deployment verification.

No external submission, account change, spend or outreach. No ranking gain, field CWV improvement or measurable traffic lift is claimed. Retain the US measurement queue and validate market demand before material-specific expansion.

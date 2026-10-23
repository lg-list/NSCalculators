# Fuel Cost Reliability and Discovery Review

Date: 2026-10-23

## Evidence and Priority

The existing US Search Console baseline (September 19 through October 16, not current demand) recorded 14 impressions for `fuel cost calculator` at average position 8.5. This supports reviewing the existing trip-fuel route rather than publishing another competing URL. No fresh US export is available, and those impressions are not a market search-volume estimate or a measured result of this release.

A static-link crawl of the current isolated build found all 302 sitemap URLs reachable from Home using links between sitemap pages: 1 at depth 0, 26 at depth 1, 273 at depth 2 and 2 at depth 3. No navigation rewrite or orphan-page fix was warranted. This is generated-artifact evidence, not a new Google indexing verdict.

Live Playwright inspection found the fuel calculator silently treating 1.5 trips as 2, 1.5 paying people as 2, and negative detour distance as 0. It also accepted a 201% buffer despite the input's 200% maximum. A blank pump price was treated as free fuel. The generic pie included both budget components and per-person cost, which double-counted costs, and its default dollar formatting did not follow non-USD currency choices.

## Changes

- Added a pure, validated fuel-cost model plus a DOM adapter. Counts must be positive safe integers; costs/detours must be finite and nonnegative; buffer must be 0-200%. Unit and currency choices are checked. Required blanks are invalid; optional blank detour/buffer/shared-cost amounts are zero. An explicit zero fuel price remains valid.
- No rounding or clamping of invalid counts/costs. Overflow, unusably small derived quantities and nonfinite results return a correction message instead of a plausible zero budget.
- Derived fuel-economy conversions from mile/kilometer and US/Imperial gallon definitions instead of separate rounded MPG constants. Every price applies to its matching volume. Currency formats the entered monetary unit; there is no exchange-rate conversion or live price feed.
- Replaced the generic trip pie with a clearly labeled cost-comparison bar chart, using the existing responsive renderer and selected currency. Per-person cost remains a comparison, not a component added into a pie total. Invalid inputs hide the chart; valid re-entry restores it.
- Clear restores one trip, one payer, and zero optional costs, removes stale results and permits calculation after the three core numeric values are re-entered.
- Moved repeat-trip count into the existing More trip budget options section and paired the eight main fields. The initial desktop Calculate button previously ended at y=892.7 in an 844px-high viewport. The compact version is checked inside the initial 844px viewport at all three tested widths without shrinking input fonts or changing the theme/CSS.
- Added an original repeated-round-trip example: 650 x 2 x 2 + 40 = 2,640 miles; at 28 US MPG and $3.60/US gal, fuel is $339.43, budget with 10% buffer is $373.37, and four paying travelers split $93.34 each. Detour is added once and calculations use unrounded values.

## Sources and Verification

Unit definitions were checked against the [NIST conversion tables](https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b8), including the distinct US and Imperial gallons, and the [NIST Handbook 44 tables](https://www.nist.gov/document/appc-11-hb44-finalpdf), which give 231 cubic inches per US gallon. The existing article retains its FuelEconomy.gov and Department of Energy references. The [Calculator.net fuel calculator](https://www.calculator.net/fuel-cost-calculator.html) was inspected as a scope reference; this report does not claim exhaustive reference-site feature parity.

- 56 Python tests, including four fuel-route/layout/content checks.
- 172 new JavaScript checks: 7 trip scenarios, 96 independent unit/currency combinations, 60 invalid scenarios and 9 DOM input cases. All 281 earlier JavaScript checks still pass (453 total).
- Full isolated build retains 5,005 calculator routes, 284 indexable calculators, 302 sitemap URLs and 140,684 validated internal links.
- Browser verification covers default/round/repeated trips, one-time detours, invalid and corrected values, GBP chart values, explicit zero price, Clear/re-entry, chart pixels, first-screen controls and no overflow/errors at 1366, 390 and 320px with 2x pixel ratio. Both old fuel-cost aliases still reach the canonical trip route via the existing static redirect pattern, not a claimed HTTP 301.

Title, description, canonical, sitemap scope, existing aliases, shared CSS, and indexing policy remain unchanged. No external submission, spending, account change, or traffic-growth claim was made. Evaluate later settled US results before further snippet changes.

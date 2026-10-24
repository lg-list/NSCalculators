# Used-Car Condition and Search Intent

Observed and implemented: 2026-10-24.

## Verified Query-to-Page Evidence

Used the existing signed-in Search Console browser, NS domain property, US country filter, daily Web report, September 24-October 21. Applied **exact query** filters and read the **Pages** breakdown, rather than joining unrelated query/page exports. Sanitized observations and report URLs are in `exports/us-query-page-observations-2026-10-24.json`.

| Exact query | Query aggregate | Observed page rows |
| --- | --- | --- |
| car price estimate | 0 clicks, 25 impressions; UI position 11.7 | Used Car Value: 0 clicks, 25 impressions |
| vehicle price estimator that includes values for poor condition cars | 0 clicks, 11 impressions; UI position 20.1 | Car Resale Value: 0 clicks, 9 impressions; Used Car Value: 0 clicks, 6 impressions |

Page-level exposure is not deduplicated property-level exposure: 9 + 6 is not 15 unique searches. The position values above are query aggregates, not separate landing-page positions. Multiple URLs alone do not establish harmful cannibalization. No redirects, canonical changes, new query-specific URL or keyword-stuffed heading are justified by this small sample. The existing current-value and future-resale tools serve distinct decisions.

## Functional Findings

Used Car Value offered only fixed condition grades, even though its benchmark is a comparable that may already reflect those issues. Blank values became zero, excessive spread was silently clamped to 50%, and deductions beyond the benchmark silently produced zero value. Clear also left the old analysis visible. These behaviors could mislead a visitor trying to estimate a low-value or poor-condition vehicle.

## Improvements

- Condition adjustment is now an editable percentage difference relative to the comparable. Zero means matching condition. Initial -5% remains only an example, not a market-derived condition discount.
- Added a pure, tested value calculation and strict DOM parsing. Required blank/nonfinite inputs, nonpositive benchmarks, percentage reductions below -100%, spreads outside 0-100%, negative adjusted values and overflow are rejected explicitly. Positive condition/local differences remain user assumptions without an invented upper market limit. Explicit, mathematically valid zero estimates remain allowed.
- Retail-to-trade spread no longer silently changes the input. Private party remains the existing midpoint-spread assumption, not a sourced market valuation.
- Invalid calculation and Clear replace stale dashboard values and clear chart data.
- Original default scenario remains $20,400 adjusted retail / $19,176 private-party / $17,952 trade-in.
- Added an original worked scenario for matching poor condition: $6,000 comparable less $800 additional issue = $5,200 adjusted retail; at 12% channel spread, $4,888 private-party / $4,576 trade-in. Avoid double deductions and distinguish repair cost from observed value loss.
- Added contextual links between today's comparable-based estimate and future resale projection, with explicit limits for non-running, severely damaged or branded-title vehicles. No invented universal poor-condition or salvage discount.
- Clarified that the existing +/-4% displayed bands are illustrative, not a market confidence interval. Compact field hints retain the theme and leave detailed interpretation below the tool.

Reviewed [Kelley Blue Book's own valuation FAQ](https://www.kbb.com/faq/values/) for selling-channel distinctions, condition inputs and case-specific appraisal limits. This is an independent planning model, not KBB data or a VIN/transaction feed. No claim of equivalent proprietary data or guaranteed offers is made.

## Verification

- 80 new JavaScript cases: default/worked scenarios, neutral/positive/negative adjustments, full reduction, 0/75/100% spread, blank/nonfinite/type errors, excessive deductions and overflow. Added to the deployment gate.
- 67 Python tests and all 644 JavaScript cases pass; generated copy/link checks cover both distinct intents.
- Playwright at 1366/390/320: defaults, poor-condition scenario, invalid input cleanup, explicit zero, blank submission, Clear, recovery and contextual link. No page errors or horizontal overflow. Inspected the 390-pixel screenshot; compact hints keep the action and primary result in view.
- Isolated build remains 5,005 calculator routes / 284 indexable calculators, with 140,686 validated internal links. Shared CSS is unchanged. Calculator content version: `8a52a8b11945b84d`.

This release is outside the measured search interval. No traffic/ranking improvement is claimed. Keep recent titles stable; evaluate after crawling and a settled post-release window. No payment, outreach, account change, sitemap resubmission, validation request or indexing submission was made.

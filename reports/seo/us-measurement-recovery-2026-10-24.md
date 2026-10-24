# US Measurement Recovery

Observed/exported: 2026-10-24. Performance interval: 2026-09-24 through 2026-10-21.

## Access and Sources

The existing signed-in in-app browser successfully displayed the NS Calculators Search Console property. Selected an explicit daily interval, United States, and Web (text-based); downloaded the original Google CSV ZIP. No subscription, reconnection, new permission or account change was needed. This restores a free measurement path, not the previously expired third-party connector.

Original remains untouched in Downloads: `nscalculators.com-Performance-on-Search-2026-10-24.zip`. ZIP SHA-256: `c5a2ec4c2e7132624cf60b78d7cbbe5aa7e08af221d3765e25129a59dd4b791e`. Raw exports and account-identifying browser content are not committed. The aggregate, scope-checked summary is `exports/us-search-baseline-2026-10-24.json`; it records CSV hashes and row counts for reproducibility.

## Verified Baseline

| Measure | Result |
| --- | ---: |
| US text-based Web clicks | 4 |
| Impressions | 5,933 |
| CTR calculated from counts | 0.0674% |
| Average position, as reported | 49.9 |
| Daily rows | 28 |

Daily, country and device totals independently reconcile to 4 clicks and 5,933 impressions. The UI rounds CTR to 0.1%; the CSV country row rounds it to 0.07%. These are rounding differences, not contradictory counts. Four clicks in 28 days average about 0.14 daily search clicks; clicks are not visitors or sessions. The 1,000 daily organic-visit objective is not achieved or supported by this baseline.

Named query rows are capped at 1,000 and sum to 1 click / 3,380 impressions. The 154 page rows sum to 1 click / 4,006 impressions. Those subtotals are not replacement site totals. Do not attribute every difference to privacy alone, infer missing URLs have zero traffic, or manufacture query/page pairs by joining these separate tables. [Google's report documentation](https://support.google.com/webmasters/answer/7576553?hl=en) distinguishes property versus page aggregation; [its export documentation](https://support.google.com/webmasters/answer/12919797?hl=en) explains the 1,000-row limit and that unavailable placeholders export as zeros. The exact causes of this file's page-table difference are not established.

## Updated Priorities

All five rows below are query-level aggregates, not exact query/page pairs or monthly market volumes. Each has zero exported clicks.

| Query | Impressions | Position | Next action |
| --- | ---: | ---: | --- |
| area calculator | 590 | 8.29 | Hold snippet changes; measure after the October 24 feature is crawled and a settled window exists. |
| car price estimate | 25 | 11.72 | Verify page-filtered query data before further targeting changes; preserve honest comparable-based estimation scope. |
| ratio calculator | 16 | 12.44 | Observe the existing cluster's post-October-20 window, rather than creating another ratio URL. |
| fuel cost calculator | 14 | 8.50 | The October 23 reliability release is outside this measured interval; do not claim its effect yet. |
| vehicle price estimator that includes values for poor condition cars | 11 | 20.09 | Inspect exact landing-page pairs before any consolidation; retain current repair/condition limitations. |

The prior September 20-October 17 baseline overlaps this one for 24 days. Do not label their difference as a clean before/after test or growth caused by recent releases. The October 23-24 changes are outside the new interval entirely. The exported US Keyword Planner monthly-volume field remains unknown, and the original China keyword files remain unsuitable for US volume scoring.

## Indexation Check

The live **All known pages** report displayed 333 indexed / 729 not indexed, but its data was last updated October 16. Reasons were noindex 699, redirects 6, crawled-not-indexed 14, discovered-not-indexed 9, and different Google canonical 1. This is not the current sitemap's index count and does not prove the October 23-24 scope has been processed. Intentional noindex and redirect routes must not be made indexable merely to clear validation warnings.

Read the single canonical example and Google's saved URL Inspection data without starting a live test or requesting indexing. It is `/mortgage-payoff-calculator/`, last crawled October 14. Google saved the old GitHub Pages URL as canonical while the declared URL is the new domain. Current public checks show the old GitHub URL already sends HTTP 301 to the custom domain's HTTP URL, which ends on HTTPS; the HTTPS page returns 200 with the correct self-canonical. The warning is therefore stale relative to current redirect signals, not proof that today's canonical tag is wrong. Do not change it back to GitHub or promise the warning has disappeared; monitor Google's recrawl. The extra HTTP-to-HTTPS hop is recorded, not removed through an unauthorized repository/account setting change.

## Tooling and Decision

Added `scripts/audit_gsc_export.py` to validate future free exports: property/report URL, country, search type, explicit dates, complete daily rows, page domains, nonnegative metric types, duplicate keys/filters, and aggregate reconciliation. Six regression tests reject wrong geography/property, hidden extra filters, date gaps/duplicates, missing metrics and conflicting totals. The importer preserves incomplete row totals, does not fabricate keyword volumes or query/page mappings, and leaves the original archive untouched. Chinese and English header aliases are supported; an unsupported date-filter locale fails explicitly.

All 66 Python tests pass. This release changes measurement scripts, tests, aggregate evidence and the plan only; calculator HTML, theme, canonical tags, robots, sitemap and assets are unchanged. No sitemap resubmission, indexing request, validation request, account modification, payment, outreach or new page was made.

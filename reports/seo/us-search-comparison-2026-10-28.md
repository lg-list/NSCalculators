# US search measurement and revised priorities

## What changed

The supported in-app browser can read the existing NS Calculators Search Console tab again. Downloaded untouched CSV ZIPs for **September 28–October 25** and a comparison with **August 31–September 27**. Both intervals are 28 completed dates, non-overlapping, United States only and text-based Web search. Country does not impose an English-language filter. No paid connector retry, account change, sitemap submission or indexing request occurred.

The source archives remain untouched in Downloads. The single-window archive SHA-256 is `a91036cffb73be6e46be5caf08b3fee57635927ceba329557109cdeb7ae87e89`; the comparison archive is `6f79c7cf26e1167b1ca60246da6df2ec51f757ded264217027b1bb808dce9f7e`. `exports/us-search-comparison-2026-10-28.json` records per-table hashes, row counts and the aggregate analysis. Raw ZIPs, all raw queries and account-identifying browser content are not committed.

## Results

| Measure | August 31–September 27 | September 28–October 25 |
| --- | ---: | ---: |
| Google Web clicks from US | 2 | 3 |
| Impressions | 1,663 | 7,275 |
| CTR from exact counts | 0.1203% | 0.0412% |
| Reported average position | 64.59 | 54.40 |
| Average daily clicks | 0.0714 | 0.1071 |

Impressions increased by 5,612 (+337.46%), while clicks increased by only one. Three versus two clicks is not a reliable treatment-effect estimate. The average-position change also reflects a changing query mix, rather than proving every keyword improved. Clicks are not visitors or GA4 sessions, and these results do not establish progress to 1,000 daily organic visits. Exposure has grown, but acquiring clicks remains the central measured problem.

The earlier October 24 baseline spans September 24–October 21 and overlaps this new window. It must not be presented as an independent control. This export ends October 25, before the October 27–28 repairs, and provides at most a small portion of the Area title/content observation period. It cannot evaluate those releases.

## Reconciliation and coverage

- The single-window daily, country and device counts independently sum to **3 clicks / 7,275 impressions**. Comparison country and device rows agree for both windows. Prior-period daily rows were not included in the comparison export.
- The single UI headline shows 7,280, but its inspected title attribute is 7,275, matching the raw export. This is a rounded display, not conflicting exact totals. The comparison headline exposes 7,275 directly.
- Single-window queries: **1,000 rows, 0 clicks / 4,254 impressions**. Single-window pages: **121 rows, 0 / 5,139**. These are detail subtotals, not site totals. A page missing from the table is not proven to have zero traffic.
- Comparison queries contain a **1,774-name union**, with **0 / 4,276** current detail and **1 / 1,315** prior detail. Every overlapping single-export query has identical current counts. The union exposes 22 more current impressions in additional rows than the single-window query table. Do not assume a universal 1,000-row cap for the union or claim complete named-query coverage.
- Comparison page union: **243 URLs**, with current **0 / 5,139** and prior **1 / 1,321**. Differences from property totals are not resolved by adding rows or substituting them for totals. Their full causes have not been established.
- Exported zero impressions/positions in comparison rows may mean unavailable detail. They are not sufficient evidence that a query was newly gained or lost. No separate query and page tables were joined into artificial pairs.

[Google's report overview](https://support.google.com/webmasters/answer/7576553?hl=en) explains report configuration and filtering. The limitations above are established from the actual export; they do not rely on assuming that every missing value has the same cause.

## Confirmed opportunities and execution queue

Exact-query filters with the Pages breakdown were rendered and inspected. `exports/us-query-page-observations-2026-10-28.json` preserves the scoped observations and report URLs:

| Query | Impressions / clicks | Position | Observed page |
| --- | ---: | ---: | --- |
| area calculator | 587 / 0 | 8.19 in CSV, 8.2 rounded UI | `/area-calculator/` (587 / 0 under exact query) |
| fuel cost calculator | 14 / 0 | 8.5 | `/trip-fuel-cost-calculator/` (14 / 0 under exact query) |

Each filtered Pages table showed one URL. The position is query-level, not a separately measured page rank. These are observed site searches, not US monthly market search volumes.

The executable queue is `exports/us-seo-action-queue-2026-10-28.json`:

1. **Area: preserve the current treatment and measure.** It is the largest observed near-page-one opportunity, but the current interval ends too soon to judge the October 24–25 edits. Earliest next review is November 8, with a completed post-change interval and device/exact-query segmentation. Do not churn the title again or create near-duplicate area pages while this evidence is still immature. Google's [SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide#how-long-until-i-see-impact-in-search-results) advises allowing weeks to assess many search changes; November 8 is our review date, not a Google guarantee.
2. **Fuel Cost: next focused CTR diagnostic.** Its exact query is already matched to the intended existing trip-cost URL. Check the served snippet and US trip task before proposing one change. Fourteen impressions are too few for confident CTR attribution. Preserve canonical consolidation and working US/UK unit support; do not add a competing URL or invent current gas prices.
3. **401(k): next full functionality audit.** Query `401k calculator` has 123 impressions at 83.09; the separate page aggregate is 266 at 79.44. These are not an exact pair. Related small-count matching and withdrawal phrases provide task hypotheses, not large-volume proof. Check full projection/withdrawal validation and the stated tax year using current IRS sources, preserving the employer-match checks already completed. Do not make local clones from place-name query variants.
4. **Observe recent repairs.** Boat, personal-loan and other recently upgraded pages remain live; their larger exposure is not attributable to those releases from this export. Continue maintenance for reproducible defects, while waiting for dates that actually include the repair when measuring impact.

No new indexed pages or website metadata changes were made during this measurement turn. The new measurements replace the stale basis for prioritization. US Keyword Planner data, approved outreach sender/draft and later measurement windows remain separate pending inputs; no spend or unapproved outreach occurred.

## Validation and reproduction

`scripts/analyze_us_search_exports.py` reads the original archives and writes the aggregate JSON without modifying input ZIPs. It rejects wrong geography/search type, overlapping/mismatched period headers, missing or duplicate daily dates, inconsistent country/device counts, changed overlapping query counts and unexpected page hosts. Eight synthetic regression tests cover reconciliation, source immutability, missing-detail handling and corrupt-scope cases. The full Python suite passes **132 tests**.

Run it with the two original ZIP paths, `--start 2026-09-28 --end 2026-10-25`, and an output JSON path. Dates, hashes, counts and calculations are inspectable. No workbook or raw export is rewritten, and no browser credential/session data is accessed. The full 90-day objective remains active and unproven.

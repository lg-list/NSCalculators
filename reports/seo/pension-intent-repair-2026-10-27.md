# Pension calculator: repair an existing intent mismatch

## Evidence and scope

The live `/pension-calculator/` page was inspected with public Playwright on October 27. It used `cn_retirement` and asked for current savings, contributions, return, years and inflation. It did not compare defined-benefit pension payout quotes. The repository confirmed that mapping. This was a product/intent mismatch, not just a missing keyword in the title.

The previously verified US Search Console export covers **September 24–October 21, 2026**, Web text search. The page table reports **38 impressions, 0 clicks, position 45.84** for this URL. Separately, the query table includes `pension payout calculator` (3 impressions, position 21.67), `pension payment calculator` (3, 22.33), `pension calculator` (3, 30.67) and `pension payments calculator` (2, 19). These incomplete tables are **not query/page pairs**. Small observations justify checking functionality; they do not establish US monthly demand, competition or a traffic forecast.

Source archive: `nscalculators.com-Performance-on-Search-2026-10-24.zip`; SHA-256 `c5a2ec4c2e7132624cf60b78d7cbbe5aa7e08af221d3765e25129a59dd4b791e`. Baseline and table hashes remain in `exports/us-search-baseline-2026-10-24.json`. No new settled performance window or US Keyword Planner file is claimed.

## Implemented on the existing URL

- Replace the savings-growth alias with a dedicated pension engine covering lump sum vs monthly income, single-life vs joint-survivor benefits, and earlier vs later retirement.
- Compare entered quotes, annual return and COLA; add explicit 50%, 75% and 100% survivor continuation, present-value summaries, a compact two-series line chart and an inspectable annual table.
- Preserve the theme, split input/results layout and compact mobile controls. Chart labels use responsive logical pixels and device-pixel scaling rather than shrinking a fixed desktop canvas.
- Validate active fields without clamping invalid ages, quotes or rates into plausible answers. Clear removes stale results and hides the chart until inputs are complete. Enter calculates the selected comparison.
- Target `pension calculator` and `pension payout calculator` naturally in title, description, explanatory content and site search. Link to this workflow from retirement planning; link back to savings, 401(k) and Social Security tools for their distinct tasks.
- Reuse the indexed route. No new landing pages, indexation expansion, fabricated demand, credentials or reviews.

## Timing, reference verification and a deliberate accuracy distinction

Reference UI: [Calculator.net Pension Calculator](https://www.calculator.net/pension-calculator.html). Numeric result and rendered chart observations, exact input URLs and timestamps are archived in `exports/pension-reference-benchmarks-2026-10-27.json`.

For lump sum and retirement-age comparisons, a year's monthly checks are combined and discounted at its midpoint; the table age marks completion of that payment year. For survivor calculations, the entered death age-year is included, annual income is valued at its start, and the payment difference accumulates to its end. These conventions are exposed on the page. They are approximations, not actual monthly payment-date calculations or actuarial valuations.

Reference defaults reproduced:

| Observation | Result |
| --- | --- |
| $800,000 vs $5,000/month, age 65, 5% return, 3.5% COLA | First completed payment-year crossover: 81 |
| Same pension PV at completed age 66 / 80 / 81 | $58,554 / $795,690 / $842,877, rounded |
| Default survivor capital if death at retirement | $657,173, rounded |
| Default payment-difference accumulation | $514,709, rounded |
| Default remaining survivor capital | $428,530, rounded |
| Retire at 60 vs 65, $2,500 vs $3,800/month, same rates: age 86 PV | $639,608 vs $636,503, rounded |
| Same earlier/later comparison: age 87 PV | $659,748 vs $662,278, rounded |

The reference's later-retirement **narrative says age 86**, although its own rendered chart still shows the earlier stream ahead at 86. This implementation reports **87**, the first completed payment year that actually meets/exceeds the other stream. It does not silently copy that inconsistent sentence or claim exact parity with every reference statement. Twenty-four selected chart values are checked against the archived rounded observations, in addition to independently derived closed-form scenarios.

## Primary sources and limits

[PBGC's pension benefits overview](https://www.pbgc.gov/workers-retirees/learn/pension-benefits-overview) distinguishes straight-life, joint-survivor and pop-up forms, and states that PBGC payments have no statutory COLA. The tool models an ordinary joint-survivor stream, not a pop-up feature. [PBGC's annuity/lump-sum guide](https://www.pbgc.gov/workers-retirees/learn/annuity-lump-sum) supplies broader decision context. PBGC-specific rules are not generalized into universal pension eligibility.

No prediction of lifespan, tax/rollover decision, insurance quote, salary benefit or guaranteed investment return is produced. The 3.5% COLA is explicitly hypothetical; fixed pensions can use zero. Results are scenario arithmetic, not a recommendation to elect or replace a pension.

## Validation and measurement

- 270 JavaScript numerical, crossover, survivor, timing, validation and archived-chart checks, plus 9 canvas-width/pixel-density checks; closed-form geometric-series checks include zero return, equal return/COLA and negative returns.
- 116 Python tests, all existing JavaScript suites against the optimized deployment bundle, asset hashing/optimizer tests, indexation and schema contracts.
- Local Playwright at 1366, 390 and 320 CSS pixels: three modes, survivor percentage, invalid/inactive inputs, Clear recovery, Enter, chart pixels, annual table, metadata, site search and category discovery. Calculate remains within the first 844px screen; no horizontal page overflow.
- Sitemap scope remains **305 URLs**, including **287 calculators**; no build-date lastmod claims. Observe the corrected URL in a later settled US GSC window; no ranking, traffic, conversion or Core Web Vitals improvement is asserted from these tests.
- Final isolated optimized bundle: **482,331 bytes**, version **`ded8f8493b6859ef`**; 4,905 script references verified. CSS version **`228773fad48ba1f8`**, 5,027 references. The new workflow adds code to the existing shared asset; no claim of faster delivery is made for this feature change.

The 90-day traffic objective remains active and unproven. Outreach approval/sender and the promised US keyword-volume CSV remain separate owner-dependent tasks; this change sends no outreach and makes no external submissions.

# GPU and AI chart semantics — October 29, 2026

Previous turn progressed the used-car comparable benchmark and independent-channel chart in commit 997e66e372, deployed successfully in Pages run 40898120194 and verified in production at three widths. This follow-up examines whether similar chart composition errors exist elsewhere.

## Prioritization and verified findings

The latest completed US page aggregate contains 3 GPU Calculator impressions, zero clicks and position 72.67 (September 28–October 25). No new Google data was obtained and this is not a volume estimate or proof of keyword/page matching. This repair is justified by concrete user-visible defects in the owner's existing GPU/AI tools, not by an invented high-demand keyword forecast.

Production Playwright captured actual canvas text before editing:

- GPU: 30.72 TFLOPS, 672 GB/s and 320 W were displayed as currency slices of **$1,022.72**, including misleading 3%, 65.7% and 31.3% shares.
- AI Compute: PFLOP-days, GPU-hours and kWh were displayed as currency slices of **$22,896.09**. They have different dimensions and cannot form a sum or a shared percentage chart.
- AI Cost: $750 input-token cost, $900 output-token cost and their $55 daily average were added to a **$1,705** chart total. The billing-period cost is $1,650; the daily average is derived from it and must not be added again.

The audit also checked the simple-interest chart's data: it contains only principal and interest, a valid nonnegative composition in its ordinary example. It was preserved rather than applying a sitewide chart removal rule.

## Changes

GPU and AI Compute retain four independently labeled result cards and all existing details. Their mixed-unit pie charts are removed and the dashboard states why those measures are not shares of a combined total. They were not replaced with another misleading common-axis comparison.

AI Cost retains its currency pie, now with exactly two components: input-token and output-token costs for the entered period. The daily estimate stays visible in the cards and is also labeled separately in the details table; the table now reconciles the period total. Example prices are user-editable assumptions, not verified current provider pricing. There is no new provider feed or API call.

No numerical model, input, default value, title, description, canonical, route or indexation scope changed. This is a chart interpretation repair, not a certification of every existing GPU, training or cost-model input boundary. Future invalid-input and model-assumption audits remain separate work; current sparse search evidence cannot establish traffic impact.

## Verification and release

- 18 chart-component reconciliations and GPU/AI output regressions, including 1/7/30/365 billing days and zero/nonzero input/output rates. Cost components sum to the modeled period total; daily cost is excluded.
- 138 Python tests, including mixed-unit chart absence, preserved result/table containers, cost composition copy and unchanged simple-interest pie.
- All 41 JavaScript suites pass. The new chart test runs in Pages CI against the final bundle.
- Browser verification across three pages at 1366×844, 390×844 and 320×844: all independent cards/details remain, no mixed-unit chart, correct $1,650 and $55 cost totals, no runtime errors or horizontal overflow, canonical unchanged. Before/after canvas text observations are saved in `exports/compute-chart-observations-2026-10-29.json`.
- Final build: 305 sitemap URLs, max depth 3; schema and full/specialized/CSS version checks pass. CSS and the specialized 401(k) script remain unchanged by this repair. The full runtime changes to `0ef9766ce1fa84fd`; per-engine renderer specialization excludes these unrelated renderer branches.

After the exact Pages workflow succeeds, rerun `scripts/verify_compute_charts_browser.cjs --live` on production. No paid tools, outreach, account changes, external submissions or keyword landing pages. No field CWV, rank/CTR improvement or 1,000-daily-visit result is claimed.

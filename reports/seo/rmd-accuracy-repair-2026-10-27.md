# RMD calculator: input integrity, trustworthy tables and clear projections

## Why this existing page

The verified US Search Console export for **September 24–October 21, 2026**, Web text search, reports **99 impressions, 0 clicks, position 82.94** for `/rmd-calculator/`. Separately, its query table includes `rmd calculator 2026` (4 impressions, position 69) and `rmd table 2026` (4 impressions, position 92.75). Those incomplete tables are not query/page pairs or US monthly keyword-volume estimates. No traffic lift is inferred.

Source archive: `nscalculators.com-Performance-on-Search-2026-10-24.zip`, SHA-256 `c5a2ec4c2e7132624cf60b78d7cbbe5aa7e08af221d3765e25129a59dd4b791e`; provenance remains in `exports/us-search-baseline-2026-10-24.json`. No newer settled export or US Keyword Planner data is claimed.

Public Playwright inspection reproduced three material problems before this repair:

- Birth year `1951.9` silently became `1951` and produced a plausible $12,195.12 answer.
- Distribution year `2021` still produced an answer using the 2022-onward factor set.
- Clear replaced the headline but left 20 old projection rows visible.

Repository review also found silently clamped projection inputs, an incorrect historical age-72 starting-year claim for older cohorts, a Table III fallback when an otherwise qualifying spouse was below the available Table II age range, and negative growth hidden from the chart. These justify an accuracy repair before pursuing stronger ranking claims.

## Authoritative factor verification

`scripts/capture_rmd_factors.cjs` read the public rendered tables in [IRS Publication 590-B](https://www.irs.gov/publications/p590b) with Playwright. It verified **all 49 Uniform Lifetime factors for ages 72–120** and **all 3,234 Joint Life factors already stored by this site**. No factor discrepancy was found. The export includes source publication, timestamp, extracted values and counts:

`exports/rmd-irs-factors-2026-10-27.json`

The production Uniform Lifetime data now lives in `src/data/rmd-uniform-lifetime-table.json`. Both the calculator bundle and the visible lookup table use this same dataset. The archived official extraction independently checks it in tests. The script is a public-source capture tool, not a scheduled network dependency of the build.

## Repair and user-facing behavior

- A pure projection function validates whole years and ages, finite nonnegative balances, return assumptions and projection length. Unsupported years before 2022 are rejected rather than using the wrong factor era. Zero balances calculate zero instead of failing or dividing a rate by zero.
- Sole-beneficiary status controls whether the spouse input is visible and active. The greater-than-10-year threshold is tested at both sides. A spouse younger than the published table's starting age of 20 produces an explicit unavailable result, not a substituted Uniform factor.
- Historical starting ages distinguish 70½, 72, 73 and 75. For older births, an optional birth-half selector refines the first year without collecting a full date of birth. Unknown birth half remains an explicitly uncertain historical year, not a guessed year; the selected 2022-onward RMD remains calculable.
- For 1959 births, the page explicitly labels age 73 as the planning assumption under the 2024 proposed clarification. This is supported by [IRS Bulletin 2024-33](https://www.irs.gov/irb/2024-33_IRB); the [current applicable-age regulation](https://www.ecfr.gov/current/title-26/section-1.401(a)(9)-2), inspected October 27, still reserves the relevant paragraph. Do not describe this edge as a final rule without rechecking.
- The annual model preserves the prior-year-end RMD basis, then applies assumed growth/loss before a year-end withdrawal. If projected available funds cannot cover the calculated RMD, it shows a modeled funding gap and stops the schedule. It does not imply that a legal withdrawal obligation disappears or calculate a tax penalty.
- Invalid inputs and Clear remove old schedule rows, summary numbers and chart values. Negative projected returns retain a signed loss bar. Existing chart sizing and shared resize handling are preserved.
- The inputs use the existing compact two-column style. At 1366, 390 and 320 CSS pixels, Calculate is visible within the first 844px screen. Annual projections and the new 49-row IRS factor lookup are expandable below the primary result.

## Search intent and internal links

The existing URL now answers both `RMD calculator 2026` and `RMD table 2026` with functioning calculations, an inspectable factor lookup, timing assumptions and citations. Metadata and site search use these terms naturally. Contextual links connect RMD with retirement savings and pension payout comparisons while distinguishing their purposes. No new keyword-clone URLs were added.

This tool excludes inherited accounts, Roth owner accounts, still-working deferrals, beneficiary changes, account aggregation, tax adjustments and corrective excise taxes. Future schedules assume unchanged tables and rules. Use the [IRS RMD FAQs](https://www.irs.gov/retirement-plans/retirement-plan-and-ira-required-minimum-distributions-faqs) and custodian guidance for an actual withdrawal obligation.

## Validation

- **3,283 IRS-derived factor checks and 189 projection/validation scenarios**, including the IRS owner-age-75/spouse-age-64 example ($100,000 / 25.3), older birth cohorts, equal/greater-than-ten-year spouse gaps, negative returns, funding gaps, zero balances and schedule caps.
- **118 Python tests**, existing JavaScript regression suites against the final optimized bundle, indexation/schema contracts and script/stylesheet hash checks pass. The Pages workflow was also parsed with an isolated PyYAML validator before commit.
- Public-browser local checks at **1366 / 390 / 320px** cover first-screen Calculate, invalid/unused inputs, birth-half refinement, 1959 scope, funding-gap output, Clear recovery, Enter, the 49-factor lookup, canonical/indexability/schema, site search and a contextual backlink. Screenshots were visually inspected; no horizontal page overflow or page-script errors were observed.
- Default output remains **$12,195.12** for age 75 and a $300,000 prior-year-end balance. At 5% return the first projected ending balance is **$302,804.88**. At -99% return, the selected-year RMD remains unchanged and the **$9,195.12** modeled funding gap is explicit.
- Final optimized calculator asset: **485,519 bytes**, version **`6639911184c87b3d`**, 4,905 references. Stylesheet version **`f56cfcdbbdaa312e`**, 5,027 references.
- Sitemap remains **305 URLs**, including **287 calculators**, with maximum crawl depth 3. This feature repair is not proof of ranking improvement or a Core Web Vitals improvement.

Reproduction: build into `doc-work/discovery-build`, optimize the assets, run `node scripts/test_rmd.cjs doc-work/discovery-build/assets/calculator.js`, and run `node scripts/verify_rmd_browser.cjs`. After deployment, the same browser script accepts `--live`. Browser checks block analytics requests to avoid polluting GA4.

The 90-day growth objective remains active and unproven. External outreach approval/sender and the promised US keyword-volume CSV remain separate pending items. No outreach, external submission, paid action or account-setting change was performed.

# IRA calculator: replace the generic savings alias

## Evidence and priority

The previous release completed the towing repair. This run first attempted a measurement refresh: GSC Wizard still required a paid plan, while the existing signed-in Search Console tab could be inventoried but its binding timed out. No new traffic result was obtained, no account was modified and no paid service was opened. See the October 27 update in `search-console-access-2026-10-22.md`.

The last verified US Search Console export covers **September 24–October 21, 2026**, Web text search. The IRA URL has **41 impressions, 0 clicks, position 83**. A separate query aggregate includes `ira monthly payout calculator` (12 impressions); that is not a query/page pair. The export is incomplete and is not US monthly demand, a current ranking report or evidence of this release's impact. Source archive SHA-256: `c5a2ec4c2e7132624cf60b78d7cbbe5aa7e08af221d3765e25129a59dd4b791e`; detailed provenance remains in `exports/us-search-baseline-2026-10-24.json`.

Public Playwright inspection of the production IRA page confirmed `cn_retirement`, with savings, monthly contribution, return, years and an inflation field. It did not compare IRA tax scenarios. The repository confirmed the same alias. A purpose-built comparison is a functionality/intent repair, not a claim that a snippet change will win high-volume searches.

## Implemented on the same URL

- A dedicated equal-pre-tax-budget model for fully deductible pre-tax IRA, Roth and simplified taxable savings scenarios, with separate current and retirement tax assumptions.
- Retirement-age results before and after modeled tax, three alternative after-tax balances in a compact bar chart, a comparison table and annual start/end values for all four displayed series.
- Explicit finite-value, whole-age and domain validation; no silent age rounding. Clear and invalid inputs remove old annual rows, summary values and chart output. Zero budgets remain valid zero scenarios.
- Existing theme and input/results split preserved. The seven inputs, short scope note and Calculate fit in the first 844px at 1366, 390 and 320 CSS-pixel widths.
- Natural title/description targeting of IRA, Traditional vs Roth and taxable savings; contextual routing from retirement planning and to working accumulation, drawdown and RMD tools. The unavailable annuity-payout route is not recommended as if it were functional. No new landing pages or indexation expansion.

## Model and reference checkpoints

For P as the pre-tax equivalent starting amount, C as the annual pre-tax budget, annual return r, current assumed tax t and retirement assumed tax u:

- Pre-tax IRA: start at P; each year multiply by (1+r), then add C. Its modeled terminal after-tax value is the ending balance multiplied by (1-u).
- Roth: start at P×(1-t); add C×(1-t) at each year end, with no modeled annual tax and qualified withdrawals assumed.
- Taxable savings: use the same after-tax starting amount and contribution; tax positive yearly returns at t. Losses receive no assumed tax credit.

This is an equal gross-budget comparison, not a conversion, tax return or eligibility determination. An existing already-after-tax Roth balance is a different input basis. The pre-tax IRA assumption may illustrate deductible Traditional/SEP/SIMPLE growth, but does not equate their contribution or employer-plan rules.

The public [Calculator.net IRA page](https://www.calculator.net/ira-calculator.html) provided rounded results and annual values. They are archived in `exports/ira-reference-benchmarks-2026-10-27.json`. **Its form values were not independently read.** Under the stated end-of-year model, the first two annual pre-tax changes imply 6% growth and a $7,500 contribution; initial after-tax ratios imply 25% current and 15% retirement tax assumptions. This parameter interpretation is explicitly an inference, checked against the selected displayed data.

With a $30,000 pre-tax starting budget, age 30 to 65 and those assumptions:

| Scenario | Modeled final value | Public reference, rounded |
| --- | --- | --- |
| Pre-tax IRA before terminal tax | $1,066,343.45 | $1,066,343 |
| Pre-tax IRA after terminal tax | $906,391.93 | $906,392 |
| Roth, assuming qualified | $799,757.59 | $799,758 |
| Simplified taxable savings | $563,433.80 | $563,434 |

Forty numeric checkpoints (final results plus selected annual start/end observations) match. A transcription of one intermediate row was caught by the check and corrected against the public source before commit; no formula was altered to fit a mistranscribed fixture. No exact-parity claim is made for every reference scenario, negative-return loss credits or tax-law eligibility.

## Source-backed limits

[IRS Traditional and Roth IRA guidance](https://www.irs.gov/retirement-plans/traditional-and-roth-iras) and [Publication 590-A](https://www.irs.gov/publications/p590a) provide contribution and deduction context. [Publication 590-B](https://www.irs.gov/publications/p590b) explains qualified Roth distributions, including the five-year condition and age 59½ or other qualifying circumstances. Merely entering an age does not determine qualification.

The tool does not enforce annual limits, compensation requirements, income phaseouts, nondeductible basis, conversions, early-distribution taxes, RMDs or changing tax rates. Taxable savings use an annual tax-drag assumption, not a capital-gains/dividend/deferral model. Returns are constant hypotheses. Younger retirement scenarios explicitly state that early-distribution taxes are excluded. This produces conditional scenario arithmetic, not an account-selection recommendation.

## Validation

- **444 numerical/accounting/validation scenarios** using independently derived annuity future values, zero and negative returns, equal tax-rate symmetry, tax-rate independence, annual cash flows, zero budgets and stale-output removal; **40 public reference numeric checkpoints**.
- **122 Python tests** and all existing JavaScript regression suites pass against the final optimized deployment bundle. Pages workflow YAML was parsed before commit.
- Local Playwright at **1366 / 390 / 320px** passes: three-scenario outputs, annual start/end columns, tax sensitivity, invalid inputs, early-distribution scope, Clear recovery, zero scenarios, Enter, independent bar chart, canonical/indexability/schema, site search and a contextual retirement backlink. Screenshots were visually inspected; no page-script errors or horizontal page overflow were observed.
- Indexation/schema/asset contracts pass: **305 sitemap URLs**, **287 indexable calculators**, maximum crawl depth 3; 4,905 calculator-script and 5,027 stylesheet references.
- Final optimized calculator asset: **492,632 bytes**, version **`d7db97446bd2d982`**. CSS version **`ad1fe6f30e15d19c`**. Feature code increases the shared asset; no Core Web Vitals, ranking or traffic improvement is inferred.

Reproduction: build/optimize into `doc-work/discovery-build`, run `node scripts/test_ira.cjs doc-work/discovery-build/assets/calculator.js`, then `node scripts/verify_ira_browser.cjs`. The browser verifier accepts `--live` after deployment and blocks analytics to avoid synthetic GA4 traffic.

The 90-day growth objective remains active and unproven. No paid action, outreach, external submission or account-setting change occurred. The separate Roth IRA alias has not been upgraded by this change and is not promoted here as a verified qualification or contribution-limit tool.

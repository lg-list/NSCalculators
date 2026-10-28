# Amortization calculator: validated extra payments and date accounting

## Priority and observed failure

The previous concrete release is deployed and verified. The last verified US Search Console export (September 24–October 21, 2026, Web text search) contains 83 impressions, zero clicks and position 71.14 for the amortization URL. This is an old page aggregate, not a query/page pair, current ranking or monthly market volume. Provenance remains in `exports/us-search-baseline-2026-10-24.json`. No fresh Search Console report, paid connector or promised US Keyword Planner CSV was used here.

Public production Playwright checks on October 28 confirmed that entering -6% silently produced a 0% schedule ($1,111.11/month) and Clear left 15 annual rows visible. Source inspection also found fractional terms silently floored, malformed months accepted, nonfinite/tiny interest instability, undated extras ignored and yearly extras forced to every twelfth payment without a selectable starting month. Those are functional and trust defects on an already indexable page, not a reason to generate another landing page.

## Change on the existing URL

- A pure validated amortization model, with required principal, annual note rate, whole years/additional months and first payment month. Negative, missing and nonfinite required inputs are rejected rather than clamped or truncated.
- Stable scheduled payment calculation using log1p/expm1. Each month's base principal is the discounted payment, avoiding cancellation when payment and interest are nearly equal. Extras' accumulated balance reduction accounts for their later interest effect. The final actual principal is cleared, including sub-cent mathematical balances, without charging requested excess extras.
- An explicit extra-payment toggle; independently dated monthly and annual starts; one main and ten additional dated one-time amounts. Same-month extras combine, repeat monthly/every twelve months as selected, and cap at outstanding principal. Positive extras outside the original repayment months are rejected; planned extras after an earlier actual payoff are identified as not charged.
- Actual regular portions, extra principal and total paid including extras are displayed separately. Total paid equals original principal plus interest. The principal/interest pie counts principal once, including the principal paid through extras.
- Monthly rows show their actual calendar month, annual rows identify loan years, and the payoff date equals the last monthly row. Clear/invalid inputs remove old rows, summaries and the chart. Turning extras off preserves their entries but disables/excludes them.
- Two-column mobile fields preserve 16px input text and first-screen Calculate at 1366, 390 and 320px. Existing theme and compact pie remain intact. Helpful original explanation naturally targets amortization schedule and extra-payment intent; title, canonical, index scope and existing related-loan links are retained. The page moves from the erroneous Savings & Growth grouping to Loans, so its directory placement, breadcrumbs and related navigation reflect borrowing intent.

## Public comparison and deliberate date correction

`exports/amortization-reference-2026-10-28.json` records rendered form values, selected schedule rows and numeric metrics from four public [Calculator.net amortization scenarios](https://www.calculator.net/amortization-calculator.html). Reproduce with `scripts/capture_amortization_reference.cjs`; it performs only public browser calculations and does not use sign-in or private endpoints. Form values were read directly, including thousands separators, rather than inferred from results.

For $200,000 at 6% over 180 months, payment is $1,687.71 and baseline interest $103,788.46. With payment 1 in October 2026:

| Extras | Months | Interest | Actual extras | Regular portions excluding extras |
| --- | ---: | ---: | ---: | ---: |
| None | 180 | $103,788.46 | $0 | $303,788.46 |
| $100 monthly from November 2026 | 165 | $93,886.58 | $16,300 | $277,586.58 |
| $1,200 yearly from November 2026 | 164 | $93,182.37 | $16,800 | $276,382.37 |
| Both recurring extras, plus $10,000 November 2027 and $5,000 November 2028 | 136 | $72,045.17 | $42,800 | $229,245.17 |

The source summary's “total monthly payments” excludes extras. For the combined case, total paid including extras is $272,045.17, not $229,245.17. Our labels make this distinction explicit.

**Source date discrepancy:** its baseline monthly table begins October 2026 and row 180 is September 2041, while its top payoff label says October 2041. The same one-month difference appears in the extra-payment cases. We match the numerical schedule and use the actual last-row month: September 2041 / June 2040 / May 2040 / January 2038 respectively. We do not reproduce the inconsistent top date label. The site's field explicitly says first payment month, avoiding an origination-versus-payment-month ambiguity.

The original explanation also cites the [CFPB amortization explanation](https://www.consumerfinance.gov/ask-cfpb/how-does-paying-down-a-mortgage-work-en-1943/). This equal-month fixed-rate model excludes daily accrual, escrow, fees, penalties, irregular payments and recasting. It is not a lender payoff quote or fee-inclusive APR calculation.

## Verification

- 231 accounting, numerical-stability, timing, independent-recurrence, boundary and validation scenarios; 64 public numeric checkpoints. Tests include rates 0, 1e-15, 6 and 100%, principal $0.01-$1 billion, 1-1200 months, 120 deterministic independently simulated scenarios, eleven same-month extras, early payoff, year 0001 and year 9999, missing/negative inputs and stale-output removal.
- 124 Python tests and all final-bundle JavaScript regression suites pass; the new numerical suite is included in Pages CI. Workflow YAML parsed locally.
- Local Playwright at 1366 / 390 / 320px passes first-screen Calculate, baseline/three extra scenarios, calendar consistency, two-column fields, extra toggle, multiple one-time payments, cost totals, unused-extra notice, invalid/Clear recovery, Enter, canonical/indexability and page overflow checks. Screenshots were inspected; the compact pie remains round and readable. QA analytics requests are blocked.
- Indexation/schema/script/style contracts pass: 305 sitemap URLs, 287 indexable calculators, maximum crawl depth 3, 140,801 resolved internal links, 4,905 calculator script references and 5,027 stylesheet references. Optimized calculator bundle: 496,505 bytes, `109c14b8da976e80`; CSS `aeca0894ce47a020`. No measured Core Web Vitals or traffic lift is claimed.

Reproduction: isolated build/optimizer into `doc-work/discovery-build`, `node scripts/test_amortization.cjs doc-work/discovery-build/assets/calculator.js`, then `node scripts/verify_amortization_browser.cjs` or `--live`. Browser checks and screenshots remain under ignored `doc-work/`.

The 90-day organic growth target remains active and unproven. No new thin URLs, indexation expansion, paid action, outreach, external submission or account change occurred.

# Personal Loan Payments, Net Cash and Fees

Date: October 25, 2026

## Evidence

The existing US GSC report (September 24-October 21) was filtered to the exact query personal loan calculator. The Pages tab shows `/personal-loan-calculator/`, zero clicks and 34 impressions; query position is 71.3. This is an observed query/page pair, not an inferred CSV join or market-volume estimate. Minimal transcription is in `exports/us-personal-loan-opportunity-2026-10-25.json`.

Production used the generic loan engine with four fields and no fee/proceeds/schedule model. Entering -$10,000 returned a negative monthly payment and negative interest as an apparent answer. That error and the missing cash-flow distinctions justify upgrading the existing route, not creating fee/insurance keyword variants.

Reviewed [Calculator.net's personal loan tool](https://www.calculator.net/personal-loan-calculator.html) for the functional coverage of fees, insurance and schedules. The site was not copied. The independent model and worked example below preserve the original NS $10,000 initial principal rather than claiming complete competitor parity.

## Scope and Accounting

Dedicated `personal_loan_advanced` engine on the existing URL. Inputs: principal, annual note rate, whole years/additional months, first payment month, optional origination fee in dollars or percent, deducted/upfront handling and monthly insurance. The unchecked option hides/disables cost inputs and excludes their values and validation. Clear removes stale cards, chart and schedule data.

Payments reuse the stable fixed-monthly-payment helper. The schedule evaluates remaining-payment present values to avoid the floating-point balloon produced by naive balance recurrence at long/high-rate boundaries. First payment month labels payment one, with one monthly period from funding assumed; no day-level accrual or time-zone conversion is implied.

Deducted: disbursement = principal - fee, upfront fee = 0. Upfront: disbursement = principal, upfront fee = fee. Both have net cash = principal - fee when the upfront fee is paid at funding. Interest and any monthly insurance continue to be paid against the full entered principal. The fee must leave positive net cash.

Total borrowing cost = interest + origination fee + included insurance. Total cash outflow = scheduled loan payments + insurance + separately paid upfront fee. The pie reconciles to cash outflow: deducted principal is split into net disbursement and fee; upfront mode shows full principal plus the separate fee. There is no duplicated fee or per-month payment inserted into the whole-term pie.

An annualized cash-flow cost rate discounts all modeled monthly cash payments against net cash at funding, then annualizes the monthly rate by multiplication by 12. It is **not** labeled a lender-disclosed/legal APR, an effective annual yield or a determination of insurance finance-charge treatment. [CFPB's rate/APR explanation](https://www.consumerfinance.gov/ask-cfpb/what-is-the-difference-between-a-loan-interest-rate-and-the-apr-en-733/) supports separating the concepts; the account-specific legal classification is not modeled. No loan approval, current rate, credit eligibility or personalized borrowing advice is claimed.

## Content and Presentation

Accurate title/description now include payments, fees and net proceeds. Original method copy explains withheld versus upfront fees, a worked $10,000/10%/60-month example, $500 fee and $10/month insurance, schedule timing, numerical limits, omitted lender rules and the cost-rate distinction. Links from Loan and Amortization route fee-specific intent here, and the page links back for those distinct structures.

Existing theme/plugins, URL, self-canonical and index scope remain. Compact paired inputs stay aligned at narrow widths, with a month-only control and a visible first-screen Calculate button in the tested 844px-high viewports. The pie has matching horizontal/vertical display scale; the monthly table is collapsible and scrolls inside its container. No cloned pages, new category or external submission.

## Verification

- 101 Python tests pass, including two new dedicated-engine/metadata/link/scope tests. Business and Boat Loan retain their original engines and are not certified by this change.
- All existing JavaScript suites pass; the new suite covers 94 scenario groups. This includes all combinations of $0.01/$10,000/$1 billion, 0%/tiny/10%/100% rates and 1/12/60/600 months, with schedule and no-balloon invariants; both fee methods, ignored hidden invalid inputs, dates 0001/0099/9999, invalid field/range handling, cleared schedule and pie reconciliation are checked.
- Cash-flow subtraction at the largest numerical boundary is reconciled to half-cent tolerance; normal reference amounts/rates use tighter checks. Row displays still round individually and are not a lender's cent-rounded ledger.
- Independent 75-digit Decimal references: payment 212.470447112682744; interest 2748.226826760964668; fee-inclusive modeled cost rate 12.238801890827607%, or 14.288214484529072% with $10 monthly insurance. JavaScript also discounts every actual scheduled flow independently to verify the rate solver's annuity shortcut.
- Local Playwright at 1366/390/320 in America/Los_Angeles verifies paired-field alignment, first-screen Calculate, option hide/disable/exclude behavior, dollar/percent fee handling, upfront net cash, repayment labels and zero ending balance, insurance, invalid/Clear/recovery, nonblank/nonstretched pie pixels, overflow at the largest supported scenario, self-canonical and incoming contextual links. Analytics traffic is blocked for synthetic tests. Harness and screenshots remain ignored in doc-work; run `node doc-work/verify-personal-loan.cjs --live` after deployment.
- Full static gates retain 303 reachable sitemap URLs / 285 indexable calculator records, 286 app nodes, 297 breadcrumb trails and 1,165 breadcrumb targets. Builder validates 140,741 internal links. JS 6a2772753bfdab86 matches 4,903 script references; scoped CSS 8073685066d88447 matches 5,027 references.

This is a verified functional and helpful-content improvement, not proof of ranking, field CWV, traffic lift or the daily-1,000 objective. Its effect requires a future settled US observation window.

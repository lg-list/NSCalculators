# Boat Loan Purchase and Budget Upgrade

Date: October 26, 2026. Existing URL: `/boat-loan-calculator/`.

## Evidence and Scope

The unchanged September 24-October 21 US Web Search Console export records 294 page impressions, no clicks and position 90.27 for this URL. Its separate query table has `boat loan calculator` at 21 impressions and position 89.86. These are **not a verified query/page pair** and must not be joined. The original ZIP hash was rechecked; minimal independent observations are in `exports/us-boat-loan-observation-2026-10-26.json`. This supports reviewing a visible existing page, not claiming large market volume or moving it above Area. The owner agreed to upload a US Keyword Planner historical export; none has yet been received or used.

Production had only generic principal/rate/years/months fields. A negative $10,000 principal returned -$212.47 monthly, -$12,748.23 total payments and -$2,748.23 interest without an error. It did not distinguish a boat's purchase price from its financed amount or a loan installment from a recurring boating budget.

## Purpose-Built Functionality

- Existing route now uses `boat_loan_advanced`: boat price, down payment in dollars or percent, annual note rate, whole years/additional months and first payment month.
- Optional purchase-tax/fee fields hide, disable and are excluded when unchecked. Enter a quoted one-time dollar amount; either finance it once or pay it upfront. No state tax rule, cap, trade-in treatment or lender eligibility is inferred.
- Separate annual insurance, storage and other-operation reserves produce an average monthly budget and a reserve over the loan-term horizon. They do not increase principal, loan interest or the repayment pie. No invented default insurance/maintenance percentage.
- Compact principal/interest pie, purchase-cash and financing details, and a collapsible monthly repayment schedule preserve the existing theme/plugins and paired mobile inputs.
- Reuse the previously tested fixed-monthly-payment and stable remaining-payment-PV schedule through `personalLoanAmounts` with fees disabled; no second amortization algorithm. Fully cash-funded cases have no loan schedule, interest or pie; a financed fee can still create a loan on a fully cash-paid purchase price.
- Cash identities: purchase cash due = down + upfront costs; principal = price - down + financed costs; modeled cash = purchase cash due + loan payments + operating reserve = price + purchase costs + interest + operating reserve. No double-counted financed tax, down payment or principal.
- Strict finite/range validation and Clear remove stale schedules, summaries and charts. Principal is zero or $0.01-$1 billion; price $0.01-$1 billion; note rate 0%-100%; horizon 1-600 whole months; each annual reserve $0-$10 million. These are numerical boundaries, not available lending terms. A positive sub-cent principal is rejected rather than silently rounded.

## Content and Sources

Original copy explains purchase costs versus operating reserves, note rate versus disclosed APR, schedule timing, full-cash behavior and omitted resale/depreciation. Modeled cash is explicitly not economic ownership cost or an affordability/approval decision. Annual reserves are averaged, not bills asserted to arrive every month. Existing Loan and Amortization pages link contextually to the boat purchase workflow; the boat page links back to relevant repayment and fee-disbursement tools. Only Boat's title/description change to reflect its actual new functionality; stronger recently revised snippets stay stable. No new URL or indexation expansion.

Primary references reviewed: [Discover Boating loan tool](https://www.discoverboating.com/buying/boat-loan-calculator-old) for price/down-payment functional coverage, its [boat-buying guide and ownership worksheet](https://www.discoverboating.com/sites/default/files/2020-06/DBBoatBuyingGuide.pdf), and [CFPB interest-rate/APR distinction](https://www.consumerfinance.gov/ask-cfpb/what-is-the-difference-between-a-loan-interest-rate-and-the-apr-en-733/). No rates, tax advice, commercial recommendation or exact competitor parity is claimed.

## Verification

- Independent Decimal reference for $50,000 price / 20% down / 7.5% note rate / 120 months: payment 474.807076543416908; interest 16976.849185210029. Financing $3,000 produces principal $43,000 and payment 510.417607284173176. Paying it upfront instead yields cash due $13,000 with unchanged $40,000 principal. Annual reserves $1,200 + $2,400 + $600 add $350/month and $42,000 over 120 months.
- 194 dedicated JavaScript scenario groups pass, including numeric bounds, zero rate, cash purchase, percent/dollar equivalence, cost handling, dates, final balance, cash reconciliation, no balloon, invalid inputs and hidden-cost exclusion. All existing JavaScript suites pass.
- 105 Python tests pass, including two new route/content/link tests. The older personal-loan test now preserves the unchanged Business Loan model rather than asserting Boat must remain generic.
- Full isolated build validates 140,745 internal links. Scope remains 5,006 calculator records, 285 indexable calculators and 303 reachable sitemap URLs (maximum depth 3). Schema: 286 applications, 297 breadcrumb trails, 1,165 breadcrumb targets.
- Local Playwright at 1366/390/320 verifies first-screen Calculate; cost hide/disable/exclusion; dollar/percent down payment; financed/upfront accounting; separate operating reserve; month-only dates; 120/600-row schedules and zero ending balance; cash purchase; Clear; nonblank, nonstretched repayment pie; no page overflow or browser errors. Synthetic Analytics requests are blocked. Harness: ignored `doc-work/verify-boat-loan.cjs`, also accepts `--live`.
- JavaScript `46d5ad8adb634001` matches all 4,903 references; unchanged CSS `cd300833995da830` matches all 5,027 references.

Release completion still requires the resulting commit's GitHub Pages job and live three-width checks. No external submission, outreach, spending or account/security modification. No field CWV, traffic increase or 1,000-daily-visit achievement is established; compare settled US data later without confusing GSC clicks with GA4 organic sessions.

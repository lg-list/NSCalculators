# Cash rebate versus promotional rate: dedicated release

## Evidence and purpose

The existing `/cash-back-or-low-interest-calculator/` previously calculated simple interest on savings. The preceding readiness audit withheld that unrelated result. This release replaces it with a dedicated same-vehicle, same-term financing comparison and restores the existing URL, rather than creating another thin page.

Primary intent: **cash back or low interest calculator**. Related intents genuinely served: **car rebate vs low interest**, **cash rebate vs zero percent financing**, **auto incentive comparison**. These concepts belong in the page's useful comparison, not a visible keyword list. This quality repair does not establish US search volume: the supplied legacy keyword exports remain China-scoped, and recently deployed tools need a settled Search Console observation window.

## Reference and independent arithmetic

Rendered input inspection of https://www.calculator.net/cash-back-or-low-interest-calculator.html found a $1,000 rebate at 5%, a 2% alternative, $50,000 vehicle price, 60 months, $10,000 down, no trade-in, 7% sales tax, $2,000 fees and no fee financing. With those inputs, the new model reproduces displayed loan balances ($39,000/$40,000), monthly payments ($735.98/$701.11), taxes ($3,500 each), upfront cash ($15,500 each), total payments, interest and purchase costs ($59,658.69/$57,566.62).

A separate 50-digit Python Decimal check gives unrounded purchase costs of 59658.686726985582857225403535343537471840009762933 and 57566.624127786514332379721372305986953695966872654. The net saving is 2092.0625991990685, displayed as **$2,092.06**. Subtracting two already-rounded cost cells yields a different last cent; the page explains independent display rounding. Net saving is not the larger interest-only difference because accepting the lower rate forfeits the rebate. Lender payment rounding and final installments can differ from a full-precision planning model.

## Model and limits

- Compare separately amortized balances, monthly payments, total interest, tax, fees, actual cash down used, upfront cash, unused down-payment budget and economic purchase cost.
- Economic purchase cost includes trade-in value once: upfront cash + loan payments + trade-in value. It is not solely cash spent and is not a full cost-of-ownership model.
- Optional financing moves tax and fees into principal; otherwise they are paid upfront. Zero-rate and all-cash cases have explicit paths, with no negative loans or invented refund of excess trade credit.
- Tax can use entered rate and explicit rebate/trade taxable-price assumptions, or two quoted tax amounts. Quoted amounts replace the calculated tax. Inactive inputs are excluded from validation. No unverified state-law presets or automatic tax-rate lookup is presented; this is a deliberate difference from the reference's state selector. Quoted amounts can represent actual dealer tax treatment rather than a simplified nationwide rule.
- The model assumes immediate rebate, fixed note rates, level monthly payments, same vehicle price and term, and a debt-free trade-in. It rejects rebate plus trade value above price and does not model negative equity, later mailed rebates, differing vehicle prices/terms, introductory-only rates, early payoff, running costs or resale. These limits are visible.
- Terms accept whole months from 1 through 600 solely as a mathematical range, not a claim of product availability. Fees are an entered separate total; in calculated-tax mode they are not themselves taxed. Fee-inclusive APR should not be substituted for note rate while fees are separately entered.
- The CFPB comparison guide is linked in original explanatory copy: https://www.consumerfinance.gov/ask-cfpb/how-do-i-compare-auto-loan-offers-what-should-i-look-at-besides-the-monthly-payment-en-753/. No personalized financing recommendation or credit-eligibility claim is made.

## Discovery and verification

Move the calculator from the inappropriate Savings & Growth grouping into Loans. Restore search/category/sitemap inclusion only with the dedicated engine and tests. Add an explanatory link from Auto Loan; link back to Auto Loan and Trade-in for other financial intents. FHA remains withheld. Indexable scope becomes **284 calculators / 302 sitemap URLs / 2,456 search entries**. Existing direct URL, HTTPS canonical and calculator schema are tested.

43 Python regressions pass. The new CI suite covers 21 financial scenarios and 52 invalid cases, including default reference outputs, fixed-cost funding identities, financing, tax assumptions, quoted-tax replacement, zero rates, cash surplus, single-month loans and overflow. The prior 130 JavaScript numeric/validation cases still pass. The content-derived bundle gate checks 4,902 references against `04abb1501c07e08e`. Clear resets optional tax/trade/fees to zero, removes the primary inputs and stale output, and allows a new basic comparison without hidden blank-cost validation errors.

Desktop 1366px and mobile 390px/320px browser checks cover reference outputs, financing, tax controls and hiding, quoted amounts, stale-result removal, Clear, canonical/indexability/schema, search/category presence and no page or comparison-table overflow. At 844px viewport height, the default Calculate button is visible at all three widths. Mobile results show both offer columns without horizontal scrolling. Screenshots were reviewed before commit. Styles are scoped to this tool with asset version `20261021a`; no plugin replacement or unrelated theme redesign is made.

Full isolated build validates 140,682 internal links across 5,005 calculator routes. Tests validate functionality and technical discovery, not Google indexing, traffic gains or field Core Web Vitals. No external submission, outreach, spending or account change is made. Continue the 90-day plan; 1,000 daily organic visits remains unverified.

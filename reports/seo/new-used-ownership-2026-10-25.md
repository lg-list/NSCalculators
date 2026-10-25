# New Versus Used Ownership Comparison

Date: October 25, 2026

## Verified Intent Gap

Used the existing signed-in Search Console report, preserving September 24-October 21 and the United States filter. Replaced the previous exact query with `new vs used car calculator` and inspected the selected Pages breakdown. Visible totals: zero clicks, 35 impressions, query position 93.5. The sole visible page row is `/used-car-value-calculator/`, zero clicks and 35 impressions. This is a directly observed query/page pair, not an inferred join of exported query and page tables. It is historical site visibility, not monthly US market volume.

The existing current-value estimator is not an ownership-cost comparison. Preserve its distinct purpose and URL; do not turn an estimate of today's value into a new-versus-used buying recommendation. The new purpose-built `/new-vs-used-car-calculator/` addresses the observed comparison intent. Minimal aggregate evidence and keyword-to-target distinction are in `exports/us-ownership-comparison-opportunity-2026-10-25.json`.

## Delivered Functionality

Both vehicles share a whole-year holding period and annual mileage. Each has purchase price, assumed end resale, cash down, fixed annual note rate, whole-month term, quoted upfront tax/fees, US MPG, annual insurance and annual maintenance/repair budget. Fuel price is shared in dollars per US gallon. Initial values are illustrative assumptions, not market averages, offers or VIN-based estimates.

The model calculates fixed monthly payments with the existing numerically stable annuity expression, extracted into a shared helper also used by the rebate comparison. It accrues interest only through the holding period and retains the loan balance owed at sale. Cash purchases ignore inactive loan rate/term. Principal is not counted twice:

`cost = price - resale + interest paid + upfront tax/fees + operating costs`

Independently reconcile:

`cost = cash down + tax/fees + paid installments + operating costs - (resale - loan balance)`

Display the lower modeled cost, both cost totals, absolute difference, common driving distance, a same-currency two-bar comparison and a detailed two-vehicle table including cash paid, loan payoff, sale equity and reconciled net cash cost. Negative equity is not silently discarded. An appreciation assumption may create negative depreciation/cost; no guaranteed profit is implied. Zero-mile comparisons omit cost-per-mile instead of dividing by zero. Invalid/Clear states hide the chart and remove stale output.

The domain model deliberately excludes state tax lookup, financed fees, trade-in/negative-equity rollover, inflation, discounting, extra payments, balloon loans, variable rates and leases. Recurring registration, parking, tolls and sale expenses are also excluded. The worked example and limitations state these boundaries. A single selected end resale does not justify fabricating an annual resale line chart.

## Original Content and Discovery

Added a worked five-year zero-interest/cash example: new car $34,000, used car $32,900, difference $1,100. It includes the explicit fuel arithmetic and cost reconciliation. Describe assumptions, remaining debt, negative equity, cash purchase, appreciation risk, and why monthly payments alone do not establish the lower ownership cost.

Primary supporting consumer references: [CFPB vehicle affordability and cost guidance](https://www.consumerfinance.gov/ask-cfpb/how-much-can-i-afford-to-borrow-for-a-car-or-auto-loan-en-751/) and [FTC financing/leasing guidance](https://consumer.ftc.gov/articles/financing-or-leasing-car). They support reviewing overall purchase/ownership costs; no rates, prices, resale forecasts or personal recommendation were imported from them.

Added reciprocal context links from current Used Car Value, future Car Resale Value and Auto Loan; the comparison links back with clearly distinct purposes. Existing Automotive / Car Value directory and site search automatically include the one new tool. No menu-category expansion or current-value redirect. The new page has a specific title/description, self-canonical, free SoftwareApplication and breadcrumb data using the existing templates/theme.

This is one purpose-built tool, not a location/model/price doorway series. Reviewed indexable calculator scope intentionally increases from 284 to 285 and sitemap URLs from 302 to 303. Existing provenance and search-scope tests preserve their previous count baselines while accounting separately for this named, US-query-backed addition. No China volume is assigned; US monthly search volume remains unknown. No manual index or sitemap submission occurred.

## Verification

- 99 Python tests pass, including two new metadata/rendering/link tests.
- All existing JavaScript suites pass, including the existing rebate helper coverage. The new suite adds 172 scenario groups with cash-flow identities, all combinations of 1/2/5/10-year horizons and 1/12/60/120-month terms at zero/tiny/6%/100% rates, inactive cash inputs, malformed fields, range/overflow rejection, negative equity, appreciation and invalid rendering.
- Independent 45-digit Python Decimal references verify financed defaults: new payment $579.98404588283755 and cost $38,799.042752970253; used payment $405.52788576827365 and cost $37,231.673146096419. These are mathematical model outputs before lender rounding, not quotations. Pure cash and zero-interest examples reconcile exactly to $34,000 / $32,900.
- Local Playwright at 1366/390/320 checks first-screen Calculate, default financed output, published zero-interest example, sale shortfall, invalid/Clear cleanup, cash purchase with blank unused financing fields, zero mileage, nonblank chart pixels, overflow, schema and self-canonical. Category and three contextual incoming links resolve. Synthetic tests block Analytics requests. Harness/screenshots remain ignored in doc-work; `node doc-work/verify-new-used.cjs --live` supports post-deployment repetition.
- Full corpus gates: 303 eligible reachable sitemap URLs (within three clicks), 286 application nodes, 297 breadcrumb trails and 1,165 breadcrumb targets. Builder validates 140,737 internal links. JS c5053a7e8a896bcb matches 4,903 references; scoped CSS ef55cd1025d2846e matches 5,027 references. No existing category palette or plugins changed.

Track the new URL's indexing and exact comparison queries in a future settled US report. Do not attribute historical Used Car Value impressions to the new tool or treat the count as a traffic forecast. Current overall daily-1,000 goal remains unachieved.

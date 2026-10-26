# Shared Installment Reliability and HTTP Route Review

Date: October 26, 2026. Scope: the existing `loan` engine, not a new specialized lending product or keyword cluster.

## Evidence

Public production Playwright reproduction on Business Loan showed two failures: -$10,000 principal returned -$212.47/month and negative total payments/interest; a $10,000 principal at 0.000000000000001% for 60 months returned $0.00/month and $0.00 total. The latter used a power/subtraction expression that loses the small positive rate through floating-point cancellation. Its chart also added one monthly payment to whole-term principal and interest, inflating the displayed repayment breakdown.

Current dataset inspection identifies four live, indexable routes sharing this engine: Repayment, Student Loan, Business Loan and Home Equity Loan. Loan Payment is an existing redirect and FHA remains intentionally withheld with no calculator. The shared bug justifies correcting existing outputs without relying on a new search-volume claim. The promised US Keyword Planner export has not been received; stronger established Area opportunities remain the priority for later demand-led expansion.

## Changes

- Reuse the stable `fixedMonthlyPayment` helper (log1p/expm1) in one pure basic-installment function and both primary/secondary result paths. Zero/tiny positive rates approach principal divided by payments, not zero installments.
- Strictly validate finite principal $0.01-$1 billion, nominal annual rate 0%-100% and 1-600 whole monthly payments. These are numerical limits, not loan offers. No forced one-month fallback or negative-principal answer. Preserve fractional years when they represent a whole combined monthly term, including 5.5 years = 66 months and one-third year = four months; extra months must be whole 0-11.
- Clear invalid summaries/chart data and recompute validation after Clear. The repayment pie contains principal plus full-term interest only; the monthly installment is not a third repayment slice.
- Label the input basis as annual note rate rather than representing a fee-free model as a disclosed APR. Extremely small positive rates use scientific notation in the detail table rather than a false 0% label. The visible introduction now matches the nominal-rate model.
- Add explicit existing-page scope: Student Loan does not implement income-driven plans, forgiveness or eligibility; Business Loan omits SBA fees, factor rates, revolving draws and balloons; Home Equity is not a HELOC; Repayment solves payment from term, not payoff time from a chosen payment. Original examples explain zero-rate behavior, rounding and chart accounting. [CFPB's rate/APR explanation](https://www.consumerfinance.gov/ask-cfpb/what-is-the-difference-between-a-loan-interest-rate-and-the-apr-en-733/) supports the conceptual distinction, not a certification of the tool.

No theme, plugins, CSS, titles, canonicals, indexing policy or new URL changed. These four basic fixed-payment estimates are not certified as complete specialized student, business or home-equity lending workflows. FHA stays unavailable/noindex; the retired Loan Payment alias is not restored.

## Verification

- All 107 Python tests and all JavaScript suites pass. The new JavaScript suite has 106 numeric, direct-month/year-term, validation and rendered-breakdown scenario groups; two new Python methods cover all four pages' scope and the withheld/redirect invariants.
- Reference $10,000 / 10% / 60 months: $212.470447112682744 monthly, $2,748.226826760964668 interest. Tiny positive and zero rates produce about $166.67 monthly and preserve the $10,000 repayment, before display rounding.
- Local Playwright: four pages x 1366/390/320 = 12 page/viewport combinations. Verified first-screen Calculate, positive default, negative rejection, tiny positive rate, 5.5-year term, fractional-month rejection, Clear/re-entry, nonblank chart pixels, nonstretched pies, canonical consistency and no overflow/browser errors. FHA remains noindex with no active calculator. Synthetic Analytics requests are blocked. Ignored harness `doc-work/verify-basic-installment.cjs` supports `--live` for post-deploy verification.
- Full isolated build: 5,006 calculator records, 285 indexable calculator records, 303 sitemap URLs, maximum crawl depth 3, 140,745 validated internal links. Schema checks 286 applications / 297 breadcrumb trails / 1,165 targets.
- JavaScript `e8bc7b286425a895` matches 4,903 script references; unchanged stylesheet `cd300833995da830` matches 5,027 references.

## HTTP Review: No Unnecessary Routing Changes

Public Playwright request context, redirects disabled, no Googlebot impersonation or authenticated account traffic:

| Request | HTTP result | Signal |
| --- | --- | --- |
| `/seo-route-check-not-a-calculator/` | 404 | Custom not-found document; noindex,follow |
| `/automotive-calculators/seo-route-check-not-a-calculator/` | 404 | Same custom not-found document; noindex,follow |
| `/404.html` | 200 | Direct error-document asset is noindex; not evidence of a soft 404 for missing routes |
| `https://www.nscalculators.com/area-calculator/` | 301 | Location is canonical HTTPS apex Area URL |
| `http://nscalculators.com/area-calculator/` | 301 | Location is canonical HTTPS apex Area URL |
| `/area-calculator/index.html` | 200 | Canonical points to `/area-calculator/` |

These are bounded spot checks, not a full HTTP crawl or proof of Google's current selected canonical. Existing static meta-refresh aliases are not misrepresented as server-side 301s. No DNS, CDN/security, robots or domain change was warranted or made.

Deployment completion requires the resulting commit's Pages job and live checks. This is a verified trust/functionality improvement, not evidence of ranking lift, field Core Web Vitals, new US market volume or achievement of the daily-1,000 aspiration. No spending, outreach or external submission.

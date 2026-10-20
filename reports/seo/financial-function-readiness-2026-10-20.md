# Financial calculator readiness review

## Verified problem

Live Playwright inspection on 2026-10-20 confirmed three calculator titles did not match the functions actually delivered. These findings are based on rendered fields and results, not just source-engine labels.

| Existing URL | Rendered functionality before correction | Missing purpose-built behavior |
| --- | --- | --- |
| `/down-payment-calculator/` | Loan amount, APR, years, extra months; default $212.47 monthly installment | Purchase cash, down payment and closing-cost calculation |
| `/fha-loan-calculator/` | Same generic installment calculation and $212.47 default | FHA-specific upfront and ongoing mortgage-insurance model |
| `/cash-back-or-low-interest-calculator/` | Principal, annual rate and years; $1,500 simple interest on $10,000 | Rebate versus promotional APR offer comparison |

The formulas may calculate generic loan or savings results, but those results do not answer the named financial questions. A larger content block or schema change would not fix the missing functionality.

## Correction

- Withhold these three routes from indexation, category discovery, recommendations and site search until a dedicated implementation is tested. Do not redirect them to a different-intent calculator or imply the alternatives are equivalent.
- Preserve direct URLs with HTTP 200, self-canonical, `noindex,follow`, an accurate availability explanation and links to working alternatives with explicit limitations. Do not block crawling in robots.txt: Google needs to read the noindex directive.
- Remove unrelated calculation forms, results, calculator JavaScript and SoftwareApplication claims from these pages.
- Replace the affordability article's recommendation of the unfinished down-payment tool with guidance about its existing cash-only ceiling.
- Keep working mortgage, auto-loan and affordability tools indexable. The three route exclusions are title/function quality decisions, not an inference from unknown US keyword volume.

This is a containment fix, not a claim that the three dedicated calculators have been completed. Restore each only after validating its actual financial model, inputs, limits, examples and regression tests. Previously indexed copies can remain in Search Console until Google recrawls; no immediate removal or ranking benefit is guaranteed. No external indexing or sitemap submission was performed.

## Verification

- 40 Python regression tests pass, including explicit readiness exclusions, disclosure text, alternatives, no calculator markup, and the affordability link correction.
- All existing shared-JavaScript numeric suites pass: 24 duration cases, 26 employer-match cases and 26 vehicle-sale comparison cases. The calculation bundle is unchanged (`5188429e167fa7a0`).
- Full isolated build: 5,005 calculator routes, 282 indexable calculators, 300 sitemap URLs, 2,454 search entries and 140,674 validated internal links. The asset gate verified 4,900 calculator script references against the shared bundle.
- Local Playwright at 1366px and 320px checks availability, canonical/noindex, removal of forms/script/schema, working alternatives, no page overflow and no browser errors. Checks also cover financial category exclusions, sitemap/search exclusions and retained working tools. Mobile screenshots reviewed before commit.

Reproduction: `python -m unittest discover -s scripts -p 'test_*.py' -q`; use the existing isolated-build procedure rather than staging generated `dist/` output. The task browser verifier is `doc-work/verify-financial-readiness.cjs` (ignored working evidence) and supports `--live` for post-deployment checks.

# Concrete Volume, Product Yield and Validation

Date: October 26, 2026. Existing URL: `/concrete-volume-calculator/`.

## Evidence and Priority

The archived US Trends review in `exports/us-construction-trends-2026-10-26.json` put the quoted concrete phrase highest among four compared terms and exposed associated 80-lb bag queries. Those normalized indexes and Rising percentages are not monthly search counts, organic difficulty or a predicted traffic gain. Area retains the separate near-page-one GSC observation priority. The promised US Keyword Planner CSV remains unreceived.

Live public Playwright reproduction found negative slab length becoming a zero-volume answer, 2.5 post holes silently calculated as two, and a chart mixing cubic-foot volumes with dollar costs. The existing 80-lb preset was correct for the named product; it was not evidence that every same-weight mix has that yield.

## Changes

- Strict, pure `concreteAmounts` validates finite positive active dimensions, whole round-project quantity (1-1 million), entered allowance (0%-100%), product yield and optional prices. Inactive slab/round/custom controls hide and disable; their invalid values are excluded. Estimates exceeding a billion bags or finite numerical range are rejected, not clamped to apparently valid zero.
- US dimension mode uses ft/in and metric uses m/mm. An explicit unit change converts both active and inactive dimension values, preserving geometry. Input/change ordering is covered in a real browser. Yield units and dollar price bases are separate from dimension units; ready-mix pricing remains dollars per cubic yard.
- Keep product-specific QUIKRETE No. 1101 examples and add its listed 50/90-lb variants. A custom product-label yield accepts ft3, liters or m3 per bag, without deriving volume from dry weight. The [manufacturer sheet](https://www.quikrete.com/pdfs/data_sheet-concrete%20mix%201101.pdf), reviewed October 26, is marked Revised October 2022; this is not a claim of a newly revised 2026 product specification, universal yields or brand affiliation.
- Apply the allowance to unrounded volume and round final bag quantity up once. A machine-scale near-integer correction prevents an extra bag due solely to arithmetic noise; a real positive excess in regression tests still requires another bag. Purchased coverage and packaging excess are separate from the entered allowance.
- Blank optional prices remain unknown/not entered; an explicit zero remains a zero-price scenario. Negative/nonfinite prices are invalid. Cost estimates exclude delivery, tax, labor and supplier-specific charges; no current prices or quote are claimed.
- Chart contains measured volume and added allowance only, both ft3. Costs stay in the table. Invalid input and Clear remove stale cards/chart data; tiny supported positive volumes use scientific notation rather than a false zero.
- Add original one-yard/whole-bag, custom-label, unit-equivalence and cylinder examples; retain material-only and gross-hole-volume limitations. No post/pipe/gravel displacement, mix design, structural thickness/strength or native-app capability is implied. Metadata now describes actual 80-lb/custom-yield and volume support; title and canonical stay unchanged.
- Browser QA caught large-cost overflow at 390px; scoped min-width/wrapping to concrete summary values only. Existing theme, font sizes and plugins are preserved. No new URLs or weight-specific doorway pages.

## Verification

- 109 Python tests pass, including two new existing-route/content/alias checks. All JavaScript suites pass; the new concrete suite has 170 scenario groups covering all three shapes, both dimension systems, all presets/custom yields, three allowances, derived-volume invariants, full-bag boundaries, invalid/hidden inputs, optional prices, overflow/underflow and DOM rendering.
- Independent formula references: default 20 x 10 ft x 4 in is 200/3 ft3; with 10% allowance it is 220/3 ft3 = 220/81 yd3. The 0.60 ft3 example needs 123 bags at $6.25 = $768.75. One yd3 needs 45 such bags before allowance and 50 with 10%. A separately entered 0.50 ft3 yield needs 54 bags for one yd3. Equivalent liter/m3 custom inputs return the same counts.
- Four 12-inch-diameter, 4-foot-high full cylinders total 4*pi ft3 before allowance. No displacement is subtracted; 2.5 cylinders is invalid.
- Local Playwright at 1366/390/320: first-screen Calculate, real unit round trip, negative dimensions, fractional quantity, hidden input isolation, default/one-yard bag examples, custom ft3/liter/m3 yields, blank versus zero prices, invalid/Clear recovery, nonblank volume-only chart, no overflow including large cost output, self-canonical and no browser errors. Analytics requests are blocked in synthetic QA. Ignored harness `doc-work/verify-concrete.cjs` also supports `--live`.
- Isolated full build validates 140,745 internal links; 5,006 calculator records, 285 indexable calculator records and 303 sitemap URLs remain. Depth <=3; schema checks 286 applications / 297 breadcrumb trails / 1,165 targets. Script fingerprint `f761017e92bcf8d7` matches 4,903 references; scoped stylesheet `066d4625bf637de9` matches 5,027 references.

Deployment completion requires the resulting commit's Pages job and live three-width verification. No Search Console submission, outreach, spending, account/security change or traffic outcome. Do not equate these tests with field Core Web Vitals, full reference-site parity, structural suitability or the daily-1,000 goal. Next evaluate settled US GSC/GA4 data without changing the observation window or substituting impressions for visits.

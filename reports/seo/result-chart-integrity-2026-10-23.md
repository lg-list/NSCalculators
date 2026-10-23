# Result Chart Integrity

Date: 2026-10-23

## Observed Production Errors

Playwright captured these canvas labels before editing:

- Percent: `20% of 150 = 30`, but its chart labeled 150 as 50%, 30 as 10%, and 120 as 40% by dividing each value by their sum. This double-counted the whole and did not represent the requested percentage.
- Fraction: 1/2 + 1/3 = 5/6 was accompanied by fabricated 30%, 20%, and 50% shares.
- Sales tax: $100 + $8.25 = $108.25 appeared as 46.2%, 3.8%, and 50% of a double-counted total.
- Calorie: a generic dollar pie combined BMR, daily calories, and protein grams into `$4,118.72 total`. Neither the currency nor that sum was meaningful.

These are result-presentation defects, not evidence of keyword demand. The original supplied keyword files are China-scoped, and fresh US Search Console exports remain unavailable. No title or keyword-priority change is justified by this audit.

## Changes

Shared comparison bars now display the actual values without automatically manufacturing percentages. Negative values extend left from a common zero baseline, zero has zero bar length, nonfinite values are omitted, and up to six rows fit the declared chart height. Scaling handles very large finite signed values without overflowing the numeric range.

Bars redraw at container width and device pixel ratio, with 16px labels above each bar rather than shrinking an entire 620px bitmap on phones. Long labels are ellipsized and long values fit their reserved region; full details remain available in summary cards and tables. Resize handling updates the comparison view without recording a calculator-submit event.

Eight pages using the existing calorie/body-metric engines now receive explicit comparison bars: calories compare only kcal/day; weight references compare only pounds. Protein and BMI remain separate summary metrics, not slices or mixed-unit bars. This does not certify those legacy engines as complete nutrition tools or medical advice.

Percentage modes no longer plot a percentage beside raw quantities on the same scale; decreases retain their signed change. Fraction arithmetic retains a value comparison, while simplification and decimal conversion keep answers and steps without comparing numerator counts, denominators, and the fraction's value. Undefined percentage/fraction results hide the chart and restore it after valid input. Removed the renderer's fabricated `Ready = 1` chart fallback. Dedicated mortgage and body-composition pies are preserved.

## Verification and Scope

- 52 Python tests pass, including two chart-selection regressions.
- 25 new JavaScript chart/engine checks pass: 11 geometry, labels and pixel-ratio checks; eight percentage cases; four fraction cases; two matching-unit cases. All 256 prior calculation/validation/chart checks also pass.
- Full isolated build retains 5,005 calculator routes, 284 indexable calculators, 302 sitemap URLs and 140,684 validated internal links.
- Asset guard checks 4,902 script references against `6b859aca9eb254b1`. CSS remains unchanged (`c6dea991aa920bec`).
- Playwright checks nine pages at 1366, 390 and 320px with 2x pixel ratio: output checks, chart pixels, no overflow or browser errors, valid/undefined transitions, fraction mode transitions, and no fabricated bar percentages. Reviewed the updated mobile calorie, negative-change and tax screenshots.

Other generic fallback charts and legacy calculator-purpose mismatches require their own reviews; this is not a claim that every chart or calculator on the site is now correct. Calculation formulas, indexation, canonical targets, sitemap scope and theme are unchanged. No external submission, paid service, account change or medical-review claim was made. Search impact requires later settled US data.

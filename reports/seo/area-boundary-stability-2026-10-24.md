# Area Boundary and Numerical Stability

Date: 2026-10-24. Priority: the existing Area Calculator, not a new competing URL. The US September 24-October 21 report has 590 impressions for `area calculator`; this historical window cannot measure this release.

## Reproduced Production Defects

Before deploying the fix, public Playwright reproduced both cases on the current live site:

| Input | Previous output | Corrected output |
| --- | --- | --- |
| Sector, radius 6 ft, angle 360 degrees | Area 113.0973355292 sq ft; perimeter 49.69911184 ft | Same area; full-disk boundary 37.69911184 ft |
| Three sides 100,000,000 ft, 100,000,000 ft, 0.00000001 ft | Unable to calculate; dimensions too large or small | Area 0.5 sq ft |

The full disk has no radial cut boundary. For a proper sector below 360 degrees, the boundary still includes both radii plus the arc. A disk physically slit along a radius would be a different model. No near-360 rounding threshold was added: 359.999999 degrees remains a proper sector.

The thin triangle is an intentionally extreme numerical regression, not a claim that field measurements can achieve that precision. The previous direct semiperimeter product rounded away the very short side. Large and small equilateral triangles also lost otherwise representable areas because the fourth-order intermediate product overflowed or underflowed.

## Change

- Corrected the 360-degree boundary and explicitly labels that result as a full circle.
- Used sorted, parenthesized Kahan factors for the three-side area, pairing their square roots before multiplying. This retains representable area in the tested thin/large/small cases without first computing the fourth-order product. Invalid or degenerate triangles remain rejected; this is not arbitrary-precision arithmetic or an exhaustive error guarantee.
- Made the existing geometry projection readable within its ownership boundary, rejected unsupported shapes, and required finite positive dimensions before computing.
- Added short original explanations of full-disk versus cut-sector boundaries and numerical precision, with a primary numerical-analysis reference. Kept titles, descriptions, theme, shapes, unit choices and room-total controls unchanged.

References: [William Kahan's numerical-analysis notes, section 2](https://people.eecs.berkeley.edu/~wkahan/Triangle.pdf) provide the stable parenthesized Heron rearrangement. [OpenStax's angles chapter](https://openstax.org/books/precalculus-2e/pages/5-1-angles) describes a full 360-degree rotation and coincident initial/terminal rays. The disk-versus-slit boundary distinction is stated explicitly in the calculator's model.

## Verification

- 64 new JavaScript checks: circle/360-sector agreement in seven input units, proper-sector angles, side permutations, equilateral scales, thin and nearly flat triangles, nonfinite/invalid sides, invalid angles and unsupported shapes. Included in CI.
- All 76 Python tests and 708 JavaScript checks pass, including the existing nine shape modes and area-total reconciliation tests.
- Playwright at 1366, 390 and 320 pixels: default 240 sq ft, full disk, quarter circle, thin triangle and degenerate triangle. No page errors or horizontal overflow. Inspected the 390-pixel screenshot.
- Re-ran the additive/subtractive room workflow at all three widths: mixed-unit totals, removals, zero, invalid deductions, overflow and Clear still pass.
- Isolated build: 5,005 calculator routes, 284 indexable calculators; 302 URLs pass the indexation/crawl-path gate; 140,686 internal links validate. 4,902 script references use content version `f0351f14f83d6e27`. CSS is unchanged.

No growth outcome, ranking lift or Google recrawl is claimed. No sitemap/indexing submissions, account changes, payment, outreach or new pages were made.

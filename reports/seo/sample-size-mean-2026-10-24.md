# Sample Size: Mean Planning on the Existing URL

## Evidence and Decision

The previous goal turn was progress: formatter reuse was committed, deployed and verified across 48 production states. This continuation returns to a functional content gap rather than another cosmetic change.

Read-only US query export screening identified `sample size calculator standard deviation`. Verified the exact query in the signed-in Search Console UI, United States / Web, September 24-October 21: five impressions, zero clicks, query average position 72.8. The selected Pages tab showed only `/sample-size-calculator/` with five impressions and zero clicks. Added this observed pair to the existing JSON observation record; no separate query/page exports were joined.

This is a weak historical visibility signal, not US market volume or a near-page-one win. The query is ambiguous: using SD to plan a mean estimate and planning precision for SD itself are different tasks. The old page explicitly supported proportions only. Add the common mean-planning use case to the existing URL and explain its limits; do not claim to satisfy every SD-related search or create a thin alternate URL. Area remains the larger measured opportunity.

## Implementation

- Default proportion model preserved: 95%, margin five percentage points, expected proportion 50%, unknown population -> 385 completed responses; finite population 1,000 -> 278.
- Added a target selector and a population-mean model using `n0 = (z x SD / absolute error)^2`, rounded up to at least one observation. Fixed two-sided z values remain 1.645 / 1.96 / 2.576. Inputs and output units distinguish absolute error from percentage points.
- Mean mode assumes independent random observations with a known or explicitly assumed planning SD and an appropriate normal approximation. It deliberately does not apply the proportion-specific population correction. Pilot-SD uncertainty, no iterative t planning, no hypothesis-test power calculation and no precision calculation for SD itself are stated in the article and results.
- Active-model-only validation ignores hidden unused inputs. Rejects nonpositive/nonfinite SD or error, unsafe counts, blank required inputs, and derived overflow/underflow. Clear removes stale result cards/chart, and mode switching restores the applicable fields. Mean mode does not invent a comparison chart when there is no second quantity to compare.
- Original worked examples, primary references, reciprocal contextual links with Standard Deviation, and a description reflecting both supported targets. Existing title, canonical, theme, plugins and indexable URL scope remain unchanged.

## Sources and Independent Checks

[NIST sample-size selection](https://www.itl.nist.gov/div898/handbook/ppc/section3/ppc333.htm) covers absolute-error planning for a mean. [OpenStax's known-SD mean interval](https://openstax.org/books/introductory-statistics/pages/8-1-a-single-population-mean-using-the-normal-distribution) explains the normal model. These are assumptions, not a study-validity certification.

Independent decimal arithmetic at z = 1.96:

| SD | Absolute error | Unrounded n0 | Rounded observations |
| ---: | ---: | ---: | ---: |
| 20 | 10 | 15.3664 | 16 |
| 25 | 5 | 96.0400 | 97 |
| 12 | 2 | 138.2976 | 139 |

## Verification

69 new JavaScript checks cover both models, confidence choices, unit scaling, invalid inputs, active-model isolation, small/large limits and stale-output cleanup. Added one Python page-content/index-scope regression and the JavaScript suite to CI. All 83 Python and 1,674 JavaScript checks pass locally, including the existing analytics checks.

Playwright at 1366/390/320px checks default and finite-population outputs, the two mean examples, mode-specific field visibility, chart hiding, Clear/recovery, first-screen Calculate, valid metadata/JSON-LD, contextual links, no horizontal overflow and no JavaScript errors. Synthetic tests block Analytics collection; screenshots were inspected.

Build: 5,005 calculator routes, 284 indexable calculators, 302 sitemap URLs and 140,689 validated internal links. Canonical/indexation/crawl-path and asset-version gates pass. No new page, submission, outreach, spending or account modification occurred. Deployment/live verification follows push and is not inferred from these local checks. No traffic or ranking lift is measured; the 1,000-daily-organic-visit goal remains unachieved.

# Body Fat Calculator: title/function correction

## Verified issue and scope

Live rendered inspection found `/body-fat-calculator/` returning **25.1 BMI** and a BMI reference weight range from a generic height/weight engine. It did not calculate body fat percentage. Source review confirmed the page was indexable with `cn_body_metric`. BMI is not a percentage, so a description or metadata tweak alone would not fix the mismatch.

Replace that engine on the existing URL with a dedicated adult estimate. This is a functionality and health-content accuracy repair, not a new landing page or evidence of US keyword volume. Do not reuse old China-scoped keyword volumes or fabricate new Search Console metrics while the documented reader access limitation persists.

Primary intent: **body fat calculator**. Related intents genuinely served include **body fat percentage calculator**, **Navy body fat estimate**, **BMI-based body fat estimate**, and **fat-free mass estimate**. Use these naturally in useful headings, controls and explanations, not visible keyword lists or unsupported traffic forecasts.

## Model and evidence

- Historical circumference equations use inches internally, for both US and metric input. They are documented in the Naval Postgraduate School's 2022 research report, printed page 17 / PDF page 33: https://dair.nps.edu/bitstream/123456789/4724/3/NPS-HR-22-210.pdf. That report is a historical research source, not current official Navy policy or an endorsement. Unlike the reference's separate metric density approximation, this implementation converts metric quantities into the same inch-based model to preserve unit equivalence; full reference parity is not claimed.
- A separately labeled adult BMI-based prediction follows Deurenberg et al., DOI https://doi.org/10.1079/BJN19910073. The tool limits age to 18-83 and does not extrapolate its BMI prediction outside the sampled 13.9-40.9 range. A cross-check outside that scope is marked unavailable rather than zero or confirmation of the other method.
- CDC's BMI explanation supports the distinction between BMI and body fat: https://www.cdc.gov/bmi/about/index.html. The page does not diagnose a condition or imply that either equation directly measures composition.
- Fat mass is entered weight times the selected estimated fraction; fat-free mass is the remainder, not measured muscle mass. Neither equation is averaged into the other.
- Reference inspection at https://www.calculator.net/body-fat-calculator.html found male default age 25, weight 152 lb, height 70.5 in, neck 19.5 in and abdomen 37.5 in. The new outputs reproduce rounded reference estimates: 15.3% circumference, 23.2 lb estimated fat, 128.8 lb fat-free mass and 15.4% BMI-based prediction. Independent Python calculations give 15.27697422074079% and 15.351497173418373%, respectively.
- Sex selection identifies the published equation coefficient, not gender identity or an individualized recommendation. No clinical review, ideal-fat prescription, automatic weight-loss target, fitness classification or military certification is claimed. This release deliberately does not reproduce such targets/categories from competitor prose.

## Interface and implementation

Keep the site's existing theme and input/results split. Provide two methods and US/metric measurements, converting entered quantities on unit change rather than reinterpreting an inch value as centimeters. Hip is active only for the female circumference equation; all tape inputs are inactive in BMI-only mode. Invalid measurements, unsupported ages, nonpositive logarithm arguments and out-of-range estimates return clear errors rather than clamped percentages.

The compact composition donut uses an explicit percentage format and a text alternative, not dollar amounts or a per-month caption inherited from financial tools. The shared pie function retains its default currency behavior unless the canvas requests percent formatting. Invalid input and Clear hide the chart and remove stale summaries. Source links, formulas, measurement sites, population limits, an example and FAQs are original page content. Add a contextual BMI-to-body-fat link while explaining that these are different questions.

## Verification and boundaries

- 45 Python tests, including dedicated engine, source/limitation markup, indexability and contextual linking checks.
- 12 numeric scenarios, 39 invalid-input cases and two chart-format regressions in the new CI suite. Both coefficients, method selection, equivalent units, ignored hidden fields, mass conservation, population limits and preserved financial currency charts are covered. All 203 prior JavaScript numeric/validation cases still pass.
- Full isolated build: 5,005 calculator routes, 284 indexable calculators, 302 sitemap URLs and 140,684 validated internal links. Index scope is unchanged. The shared asset hash is `17afe927c787b8e5`, checked across 4,902 script references; scoped stylesheet version is `20261023a`.
- Desktop 1366px and mobile 390px/320px Playwright checks verify both formulas, automatic unit round-trips, hidden inputs, validation, Clear, metadata/schema, search/sitemap inclusion, reciprocal linking and no page/table overflow. Canvas-pixel and aspect-ratio checks confirm a nonblank, undistorted chart; captured chart labels contain percentages and no dollars/monthly caption. Default Calculate fits inside 844px viewport height. Screenshots reviewed before commit.

These tests establish implementation behavior, not clinical validity for an individual, a medical endorsement, Google rankings, indexing gains or field Core Web Vitals. The broader Health directory is not certified by this narrow audit: Ideal Weight and Protein were inspected but need their own purpose/content review before any claim of reference parity. The 90-day traffic objective remains active and unverified; no external submission, spending or account change was made.

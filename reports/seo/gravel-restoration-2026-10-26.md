# Existing Gravel Calculator Restoration

Date: October 26, 2026. Route: `/gravel-calculator/`.

## Evidence and release decision

The preceding landscape audit confirmed this existing page had no calculator inputs, an unavailable message and intentional noindex. A dated publisher-labeled US Gravel estimate is a lead, not independently verified Keyword Planner data. Current comparative Trends data is unavailable and named US GSC export rows did not observe this intent; neither absence nor third-party estimates establish traffic upside. See `exports/us-landscape-opportunities-2026-10-26.json` for separated provenance. The reason to restore this route is a distinct, verifiable quantity-estimation task now implemented with useful original explanation, not merely an increase in indexed URL count.

This release completes the brief's functional/content/local release gates and deliberately restores one existing route to indexability, site search, its Construction category and the sitemap. It creates no new URL. Mulch and other unfinished tools stay unavailable/noindex. Existing index-scope and search-baseline tests now explicitly exclude only the two reviewed additions (ownership comparison and Gravel) while retaining the original baseline counts; unrelated CN metrics still cannot enlarge scope unnoticed.

## Functionality

- Rectangle dimensions or a separately measured area plus loose layer depth. Inactive dimension/area controls hide, disable and are excluded. US feet/inches and metric meters/centimeters convert active and inactive values on unit changes; duplicated input/change events do not double-convert. No GPS, address lookup or map measurement.
- Positive finite dimensions, area and depth; a finite entered 0%-100% volume allowance. Numerical over/underflow and unsupported final quantities are rejected rather than clamped. Allowance is added to base loose volume once, not treated as a universal compaction rate.
- Default 20 x 10 ft x 3 in = 50 ft³ = 50/27 yd³. With an entered 10% allowance: 55 ft³ and 55/27 yd³. No rounding feeds subsequent weight/cost arithmetic.
- Optional supplier density in lb/ft³, US short tons/yd³ or kg/m³. Blank means unknown, zero/negative density is invalid. No national pea-gravel, crushed-stone or driveway-density preset. The illustrative 100 lb/ft³ yields 5,500 lb / 2.75 US short tons for 55 ft³; metric mass is separately 2,494.758035 kg / 2.494758035 tonnes. Density must match the loose/as-supplied volume state.
- Optional dollar quotes per yd³, m³, US short ton or metric tonne. Blank prices remain unknown, explicit zero remains zero and weight-based prices require density. At 55 ft³, $50/yd³ gives $101.85 after display rounding; with the illustrative density, $40/US short ton gives $110. These are independent entered quote scenarios, not retail prices or a cost comparison with delivery included.
- Clear/invalid edits replace stale cards/table/chart; valid edits recover without reload. Enter submits through the existing scoped handler. The chart contains only base and allowance volumes in ft³; all equivalent volume/mass/cost fields are labeled in the details table. Supported tiny/large numbers use scientific notation and scoped card wrapping prevents overflow.
- Existing theme/fonts/plugins retained. Mobile options stack for readable density/price units; short mode labels and a concise page intro preserve first-screen Calculate. No runtime dependency added beyond the existing shared bundle; the prior production minification pipeline applies.

## Helpful content and primary sources

Original explanation distinguishes volume versus mass, US short tons (2,000 lb) versus metric tonnes (1,000 kg), loose versus compacted layers, and added allowance versus percentage volume loss. Adding 25% is not the same as dividing by 0.75 to replace a 25% volume reduction. No grade, layer depth, compaction method, road design, bag count, truck capacity or structural adequacy is prescribed. Costs exclude delivery, tax, labor, minimum orders and supplier rounding.

[Penn State DGLVR guidance](https://dirtandgravel.psu.edu/general-resources/dglvr-materials-calculator/) was read in the preceding audit: it distinguishes loose/compacted input states, loose output and supplier/regional conversion differences; a repeat open timed out this turn, so no newly retrieved specification or preset is claimed. [NIST's factors](https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b9) document short-ton and other mass-unit conversions; its [packaged-goods handbook](https://www.nist.gov/system/files/documents/2017/05/09/h133-16-final2.pdf) gives the cubic-foot/cubic-yard SI factors. [Vulcan's calculator overview](https://www.vulcanmaterials.com/construction-materials/product-calculators) supports supplier review of quantity estimates. No source affiliation or nationwide conversion factor is implied.

The restored page links to existing Square Footage/Area for measured shapes, while Square Footage and Concrete link contextually back to Gravel. Metadata targets gravel calculator / cubic yards / US tons / material cost; secondary pea-gravel and driveway intents are served as entered-product geometry, not fabricated recommendations or clone pages. App schema remains the site's existing UtilitiesApplication structure with no invented rating/review.

## Validation

- 113 Python tests pass, including two new Gravel content/discovery/metadata/schema checks. All JavaScript suites pass against the optimized deployment asset, including 231 new gravel groups: 144 mode/unit/allowance/density/price combinations, independent example outputs, missing/zero data, numeric limits, inactive fields, unit round trips and result rendering.
- Isolated full build validates 140,766 internal links; schema/indexation gates pass with 286 indexable calculators, 304 sitemap URLs, maximum depth 3, 287 apps, 298 breadcrumb trails and 1,169 breadcrumb targets.
- Build-time optimizer reduces this release's readable bundle from 547,819 to 465,533 bytes; optimized content hash `2ddc648f724cffa4` verified across 4,904 references. CSS `f2734abdc1120215` verified across 5,027 references. These are payload/build observations, not field CWV claims. Local tracked `dist/` remains untouched.
- Local Playwright at 1366, 390 and 320px verifies first-screen Calculate, unit conversions including after Clear, invalid/hidden fields, all three density units, weight/volume price bases, blank/zero values, chart pixels, Enter, Clear recovery, extreme-value wrapping and canonical/app metadata. Search finds Gravel once and opens the working tool; Construction links to it; sitemap has Gravel but not Mulch. Reviewed default, chart and open-options mobile screenshots. Ignored `doc-work/verify-gravel.cjs` supports `--live` for deployment checks.

No Search Console indexing request or sitemap submission, account change, spend or outreach. Indexability and a submitted sitemap do not prove Google has recrawled/indexed this release. Monitor settled US impressions/queries after deployment; the 1,000 daily-visit goal remains unverified and unachieved.

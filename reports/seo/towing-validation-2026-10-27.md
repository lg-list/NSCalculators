# Towing calculator: trustworthy limits and compact controls

## Priority and evidence

The existing towing page had **105 US impressions, 0 clicks and position 76.47** in the verified September 24–October 21, 2026 Search Console export. The separate query table included `towing calculator` (22 impressions), `towing capacity calculator` (19) and `estimated towing capacity` (16). These are incomplete, separate aggregates, not query/page pairs or monthly market volumes. The record's historical Keyword Planner figure is China-targeted and was not used as US demand evidence.

Provenance: `exports/us-search-baseline-2026-10-24.json`, source archive `nscalculators.com-Performance-on-Search-2026-10-24.zip`, SHA-256 `c5a2ec4c2e7132624cf60b78d7cbbe5aa7e08af221d3765e25129a59dd4b791e`.

Public Playwright inspection on October 27 reproduced valid-looking towing answers after negative or blank occupant weight. Clear left the previous 10,000 lb dashboard visible. The existing generic dashboard also drew independent trailer-weight ceilings as pie slices, implying they were parts of a meaningful total. These are product-quality problems worth fixing before claiming ranking gains.

## What changed

- Add a pure, bounded projection with explicit validation of every required weight and percentage. Blank inputs are not treated as zero; an invalid optional hitch rating is not silently ignored. Zero tow/hitch ratings remain meaningful zero-capacity constraints.
- Keep an unknown optional vertical hitch rating distinct from an entered zero. The result explicitly states when this rating is unchecked. No VIN lookup, manufacturer-rating verification or towing certification is performed.
- Compare vehicle tow rating, GCWR headroom, hitch trailer rating, payload-based ceiling and any entered vertical-hitch ceiling. Show tied controlling limits together. Round the final modeled trailer ceiling down to whole pounds, normalizing only machine-precision noise at exact integer boundaries.
- Include added hitch hardware in vehicle cargo, while keeping trailer tongue load separate. Combined modeled weight is the vehicle before coupling plus the entire loaded trailer; tongue load is not added twice. Show actual signed pre-trailer GVWR/GCWR margins and overload warnings.
- Replace the pie with a compact, responsive bar chart of independent pound-based ceilings. Invalid inputs and Clear remove old cards and hide the chart.
- Keep the established theme and two-column input/results layout. The optional vertical-rating details are expandable; required inputs remain visible. Calculate is visible in the first 844px at 1366, 390 and 320 CSS-pixel widths.
- Improve the existing page title around towing capacity, GCWR, payload and hitch limits. Add original worked examples, precise load definitions and contextual links to payload, trailer payload and tongue-load tools. No duplicate landing pages or indexation expansion.

## Source and model boundaries

[Ford's towing guidance](https://www.ford.com/towing/) and its [2026 RV & Trailer Towing Guide](https://www.ford.com/content/dam/brand_ford/en_us/brand/towing/pdf/2026-Ford-RV-and-Trailer-Towing-Guide-v3.pdf), especially the weight-limit definitions, support the distinction between GVWR, GCWR, vehicle cargo and trailer tongue load. Inputs must come from the exact vehicle and equipment, rather than a generic model name. The PDF was accessible during this review; an initially attempted Ford support article was unavailable and was not relied on.

The calculator assumes the entered tongue load is carried by the vehicle; it does not model axle-load transfer or a weight-distributing hitch setup. GAWR, tire and wheel capacity, trailer GVWR, brakes, compatibility and the actual loading arrangement remain separate checks. A higher value in one constraint does not raise another rating. The 12% default is an editable example, not a loading recommendation.

Worked checks on the page:

| Scenario | Modeled result |
| --- | --- |
| 5,200 lb curb + 400 lb occupants + 200 lb cargo/hardware | 5,800 lb before trailer tongue load |
| 7,200 lb GVWR and 16,000 lb GCWR | 1,400 lb available for tongue load; 10,200 lb for the full trailer |
| 10,000 lb vehicle/hitch gross trailer limits, 12% tongue assumption, unknown vertical rating | 10,000 lb among modeled constraints; vertical rating explicitly unchecked |
| Add 900 lb vertical hitch limit | 7,500 lb trailer ceiling, 900 lb tongue load, 6,700 lb vehicle and 13,300 lb combined weight |
| 650 lb remaining payload / 12% | 5,416.666… lb raw ceiling; final whole-pound ceiling 5,416 lb |

## Validation

- **505 JavaScript scenarios** covering every controlling constraint, ties, exact whole-pound boundaries, unknown/zero hitch ratings, negative/blank inputs, overloads, mass accounting and monotonicity (adding cargo cannot increase capacity).
- **120 Python tests** and all existing JavaScript regression suites passed against the final optimized asset. Pages workflow YAML was parsed locally with the new towing step in `build.steps`.
- Local Playwright at **1366 / 390 / 320px** verifies first-screen Calculate, optional-rating behavior, bad inputs, overloads, downward rounding, no tongue double-counting, Clear recovery, Enter, metadata/schema, site search and category discovery. Screenshots of the inputs and 320px bar chart were visually inspected. No page-script errors or horizontal page overflow were observed.
- Indexation and schema contracts pass: **305 sitemap URLs**, **287 indexable calculators**, maximum crawl depth 3. No sitemap submission or account change was made.
- Final optimized calculator asset: **487,743 bytes**, version **`6788bbf55d584c44`**, 4,905 references. Script size increased for this feature; no faster-delivery, Core Web Vitals or traffic claim is made.

Reproduction: build and optimize into `doc-work/discovery-build`, then run `node scripts/test_towing.cjs doc-work/discovery-build/assets/calculator.js` and `node scripts/verify_towing_browser.cjs`. The browser script supports `--live` after deployment and blocks analytics requests to avoid synthetic GA4 visits.

## Growth follow-up

Observe this existing route in a later settled US Search Console window; the pre-release export cannot show an effect of this repair. The broader 90-day / 1,000-daily-organic-visits objective remains active and unproven. No outreach, external submission, spending or account-setting change occurred. A separate IRA savings-growth alias remains an unaddressed comparison-workflow candidate; no implementation or demand expansion for that page is claimed here.

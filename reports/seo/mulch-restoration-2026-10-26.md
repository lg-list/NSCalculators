# Existing Mulch Calculator Restoration

Date: October 26, 2026. Existing route: `/mulch-calculator/`.

## Why this release

The landscape audit confirmed the old route had no inputs, an unavailable message and noindex. Its distinct missing task is measured-volume arithmetic plus whole bags using an actual volume label, rather than Gravel's optional density-to-weight conversion. US monthly volume remains unknown, current comparative Trends was unavailable and the incomplete US GSC export has no named Mulch row. Those gaps do not justify a traffic forecast or material/retailer clone pages. This release restores a complete existing tool with original content and primary quantity references; see `exports/us-landscape-opportunities-2026-10-26.json` for separated provenance.

## Workflow and assumptions

- Rectangle dimensions or independently measured net area and depth to add. Hidden measurement inputs disable and do not affect the active method. Dimensions switch between ft/in and m/cm with numerical conversion. Net area must exclude unmulched paths, structures or other deductions; none are made automatically. For top-up projects, enter only the layer being added.
- Reuses validated area/depth volume logic from Gravel with no density or mass-price input. Positive finite active geometry and entered 0%-100% volume allowance; unsupported numerical quantities are rejected rather than clamped. The default 3-inch layer and 0% allowance are editable arithmetic examples, not horticultural recommendations, settling measurements or compaction conversions.
- Optional volume per bag supports ft³, liters and m³; switching the label unit converts the value while retaining physical volume. Project-unit changes do not reinterpret the label. Zero/negative entered bag volume is invalid. Blank label volume leaves bulk volume/cost available and bag count, purchased bag volume and bagged cost unknown. Weight-labeled/compressed products need other information; there is no universal lb-to-volume conversion.
- Whole bags are rounded once from the unrounded allowance-adjusted target, with a machine-scale near-integer correction. Counts outside 1-1 billion are rejected. Purchased volume and bag-rounding excess are separate from planned allowance. Tiny supported projects still require one bag and a real excess still requires another.
- Optional entered price per bag and independent bulk quote per yd³ or m³. Blank is unknown, explicit zero remains zero. Bagged cost needs a label volume and bag price; bulk cost needs only a bulk quote. They are mutually exclusive material-only scenarios, not a grand total or a lowest-delivered-price recommendation. No delivery, tax, labor, supplier minimum, bulk delivery increment or return term is applied.
- Default 200 ft² x 3/12 ft = 50 ft³ = 50/27 yd³, or 25 two-ft³ bags. With entered 10% allowance: 55 ft³, 28 bags, 56 ft³ purchased and 1 ft³ of bag-rounding excess. At example-only $4/bag, bagged material is $112; at an independent $50/yd³ quote, bulk material is $101.85 after display rounding.
- Chart compares only cubic-foot components: base, allowance and (when known) bag-rounding excess. Dollars remain in separately labeled cards/table. Invalid edits and Clear remove stale analysis; valid edits recover without reload. Enter uses the existing scoped handler. Theme/fonts/plugins remain; scoped card wrapping handles supported extreme values and concise bag-unit labels fit mobile controls.

## Precision finding and repair

Before release, a deterministic audit found 32 of 100 sampled exact-17-bag projects could become 18 solely from converting intermediate values to 15 significant digits. The new Mulch unit path retains floating-point conversion precision instead of rounding it for display; the shared conversion helper has an explicit precision-preserving option used by Mulch. Gravel's default behavior remains unchanged and its existing 231 scenarios continue to pass. Bag label conversion routes through cubic feet without intermediate decimal rounding.

Regression coverage now checks 1,000 paired US/project-ft³ versus metric/liter exact-boundary cases: each remains 17 bags. This repairs this observed conversion path; it is not a claim of unlimited decimal precision or certification of every physical measurement. Real excess and unsupported ranges have independent checks so the fix is not a broad arbitrary tolerance that hides additional material requirements.

## Original content and primary evidence

[Iowa State Extension's quantity guidance](https://yardandgarden.extension.iastate.edu/how-to/how-determine-amount-mulch-needed-garden-bed), labeled reviewed July 2026, describes area-times-depth volume, bag-label division and the 27 ft³/yd³ conversion. A numeric test independently reproduces its 265 ft² / 1.5-inch / two-ft³ example (33.125 ft³, 17 whole bags); public page examples are independently written and retain precision rather than copying rounded table values.

[UC Marin's application guidance](https://ucanr.edu/site/uc-marin-master-gardeners/applying-mulch) shows that material, site and placement matter. The tool points to that guidance without prescribing a product, universal layer thickness, trunk distance, fire-risk assessment or local-code decision. No university/retailer affiliation is claimed.

Original explanations cover unknown costs, net area, existing mulch, package excess versus allowance and why bagged/bulk prices are alternatives. Mulch links to Area/Square Footage and Gravel for distinct measurement/mass tasks; Gravel/Square Footage link back to the restored bag-volume workflow. No bag-size, retailer or mulch-material clone URL is created. Metadata targets mulch calculator, cubic yards, whole bags and material cost without publishing keyword-research labels on the site.

## Release validation

- 115 Python tests pass, including two new Mulch content/discovery/metadata checks. All JavaScript suites pass against the optimized artifact: 165 core Mulch scenarios and 1,000 paired boundary checks (2,165 total model/render executions), plus the existing calculation suites. CI includes the new suite.
- Existing index/search baseline tests keep original baseline counts and explicitly permit only the reviewed ownership/Gravel/Mulch additions. No other unfinished route becomes indexable through this release.
- Full isolated build validates 140,780 internal links. Indexation/schema gates pass with 287 indexable calculators, 305 sitemap URLs, maximum depth 3, 288 apps, 299 breadcrumb trails and 1,173 breadcrumb targets.
- Readable bundle is 556,307 bytes; build-time optimization produces 473,169 bytes with content hash `9cfdaa4c9bd672b2` across 4,905 references. CSS gate confirms 5,027 references to `137a61e00f1a1a4a`. Tracked `dist/` is unchanged; CI builds and tests the final optimized asset.
- Local Playwright at 1366, 390 and 320px passes first-screen Calculate (844px height), project/bag-unit round trips, invalid and inactive inputs, optional prices, separate cost scenarios, bulk-only input, Clear recovery, Enter, chart pixels, extreme wrapping and canonical/indexability. Homepage search finds Mulch once and opens it; Construction links to it; sitemap includes both restored tools. Reviewed default and chart mobile screenshots. Ignored harness: `doc-work/verify-mulch.cjs`, with `--live` for deployment verification.

No external indexing/sitemap submission, account change, payment or outreach. Restored indexability is not proof of a Google recrawl/index entry. The 1,000 daily organic-visit goal remains unachieved/unverified; assess settled US performance after deployment rather than declaring search lift from passing tests.

# Structured Data Consistency Guard

## Finding and Decision

October 24, 2026. The previous goal turn was progress: the Sample Size mean-planning release was committed, deployed and production-verified. This continuation audits structured data, not another snippet rewrite or index expansion.

The generated indexable corpus contains 302 sitemap URLs, 285 application declarations, 296 breadcrumb lists and 1,161 breadcrumb items. All breadcrumb destination files and fragment IDs existed before this change. There was no evidence for restructuring that hierarchy.

Every application declaration used `CalculatorApplication`, which is not in Google's supported application-category list. Changed it to `UtilitiesApplication` in the shared calculator schema and the separate Scientific Calculator template. The previous payload was syntactically valid JSON; this finding is not proof of an indexing failure, ranking penalty or inability to parse the app.

[Google's software-app reference](https://developers.google.com/search/docs/appearance/structured-data/software-app) lists supported categories and separately requires a qualifying rating or review for software-app rich-result eligibility. The site has no established review/rating source. No rating, review, date, author credential or popularity count was invented to satisfy that prerequisite. Keeping truthful software metadata is not a claim that app rich results are available.

## Deployment Guard

Added `scripts/check_schema_contract.py`, run after the existing sitemap/crawl-path check and before artifact upload. It reads the generated sitemap and HTML using XML/HTML/JSON parsers, with no external submission or account access.

For each sitemap URL it checks this site's current contract:

- One canonical, description and visible H1; the WebPage/CollectionPage URL and description match that metadata.
- A visible calculator has exactly one app entity and breadcrumb trail. The app name matches H1; app URL and description match the page. Non-calculator pages do not silently acquire an app declaration.
- Supported application category and the site's existing free USD offer. Rating/review additions fail closed pending an explicit source audit, rather than being assumed genuine.
- Sequential breadcrumb positions, the site's intended Home/current-page endpoints and current-page H1; each target is on the configured HTTPS origin and its file and optional decoded fragment ID exist. Unsafe paths and query-bearing schema targets fail.
- Invalid JSON-LD and nonstandard numeric constants fail. Flat blocks, graph payloads and the optional GitHub project base path are covered.

The Home endpoint and free-USD conventions are local implementation contracts, not universal Google requirements. This checker is not a general schema.org validator, a Google Rich Results Test, verification of every formula/content claim, a crawler/CDN header check or proof of indexing. Its complete-corpus scope is the 302 sitemap pages, not every noindex URL.

[Google's general guidelines](https://developers.google.com/search/docs/appearance/structured-data/sd-policies) require relevant, truthful visible-content representation and do not guarantee display. [Its breadcrumb reference](https://developers.google.com/search/docs/appearance/structured-data/breadcrumb) describes the hierarchy use case. Do not conflate JSON parsing, these local checks and rich-result eligibility.

## Verification

Ten new Python test methods exercise flat/graph payloads, invalid/missing JSON, mismatched app metadata, unsupported category, review-source guard, free-offer drift, missing/duplicate entities, breadcrumb order/endpoints, missing files/fragments, old/external/unsafe URLs and project-base-path resolution. All 93 Python tests and 1,674 existing JavaScript cases pass locally.

The full generated corpus passes: 302 pages / 285 apps / 296 trails / 1,161 items. Existing indexation and version gates also pass: 284 indexable calculator records, 140,689 internal links, 4,902 calculator-script references and 5,026 stylesheet references. No CSS, calculator JavaScript, formulas, titles, descriptions, Analytics settings or index policy changed.

Rendered Playwright checks cover nine representative paths at desktop and mobile widths, including regular/basic/scientific calculators, homepage, category, guide and an intentionally unavailable tool. JSON-LD name/URL/description/category/free offer and breadcrumb endpoints are checked against rendered page metadata; unavailable/non-tool pages retain no app entity. No JavaScript errors or horizontal overflow. Analytics requests are blocked during synthetic checks.

Deployment/live verification is completed after push, not inferred from local tests. No external validation/indexing submission, outreach, purchase or account change occurred. No traffic gain or rich-result qualification is established, and the daily-1,000 organic-visit goal remains unachieved.

# Static Indexation Contract

Audited: 2026-10-24. This is deployment evidence, not Google indexing evidence.

## Current Findings

The current generated sitemap contains 302 unique URLs. Traversing ordinary HTML links **only through sitemap pages**, not through the 4,700+ intentionally excluded calculator routes, reaches every sitemap URL from the homepage. Shortest click distances are: homepage 1 URL, one click 26, two clicks 273, three clicks 2. No orphan sitemap URL was found. This three-click threshold is our usability/regression policy, not a Google ranking requirement.

Each sitemap page has one exact HTTPS self-canonical, one nonempty description, no robots/googlebot noindex or none directive, no meta refresh or base element, an existing HTML artifact, and permission under the current simple robots rules. The canonical sitemap is referenced from robots.txt.

Public Playwright spot checks of Area, Used Car Value, Ratio and Trip Fuel Cost returned HTTP 200 with correct self-canonicals and parseable rendered WebPage, BreadcrumbList and SoftwareApplication JSON-LD. Both robots.txt and sitemap.xml returned HTTP 200; sitemap content type was application/xml. Parsing schema does not establish Google rich-result eligibility. These spot checks do not prove every production route or geographic edge is healthy.

## Improvement

Added `scripts/check_indexation_contract.py` to GitHub Pages after the build and before uploading the deployment artifact. It checks **every sitemap URL**, not a sample or hardcoded count. It rejects duplicate/noncanonical/out-of-domain/parameterized sitemap URLs, unsafe paths, missing files, wrong or multiple canonical tags, meta indexing exclusions, redirect/base markup, missing or duplicate descriptions, robots blocks, a wrong sitemap reference, and unreachable/deep crawl paths.

The graph resolves relative links and fragments and excludes rel=nofollow/sponsored/ugc links conservatively. Pages with a nofollow meta directive do not provide traversal edges in this gate. This is a conservative discovery contract, not a claim about how Google treats all link hints.

The robots check uses the standard parser only for simple non-overlapping prefix rules. Wildcards, end anchors or overlapping paths fail closed and require a separate Google-compatible audit; it does not silently pretend to implement Google's longest-match behavior. Project subdirectory deployments are supported via `--site` without changing the production domain.

Run after building:

```powershell
python scripts/check_indexation_contract.py dist
```

## Verification and Limits

All 75 Python tests pass, including eight new fixture-based regression methods covering crawl paths, exact canonicals, combined robots directives, geography/domain drift, unsafe paths, duplicate URLs, robots blocking/unsupported rules, redirects/base markup and subdirectory deployment. The current isolated site passes the new gate for all 302 sitemap URLs. HTML, CSS, scripts, calculation formulas, snippets, canonical output, robots output and sitemap output are unchanged by this release.

This static gate does not execute arbitrary client-side SEO changes, validate every JSON-LD semantic property, fetch production response headers, detect all server/CDN redirects, measure Core Web Vitals, inspect Google's selected canonical or prove indexing. Keep Search Console recrawl evidence and live checks separate. Existing intentional noindex routes remain excluded; do not remove noindex merely to clear a coverage warning. No account changes, payments, submissions or outreach were made.

Reference: [Google's sitemap documentation](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap) describes absolute URLs and sitemap scope. [Google's robots meta documentation](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag) explains crawler-specific directives and indexing exclusions. Neither promises indexing or ranking after a sitemap is supplied.

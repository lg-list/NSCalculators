# Sitemap indexing triage — November 9, 2026

The preceding turn recovered current US performance totals and flagged a low recent seven-day global observation. This turn reads Google's actual indexing overview rather than treating public HTTP 200 responses as proof of Google inclusion.

## Observed Google report

NS domain property, updated November 6: all-known URLs show 336 indexed and 729 excluded (707 noindex, 9 redirects, 1 other Google canonical, 1 crawled-not-indexed, 11 discovered-not-indexed). These counts are not US search metrics and do not establish a historical change without a prior comparable indexing series.

Selecting the actual `https://nscalculators.com/sitemap.xml` scope gives **290 indexed + 15 excluded = 305**. Exclusions are 2 noindex, 11 discovered-not-indexed, 1 other Google canonical and 1 crawled-not-indexed. This contradicts a claim that the entire site is currently absent from Google's reported index, but does not rule out a historical decline or explain recent low impressions. Do not remove all noindex directives to inflate coverage.

The two sitemap noindex examples are Gravel (last crawled October 17) and Mulch (October 14). Both crawl dates precede their verified October 26 restorations. Current independent public Playwright requests return 200, matching canonical, no meta/header noindex and inclusion in the sitemap for both. The evidence is consistent with a stale pre-restoration crawl status. It does not prove Google has re-fetched either corrected page.

Sanitized Google observations: `exports/indexing-ui-observation-2026-11-09.json`. Independent response evidence: `exports/gravel-mulch-live-indexation-2026-11-09.json`. No account identity, authentication data or full private UI snapshot is published. Browser recovery was slow but the scoped report and both examples were visibly read. No download, validation, resubmission or request-indexing action was performed.

## Implemented improvement

Add `lastmod=2026-10-26` only to these two sitemap entries. The dates are backed by Git commits 5becd87046, 3defecfc13 and f07dec8071, all dated October 26, which restored the tools and clarified methodology. This is a significant-content date, not today's build date. Other entries remain undated where a latest significant change has not been verified. Update this explicit mapping when a later significant page change is verified; do not refresh it automatically on deploy.

[Google's sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap) says modification dates should be accurate and reflect significant page changes, and that sitemap hints do not guarantee crawling. The change supplies truthful information; it is not a claim of accelerated crawling, restored rankings or completed inclusion. Preserve the current page indexability and URL set. The remaining 13 exclusions and current daily performance breakdown still require targeted investigation.

## Validation and follow-up

139 Python tests pass, including exact verified dates, canonical locations, omission on unverified routes and invalid-date rejection. Build/indexation/schema/version checks and exact Pages deployment gate the release; after deployment confirm the two XML dates and live page signals again. No new indexable page or calculator change, spending, account modification, outreach or external submission. The 1,000 daily organic visits goal remains active and unproven.

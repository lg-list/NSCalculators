# Public indexation-signal audit — October 29, 2026

Previous turn yielded a verified access limitation, not a site fix: updated GSC Wizard remained subscription-gated and Windows browser observation was stopped before any report was read. Do not repeat those blocked methods or label the site deindexed. This turn made independent progress by inspecting the current public deployment.

## Scope and results

`scripts/audit_live_indexation.cjs` uses Playwright's request client for read-only public HTTP checks. It fetched the production sitemap, verified its namespace, unique URL list and same-origin scope, then fetched all listed pages with six concurrent workers. No browser scripts, analytics requests, Google APIs, credentials or account endpoints were executed. No form or sitemap was submitted. The raw report's `checkedAt` is authoritative for observation time.

All **305** sitemap URLs returned HTTP 200, `text/html`, and their expected final URL without a redirect. Each had exactly one matching self-canonical, one H1, a nonempty title and description, and no detected noindex/none directive in robots/Googlebot meta or X-Robots-Tag response headers. No duplicate title was found among the 305 pages. The current published release is the previously verified Area delivery commit d1ae7886ae, Pages run 40894608137.

Original observations: `exports/public-indexation-2026-10-29.json`. Public page titles, URLs and response findings only; no account data. Eight synthetic parser checks cover valid signals, robots/Googlebot/header noindex, wrong canonical, duplicate H1 and missing title/description. These fixture checks are added to Pages CI; the production network audit is deliberately manual rather than recrawling 305 URLs on every deployment. All 136 existing Python tests pass.

## Decision

No production canonical, robots, sitemap or metadata change is warranted by this audit. Search index source and existing discovery tests already exclude unfinished tools; functional noindex conversions remain available to users and should not be removed merely because they are outside the sitemap. No title churn or index-scope expansion was introduced.

Public fetching is not evidence that Google crawled or indexed a page, chose its canonical, or will rank it. This audit does not cover the excluded URLs, robots.txt semantics, JavaScript rendering, calculation accuracy, field Core Web Vitals or a controlled Googlebot fetch. It does not prove that the 1,000 daily organic visits objective was reached. Current GSC indexing and later completed US query data are still needed before diagnosing a Google-specific exclusion or claiming impact from the recent changes. The last validated US performance window still ends October 25.

Reproduction: `node scripts/audit_live_indexation.cjs` writes the detailed timestamped results to the ignored working directory; `node scripts/test_live_indexation_signals.cjs` runs offline parser fixtures. Network exceptions remain request errors, not assertions about Google's crawl access. Preserve the current healthy settings and use a concrete failing URL or fresh Search Console export to guide the next indexation repair.

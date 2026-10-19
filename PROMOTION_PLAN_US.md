# NS Calculators — US Growth Plan

Updated: October 19, 2026

## Goal

Grow qualified US organic traffic by concentrating authority, content improvements, and outreach on pages that already show search demand. Avoid publishing thousands of thin variations or buying low-quality links.

## Current Search Baseline

- US Google Search visibility (September 18-October 15, settled through October 16): 4,187 impressions, 4 clicks, 0.10% CTR, average position 44.65.
- Strongest observed opportunity: `area calculator` — 593 US impressions, 0 clicks, average position 8.62 on `/area-calculator/`.
- Other near-page-one queries include `fuel cost calculator` (14 impressions, position 8.5), `car price estimate` (22 impressions, position 11), `used car value` (29 impressions, position 25.7), and `ratio calculator` (21 impressions, position 22.6).
- The latest settled Search Console data predates the October 18 Area title/description update, the new irregular-room guide, and the October 19 multi-section area feature. Do not judge or repeat those changes until a post-deployment data window is available.
- The audited priority pages are indexable, return HTTP 200, use self-referencing canonicals, have one H1, and include structured data. The main constraint is relevance, differentiation, and authority rather than a basic crawl failure.
- 2026-10-19 keyword-map audit: `seo-priority-keywords.csv` contains 371 URL rows for 174 unique terms. Every term has exactly one indexable URL; the other 197 rows are noindex contextual variants. Use `exports/seo-priority-keywords-indexable.csv` for prioritization and keep the all-targets export as the source; the normalized map is reproducible with `scripts/build_indexable_keyword_targets.py`.

## Priority Pages

1. `/area-calculator/`
   - Primary intent: calculate area for a rectangle, circle, triangle, square, trapezoid, ellipse, parallelogram, or sector.
   - Supporting terms: square footage calculator, area formula, area unit converter, rectangle area calculator, circle area calculator.
   - Promotion angle: a single tool with multiple shapes, perimeter, formulas, and US/metric unit conversion.

2. `/used-car-value-calculator/`
   - Primary intent: free used-car price estimate based on local comparables.
   - Supporting terms: car price estimate, car value finder, used car value, private-party value.
   - Be explicit that the tool has no live VIN or transaction feed.

3. `/car-trade-in-value-calculator/`
   - Primary intent: dealer trade-in offers and positive/negative equity.
   - Supporting terms: car trade in calculator, trade in value calculator, dealer offer comparison.

4. `/car-resale-value-calculator/`
   - Primary intent: future private-sale value, depreciation, loan payoff, and net proceeds.
   - Keep this page distinct from current used-car value and dealer trade-in intent.

5. `/geodesic-dome-calculator/`
   - Existing click signal and a focused niche with outreach potential to dome builders, greenhouse communities, makers, and architecture educators.

## First 30 Days

### Week 1 — Search CTR and intent alignment

- Deploy the revised titles and meta descriptions for Area, Used Car Value, Future Resale Value, and Trade-In Value.
- Confirm the generated sitemap is live and monitor Search Console for title rewrites, impressions, average position, and CTR.
- GA4 is installed. Track `calculator_submit` and `outbound_reference_click` as implemented events; add `result_view`, `copy_result`, or `share` only if those distinct user actions are implemented and can be measured reliably.

### Week 2 — Authority pages and internal links

- Add one useful English guide for each priority cluster, not generic filler:
  - How to Calculate Square Footage for Irregular Rooms
  - Rectangle, Circle, and Triangle Area Formulas
  - Used Car Value vs. Trade-In Value vs. Resale Value
  - How Negative Equity Changes a Trade-In
  - Geodesic Dome Area, Volume, and Material Planning
- Link each guide to one primary calculator and relevant supporting tools using descriptive anchor text.
- Add “last reviewed” and named editorial/review responsibility where genuine.

### Week 3 — US-focused outreach

- Pitch the Area and construction tools as free references to US flooring installers, landscaping blogs, community-college math pages, teacher resource lists, and DIY publishers.
- Pitch the geodesic-dome calculator to dome builders, greenhouse forums, maker communities, and architecture education sites.
- Pitch automotive comparison guides to independent dealers, auto-finance educators, credit unions, and consumer auto blogs.
- Personalize every outreach message around the recipient's existing resource page. Do not buy links or use automated bulk guest-post networks.

### Week 4 — Distribution and iteration

- Publish short, native demonstrations on YouTube Shorts, Pinterest, Reddit communities where self-promotion is permitted, and relevant Q&A pages.
- Each post should answer one concrete calculation question and link only when the tool adds value.
- Compare the latest 28 days with the prior period. Keep changes that improve clicks without losing relevant impressions.

## Content and Link Standards

- Write for US English and US customary units first, while keeping metric conversion available.
- Use current US government or primary references for finance, health, tax, vehicle, and construction claims.
- Avoid doorway pages, spun location pages, fake reviews, AI-generated link spam, and pages that differ only by a keyword.
- Consolidate pages when two URLs serve the same search intent; preserve redirects and canonicals.
- Prefer a smaller number of demonstrably accurate calculators over rapid low-quality expansion.

## Measurement

Track weekly by page and query:

- US impressions, clicks, CTR, and average position
- Indexed pages and sitemap errors
- Organic landing sessions and engaged sessions
- Explicit calculator submissions and outbound reference clicks (GA4); result-copy/share events are not available because the site has no copy/share actions.
- Referring domains and links earned to priority pages

Initial 30-day targets after deployment:

- Area Calculator CTR: move from 0% toward at least 2% while holding first-page visibility.
- US organic clicks: establish consistent weekly growth from the current low baseline.
- Earn 5–10 relevant referring domains through direct, manual outreach.
- Resolve the Resale vs. Trade-In keyword overlap so the intended page ranks for each query family.

## Promotion Assets to Prepare

- One 30–45 second screen recording for each priority calculator.
- One 1200×630 social preview image per priority page.
- A one-paragraph tool description and three short post variants per page.
- A compact outreach sheet with prospect URL, contact route, relevant resource, pitch angle, status, and response.

## Search Snippet Test Log

- 2026-10-19: Tested a snippet revision for `/trip-fuel-cost-calculator/` after US GSC showed `fuel cost calculator` at 14 impressions, 0 clicks, position 8.5, and 83 total US page impressions with 0 clicks in 2026-09-18 through 2026-10-15. The old description did not name MPG or gas price; the new 137-character description does. On-page audit showed indexable, self-canonical, 1,187 words, 29 internal links, valid structured data, and no issues. Hold further edits until a settled post-change window.
- 2026-10-14: Updated the Area Calculator title to state its eight supported shapes, formulas, and unit conversions, and rewrote the description to emphasize entering dimensions and getting area/perimeter outputs. Baseline from US Search Console, 2026-09-14 through 2026-10-11: `area calculator` had 593 impressions, 0 clicks, and average position 8.62 for this URL. The page audit found 1,308 words, 31 internal links, a self-canonical, indexable status, and no on-page issues; URL Inspection returned `PASS` / `Submitted and indexed`. Recheck after a full 28-day post-change window; Google may choose a different title or snippet.
- 2026-10-14: Improved the Square Footage Calculator after GSC showed 0 US impressions in the prior 28 days despite confirmed indexing. Replaced its generic title with an accurate feature-focused title, expanded measurement, wall, irregular-room, overage, and cost examples, added a current NIST foot-conversion reference, and linked the specialized flooring and general area tools. Recheck query impressions and clicks after a full 28-day window.
- 2026-10-14: After the post-deployment page audit flagged the Area Calculator meta description at 168 characters, shortened it to 155 characters while keeping the shape, formula, perimeter, and unit-conversion value proposition.
- 2026-10-14: Refined the Compound Interest Calculator title and description to reflect monthly/annual deposits, nine compounding frequencies, timing, tax, inflation, charts, and schedules. The keyword forecast export estimates 500 monthly searches for the head term (dated 2026-09-02); GSC URL Inspection reports the page as discovered but not indexed, with no on-page or technical audit issues. Monitor indexing and query performance; request indexing only after user authorization.

## Search Console Baseline

- 2026-10-14: US page-level Search Console data for 2026-09-14 through 2026-10-11 showed 2,519 impressions and 1 click across 151 pages with impressions. Leading pages were Area Calculator (601 impressions, average position 9.41), Car Trade-In Value Calculator (323, position 84.10), and Used Car Value Calculator (191, position 52.23). The Area snippet changes were deployed after this baseline; wait for a complete post-change window before judging their effect.
- The submitted sitemap contains 300 URLs and was fetched with 0 warnings and 0 errors. The sitemap summary reports 0 indexed, but a sitemap-URL-to-Search-Console-performance join found 148 of those URLs with impressions in the same date window, and URL Inspection confirms key pages as indexed. Treat the sitemap indexed count as inconsistent with observed search visibility; use URL Inspection and URL performance for individual decisions. Do not respond by broadening the sitemap to low-quality pages.
- 2026-10-14: A fresh US query/page/device pull for that same settled window confirms `area calculator` at 593 impressions, 0 clicks, position 8.62; almost all were desktop (599 page-device impressions versus 2 mobile, reflecting the separate page/device aggregation). Trade-in queries were mostly on the intended Car Trade-In Value Calculator, but `trade in value calculator` had 50 impressions at position 84.3 and `car trade in value calculator` had 17 at position 87.5. `used car value` had 26 impressions at position 20.0. Live audits of Area, Car Trade-In Value, and Used Car Value returned HTTP 200, self-canonicals, indexable pages, structured data, and no reported issues. A cross-query cannibalization scan found small-volume overlap between trade-in and resale pages, but their tools answer distinct current-offer/equity versus future-private-sale questions; do not consolidate on this evidence. Focus next on measuring post-deployment Area snippet performance and improving trade-in relevance/authority only when stronger query evidence or a concrete content gap supports a change.
- 2026-10-14: Extended the live on-page audit to the 10 highest-impression pages: all 10 are indexable, self-canonical, return HTTP 200, and have no schema issues; one low-severity slow-response warning (4,198 ms) appeared on the Car Trade-In page. Direct repeated requests from this environment varied widely (about 0.97–6.57 s TTFB), while response headers show Cloudflare in front of GitHub Pages and a short GitHub edge processing time. Treat this as a regional/CDN-path signal, not a confirmed application regression; verify from a US region and with field data before making infrastructure changes. CrUX field metrics remain unavailable because no API key is configured in GSC Wizard; do not change account settings without authorization. GA4 is connected to GSC Wizard, but the authenticated account has no GA4 property linked to this site (`no_property`), so session and calculator-event performance cannot yet be joined to Search Console data.
- 2026-10-19: Latest US Search Console query/page data is still settled only through 2026-10-16. The Area Calculator leads with 593 impressions for `area calculator` at position 8.62 and no clicks; other queries near positions 3-30 have materially lower volume (`fuel cost calculator`: 14 impressions at 8.5; `car price estimate`: 22 at 11; `used car value`: 29 at 25.7; `ratio calculator`: 21 at 22.6). Treat the October 18-19 page changes as unmeasured until later settled data includes them.
- 2026-10-19: Rechecked the exact `area calculator` query with both USA country and landing-page dimensions: 593 US impressions, 0 clicks, position 8.62 on `/area-calculator/`. Important measurement caveat: `score_opportunities` returned unfiltered/global data (for example, 50 impressions for `tip calculator` globally), while an explicit USA query/page check found only 2 US impressions for that query. Use country-filtered Search Analytics before using global opportunity rankings to set US priorities. `car trade in calculator` had only 8 US impressions on its intended page (position 72) plus 1 impression on `/used-car-value-calculator/` (position 80); this overlap is too small to justify consolidation.
- 2026-10-19: The latest GSC on-page audit of the 10 highest-impression pages found 0 issues; all 10 return HTTP 200 and are indexable with self-canonicals, one H1, valid structured data, and no schema issues. No technical edit is warranted from this audit. Before resubmission, Search Console showed 301 URLs while the live sitemap had 302; the sitemap has since been resubmitted with owner authorization (see the 2026-10-19 entry below).
- 2026-10-19: Published `/guides/calculate-square-footage-irregular-room/` and linked it from the Area, Square Footage, Flooring, and Tile calculators. Added a multi-section area accumulator to the Area Calculator, converting each section to square meters before summing and allowing the output unit to change. Added visible breadcrumbs and `BreadcrumbList` schema to both editorial guides. Local build, interaction tests, mobile/desktop overflow checks, and live deployment checks passed.
- 2026-10-19: The live sitemap returns HTTP 200 and contains 302 URLs, including the new guide. Before the latest submission, Search Console still reported the prior 301-URL version last downloaded on 2026-10-18 before the guide deployment. The indexing tracker last checked 2026-10-18 reports 8 of 9 tracked URLs indexed; the existing used-car guide is still "URL is unknown to Google," and the new guide is not in the tracker. Do not submit repeatedly; URL inspection has not been requested.
- 2026-10-19: Following the owner's prior explicit request to submit the sitemap, re-submitted `https://nscalculators.com/sitemap.xml` in Search Console. Google accepted it; a subsequent sitemap report shows 302 URLs submitted, 0 warnings, 0 errors, and 0 indexed, with no pending fetch. The live sitemap parses as a standard XML `urlset` with 302 URLs and HTTP 200; `robots.txt` also returns HTTP 200 and names the sitemap. Submission is complete, but 0 indexed remains a Search Console status to monitor; a sitemap submission does not guarantee indexation. Do not submit repeatedly; revisit after Google has had time to crawl.
- 2026-10-19: Rechecked the P1 Compound Interest Calculator against Search Console and its indexing tracker. Google reports it indexed with the correct self-canonical and last crawled 2026-10-16; its URL is included in the 302-URL sitemap. It had 0 search impressions in the 2026-09-18 to 2026-10-15 report, which predates confirmed indexation, so this is not evidence of a performance failure. The live page has a 55-character title, 157-character description, 783 words, 28 internal links, financial-growth features, worked examples, and no issues in the latest on-page audit. Hold further edits until a post-indexing data window is available.
- 2026-10-19: The other keyword-planner leader, `feet to meters calculator` (500 average monthly searches in the supplied export), is also confirmed indexed with its correct self-canonical; Google last crawled it on 2026-10-15. It had 0 impressions in the 2026-09-18 to 2026-10-15 window, but that window contains almost no time after its last crawl/index confirmation. The live page has an exact-match title, 872 words, 28 internal links, and no issues in the latest on-page audit. Treat both 500-search P1 pages as newly indexed measurement candidates, not as proven failures; re-evaluate after a full settled post-indexing period.
- 2026-10-19: A USA-filtered GSC query/page review found the long-tail `vehicle price estimator that includes values for poor condition cars` at 5 impressions total, split between `/used-car-value-calculator/` and `/car-resale-value-calculator/` (positions 17-18). The overlap is too small to consolidate. Improved the current-value page's input label and explanatory copy so users know a negative repair adjustment is supported, and added an FAQ explaining that poor-condition estimates require a comparable in similar condition and documented repair assumptions; no market discount is claimed. GSC returned 1,133 named US queries covering 67.8% of filtered impressions, so anonymized/omitted query data is a material limitation when interpreting the long tail.
- 2026-10-19: A fresh audit of the top 20 pages with impressions (2026-09-19 through 2026-10-16) found one intentional non-indexable URL: `/weight-watchers-points-calculator/` (74 impressions in the mixed-date GSC report, 196 words). The page was deliberately replaced on 2026-10-14 with a brief, non-affiliated explanation and `noindex` because the official personalized points formula cannot be reproduced reliably; the live page sends `noindex` and is absent from the sitemap. URL Inspection still says "Submitted and indexed" with last crawl 2026-09-17, predating the replacement. Treat its impressions and verdict as stale pre-change data, not a current indexation defect or a page to promote. Do not request indexing for it; let Google recrawl the noindex page.
- 2026-10-19: Re-inspected five key URLs in Search Console: Area, Car Trade-In, Mortgage, Compound Interest, and Square Footage all return `PASS` / `Submitted and indexed`, with Google-selected canonical matching the declared self-canonical. Search Console's sitemap report still displays 0 indexed, but the sitemap-performance join found 181 of 302 URLs with Search impressions in 2026-09-18 through 2026-10-15 (5,888 total impressions, 12 clicks); this is evidence of search visibility, not an exact index count. Keep the sitemap scoped to indexable pages and use URL Inspection for individual index-state decisions.
- 2026-10-19: Improved the Towing Capacity Calculator after the US query/page report showed 89 page impressions at average position 76 (9/19-10/16); visible intents included `towing calculator` (17 impressions, position 74.1), `towing capacity calculator` (15, position 73.3), and `estimated towing capacity` (11, position 69.3). Code review found that the limiting formula omitted the receiver's maximum vertical/tongue-load rating and clamped negative payload to zero without stating the existing overload. Added an optional hitch tongue-load input and converted that limit into its trailer-weight equivalent; preserved negative GVWR/GCWR margins and surfaced explicit overload warnings. Updated the explanation and rating guidance, with Ford towing guidance as the primary reference. Playwright verified baseline, an entered 1,000 lb tongue rating (8,333 lb cap at 12%), GCWR overload, and GVWR overload; mobile width remained 390/390 with no browser errors. `node --check` and the full build/link validation passed (5,008 pages; 140,739 internal links checked).
- 2026-10-19: Live Playwright inspection found homepage search promoting Currency Calculator with unrelated Amount/Rate/Years inputs from the generic engine. Removed 104 unfinished routes from site search and prevented unfinished tools from entering homepage recommendations. Their direct URLs retain noindex and now show availability plus relevant working tools instead of unrelated calculation forms; the existing WeightWatchers explanation is preserved. Search still includes working low-demand/noindex converters and the dedicated scientific calculator (4,904 entries total), while sitemap scope stays at 302 URLs / 284 calculator entries. Five regression tests, full isolated build/link validation, and Playwright checks for unavailable searches, valid searches, direct routes, and mobile overflow passed. Future implementations can re-enter discovery by replacing the generic engine and clearing the explicit unfinished list after verification.

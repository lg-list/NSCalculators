# Search Console measurement access

## Newly verified limitation

On 2026-10-22 the connected GSC Wizard reader refused requests. Its detailed error was `payment_required` / `subscription_required`; the initial structured response only reported `INVALID_ARGUMENT`. The follow-up property listing exposed the actual reason: the connector has no active trial or subscription. Further retries cannot provide current Search Console data until that access condition changes.

This is a third-party connector limitation, not evidence that Google Search Console itself requires payment, the site lost verification, traffic fell, the sitemap failed or Google stopped indexing pages. No paid subscription, account change, reconnection or external submission was performed.

Tried the existing Chrome browser as a free read-only alternative. The requested NS Calculators performance tab was created and its title/URL appeared in browser inventory, but binding/reading that tab timed out. Authentication and property access could not be verified from its contents. No metrics were successfully read from it. Did not restart an unobserved browser job, alter the unrelated existing tabs, submit a sitemap or request indexing.

## Decision

Do not claim a new US traffic result, use worldwide/China figures as US demand, or reprioritize recently edited snippets using old numbers. Existing source corrections and the full 90-day objective remain intact. This access issue does not establish that independent technical or functionality work is blocked, and it does not justify marking the growth goal complete.

The owner can provide a free export directly from Google Search Console. A paid connector is optional, not a prerequisite for SEO work.

## Free export handoff

1. Open the **nscalculators.com** property in Google Search Console, then the search-results performance report. Do not export a different site's currently selected report.
2. Select **Web** search, a completed date range and **United States** as the country filter. Prefer the latest 28 completed days, excluding the newest partial days; keep the exact dates visible. A second preceding, equal-length range is useful for comparison but should be exported separately.
3. Export the report as CSV or Excel and provide the original files. Keep the Queries, Pages and Dates tables together where the export includes them. Include the Filters table or a screenshot showing property, country, search type and dates, plus the displayed total clicks and impressions.
4. For a query/page opportunity requiring an exact pair, apply a page filter and export that page's Queries table separately. Separate unfiltered Queries and Pages tables cannot be joined to manufacture query/page pairs.
5. Do not send Google passwords, cookies, API keys, recovery codes or a payment method. No new account permission is needed merely to provide an export.

## Rules when the export arrives

- Verify property, geography, date range, search type and whether days are complete before analysis. Unknown geography remains unknown, not US.
- Preserve raw source files and identify export date independently of the measured date range. A newly exported old period is not new performance.
- Search Console clicks are search clicks, not GA4 sessions, visitors or Keyword Planner monthly search volume.
- Use the report's totals for totals, not summed named query rows: anonymized queries may be omitted. State row limits and incomplete coverage.
- Compare equal, non-overlapping windows. Recently restored calculators require time for recrawling and measurement; a pre-release window cannot show the release's effect.
- Rank opportunities using observed US intent, current functionality and realistic competition. Do not promise 1,000 visits per day from impressions, positions or a small CTR sample.

No website HTML, canonical, indexing policy or calculator logic is changed by this access report. The current deployment remains the previously verified release, not a newly optimized site version.

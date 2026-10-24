# Analytics Metadata and Measurement Scope

Follow-up after explicit owner approval on October 24: Site search enhanced measurement has now been disabled for the matching NS Calculators stream. Reopened settings confirm persistence; a fresh intercepted SDK run retained page_view and calculator_submit without view_search_results or the synthetic search marker. See `analytics-site-search-disabled-2026-10-24.md`. The account-setting limitation below records the state before approval, not a current outstanding request.

Date: 2026-10-24. No GA4 account/report settings were modified.

## Finding and Bounded Fix

The existing Google tag used a default config call, without an explicit page URL/referrer override. Added supported `page_location` and `page_referrer` context to that existing stream and global defaults. Page location is the current origin plus pathname, without query or fragment. Referrer is only the HTTP(S) origin, without its path, query or fragment; empty/malformed/non-HTTP referrers become empty. The existing stream ID, script, custom event names, calculator behavior, theme and plugins remain unchanged.

This narrows those two metadata fields. **It is not a complete analytics privacy fix.** A real Google SDK test also found automatic `view_search_results` collection of a URL `q` parameter as `ep.search_term`, independently of the sanitized page URL. Do not infer that overriding page_location suppresses all automatic events, campaign extraction or other fields.

## Test Evidence

Used the generated Area page at a locally intercepted `https://ns.test/` origin with invented query/fragment/referrer markers. Loaded the existing stream's public Google SDK. Every analytics collection request was intercepted and fulfilled locally with HTTP 204 before reaching Google; other non-tag third-party requests were blocked. No real account identifiers, personal input, visitor cookies or production conversion hits were used.

Observed page_view and calculator_submit payloads carried `dl=https://ns.test/area-calculator/` and `dr=https://www.google.com/`, with no query/fragment in those fields. The automatic view_search_results payload had the same minimized dl/dr but retained the invented q marker in ep.search_term. This residual was explicitly recorded rather than hidden by relaxing an all-fields privacy claim. No raw SDK payload or generated client identifier is committed.

The test was not a GA4 DebugView/report verification, a consent-compliance audit, an attribution accuracy study or proof about every later SDK event. External referrer-path detail is intentionally lost. Changes to campaign attribution must be evaluated separately; this code does not promise that all campaign parameters stop being processed.

## Approval Needed

Requested explicit permission to turn off **Site search** enhanced measurement for the NS Calculators GA4 web stream. No approval has been assumed and no account toggle has been changed in this release. The site's actual search operates in page memory, so this URL-parameter event is not a reliable measure of that workflow. Disabling automatic site-search collection would leave website search functionality, ordinary page views and existing Calculate events intact, subject to verification after the approved setting change.

Google documents [configuration fields](https://developers.google.com/analytics/devguides/collection/ga4/reference/config) and [enhanced measurement's automatic query-parameter search detection](https://support.google.com/analytics/answer/9216061?hl=en). [Data redaction](https://support.google.com/analytics/answer/13544947?hl=en) is a separate account-level control, not something this page-context override certifies.

## KPI Contract

- Search Console clicks: Google Search result clicks, not site sessions or unique visitors. The last verified US September 24-October 21 baseline remains 4 clicks / 5,933 impressions, not 5,933 visits.
- Natural-search visits: a GA4 session-based report scoped by session source=google and medium=organic is a diagnostic for Google organic visits. Report country, timezone, interval, sessions and users separately. Do not use all Organic Search traffic as exclusively Google, or silently substitute sessions for people.
- calculator_submit: an interaction/attempt event. Invalid Calculate attempts can fire it; valid room add/subtract actions also use it with interaction_type. It is neither a unique visitor count nor proof of a successful answer. No key-event/conversion configuration was changed.
- The 1,000-daily-organic-visit objective is still unproven. No GA4 report totals were inspected in this run, so sessions/users are unknown, not zero. New collection code is not evidence of traffic growth or completed goal attainment.

## Verification

78 Python tests and six rendered-context JavaScript scenarios pass. Tests cover context binding, source/referrer minimization, malformed values and disabled analytics. The real-SDK interception test verifies both the bounded fix and the remaining automatic search-term path. The 302-URL indexation/crawl-path gate and the desktop/mobile Area boundary regression still pass. No title, formula, sitemap, robots, canonical, CSS or shared calculator-bundle change was made. No external submission, outreach, payment or new page was made.

# US Google Organic Session Baseline

Observed October 25, 2026, in the existing signed-in GA4 Traffic acquisition report. The NS website stream URL and measurement ID were matched before using the report. Only aggregate cells and a sanitized landing pathname are retained; no account identity, raw query strings or user-level records are published.

## Verified Scope and Result

Visible dates: September 27-October 24, 2026, inclusive (28 days). Property reporting timezone was not inspected. Applied temporary report-view filters with AND: Country exactly United States, Hostname exactly nscalculators.com, Session source/medium exactly google / organic. These do not change collection settings or save a new account filter.

The filtered grid shows one session, zero engaged sessions, seven seconds average engagement per session, five events across all event types, and zero key events. Adding the visible Landing page + query string secondary dimension shows one row: Organic Search, `/finance-calculator/`, one session, zero engaged sessions, five events. No query string appeared in that row. The row session count reconciles with the report total.

Machine-readable transcription: `exports/us-ga4-baseline-2026-10-25.json`. This is a UI observation, not an API response or exported raw dataset. The daily mean is 1 / 28 = approximately 0.036 reported sessions, not daily unique visitors or verified people. Data collection completeness, consent effects, bot classification and property timezone remain unverified.

## Decisions

- The 1,000 daily organic-visit objective is not established. Global sessions, Bing organic sessions, GSC impressions and all-source users must not be substituted for US Google organic visits.
- Do not prioritize Finance above Area from a single landing session. Retain the independently verified GSC opportunity queue: Area, comparable-based car-price intent, Ratio and Fuel Cost. Their impression counts indicate observed site visibility, not market-wide search volume.
- Do not infer conversion failure from zero engaged sessions or key events. The sample is one; existing calculator_submit records attempts, and this report does not demonstrate successful result rendering or key-event configuration.
- Preserve the October 24 calculator fixes and snippets while collecting a post-release window. No additional title, layout or index-scope churn is justified by this report.

## Next Measurement Contract

After October 31 is available in both products, inspect an absolute October 25-31 window rather than comparing overlapping rolling totals. Allow each report's processing delay and record its actual availability; a calendar date is not proof data are settled. Preserve each product's displayed timezone or explicitly mark it unknown.

In GSC, use United States and Web (text-based), retaining clicks, impressions, CTR and position separately. In GA4, reuse the exact country/hostname/session-source-medium filters above and record sessions and landing pages. Compare the two products descriptively, not as interchangeable counts or a causal tracking-loss calculation. If sufficient settled data are unavailable, retain the existing baseline rather than inventing a growth rate.

Inspect exact query-to-page breakdowns before modifying pages; separate query and page export tables cannot be joined into observed pairs. Review Area first because the previous US GSC window reports 590 impressions for the exact query at position 8.29. A seven-day observation is not by itself a controlled experiment or proof of ranking lift.

## Scope of This Run

No HTML, CSS, calculator formula, analytics event, account setting, sitemap submission or outreach changed. Only the baseline and the growth plan were updated. This measurement recovery changes the next decision: keep traffic metrics distinct and wait for a post-release window instead of expanding pages from one session. The approved Site search disablement remains documented separately in `analytics-site-search-disabled-2026-10-24.md`.

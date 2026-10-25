# Preserve Calendar Dates in US Time Zones

Date: October 25, 2026

## Evidence and Reproduction

Revalidated the untouched September 24-October 21 US/Web Search Console archive against its committed source hash and scope checks. The named query `day counter` has six impressions, zero clicks and reported position 55.67. This is observed site visibility, not US market search volume. No query-to-page mapping was inferred from the separate exported page table.

Reviewed the existing calendar-engine routes as candidate tools. On production `/date-calculator/` in America/Los_Angeles, entering January 1 through January 2, 2026 returned one day but identified the end as Thursday; the table displayed December 31, 2025 and January 1, 2026. The entered endpoints are Thursday and Friday, January 1 and 2. The bug is significant for the intended US audience independently of this small search sample.

The engine parsed date-only ISO inputs into UTC timestamps, then formatted them in local time. MDN's [Date.parse reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/parse) documents that a date-only standard input implies UTC. Mixing that representation with local date formatting shifts labels backward in negative UTC offsets. Explicit UTC representation and formatting are used here only to preserve calendar dates, not to claim physical elapsed hours or geographic time-zone conversion.

## Changes

- Strictly validate complete Gregorian calendar inputs from 0001 through 9999, including round-trip rejection of impossible dates. The Unix epoch value zero remains valid.
- Use one pure calendar-day projection for the primary answer, summary and table. Date labels and weekdays refer to the entered dates independently of the viewer's time zone.
- Preserve signed differences, including zero and reverse ranges. Show the absolute span in complete weeks and remaining days, with direction separately identified.
- Clear invalid/stale results on empty inputs and Clear. Remove the mixed-unit days/weeks/average-month chart from this engine; it was not a composition or a comparable-unit series.
- Add shared original method copy with worked leap-day, reverse-range and inclusive-count examples, plus contextual Age and Time Duration links. Explain calendar-day, daylight-saving, holiday and historical-calendar limitations; no business-day or deadline algorithm is claimed.
- Use a scoped two-column result summary with 18px strong values, minimum-width safeguards and wrapping after the maximum supported range reproduced layout overflow. No site-wide palette or typography redesign.

Existing engine scope is three indexable routes: `/date-calculator/`, `/day-counter/`, `/day-of-the-week-calculator/`. This fixes their shared calendar results; it does not certify that all three distinct user journeys have feature parity with any competitor. Their URLs, titles, descriptions, canonicals and index status are preserved. The pregnancy/due-date engine was left separate and is not certified by this fix.

## Verification

- 97 Python tests pass, including two new shared-route and scope regressions.
- 38 new JavaScript cases pass independently under America/Los_Angeles, America/New_York and UTC, also enforced in CI. Cover leap/non-leap centuries, year 0001, years 0099-0100, year 9999, full supported span, DST calendar boundaries, reversed/same dates, malformed/impossible values, rendering, invalid recovery and no mixed-unit chart.
- Weekdays at the early/century/upper boundaries and the 3,652,058-day full-range difference were independently cross-checked with Python datetime.
- All existing JavaScript suites pass with the rebuilt bundle.
- Local Playwright checks all three routes at widths 1366, 390 and 320 in both US time zones (18 combinations): date/weekday consistency, leap day, spring/fall calendar spans, Wednesday labels, maximum span, reverse/same date, invalid/Clear/recovery, no horizontal overflow, first-screen Calculate control, self-canonical/index status and no page errors. Screenshots and `doc-work/verify-calendar-days.cjs` remain ignored, not production assets.
- Full static gates still validate 302 sitemap URLs, 284 indexable calculator records, 285 application nodes, 296 breadcrumb trails and 1,161 breadcrumb targets. The builder validates 140,698 internal links. JS fingerprint ca3c8f99318ad219 matches 4,902 script references; scoped CSS fingerprint 6e3eeee2660b7280 matches 5,026 stylesheet references.

This is a reproduced correctness and content-clarity improvement. No search lift, external link acquisition, new market volume, field Core Web Vitals improvement or goal attainment is established. No new page, submission, account setting or outbound campaign was created.

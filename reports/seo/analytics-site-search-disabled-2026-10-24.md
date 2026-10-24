# Approved Site-Search Collection Change

Completed: October 24, 2026, after the owner explicitly approved disabling Site search enhanced measurement.

## Identity and Scope

Used the existing signed-in Google Analytics browser session. Verified the web stream URL is `https://nscalculators.com` and its measurement ID matches the site's existing `G-19CY1VWHFM`. No new account, permission, credential, API secret, property or data stream was created.

Changed only the **Site search / website search** enhanced-measurement switch from on to off, then saved. Reopened the editor and confirmed it remains off. The overall enhanced-measurement switch, page views, scrolls, outbound clicks, form interactions, video interactions and downloads retain their prior enabled states. No data-redaction, retention, key-event, campaign, billing or other account setting was changed.

## Verification

The settings screenshot in the conversation shows Site search off while page views and other displayed switches remain on. This screenshot is not uploaded to the public repository.

Repeated the real-SDK interception test in a new browser context using an invented URL query marker, synthetic referrer and the locally routed generated Area page. All collection requests were fulfilled locally with HTTP 204; no test pageviews or conversion events were delivered to production Analytics.

Observed after the setting change:

- `page_view` still generated.
- `calculator_submit` still generated after Calculate.
- Both carried the minimized page location and origin-only referrer from the deployed site code.
- No `view_search_results` event or synthetic query marker appeared in this tested load/Calculate sequence.

Before the approved change, the same test observed `view_search_results` with the invented q value in `ep.search_term`. The account change resolves that reproduced collection path in the fresh-SDK test. It is not a comprehensive privacy/consent audit, a guarantee about every browser with cached tag configuration, or deletion of historical data. Existing website search remains unchanged because it is implemented independently in the site's own JavaScript.

## Operational Record

No website HTML, CSS, formulas, search logic or event names changed in this follow-up. Only the authorized account toggle and this documentation changed. No new traffic or ranking outcome is inferred, and the daily-1,000 organic-visit objective remains unproven.

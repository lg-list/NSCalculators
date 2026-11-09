# US search measurement triage — November 9, 2026

The previous turn completed verification of compute-chart release 4530d06a50: Pages run 40899718958 succeeded and all nine production page/viewport checks passed. This turn recovers current first-party evidence instead of continuing edits based solely on the October 25 cutoff.

## Readable report and material finding

The in-app browser binding became readable again. The visible NS property, Web text search, US country chip and October 11–November 7 chart dates were checked together. It shows **2 clicks, 5,601 exact-tooltip impressions** (rounded display 5,600), and displayed average position 63.7. Selected named queries include 401k calculator 132 impressions, trade-in calculator 112, personal loan calculator 57 and boat loan calculator 46, all zero clicks in those rows. These are incomplete query aggregates, not verified landing-page pairs or market volume.

Before applying the US/date filter, the existing report showed November 1–7, no country filter, **0 clicks and 6 impressions**, average position 4.3 and no named query data. This is a material low-volume observation requiring follow-up. It cannot be relabeled US demand, used to infer that US rankings improved to 4.3, or attributed to any deployment. Named query absence does not mean no searches occurred.

Sanitized observations are recorded in `exports/us-search-ui-observation-2026-11-09.json`; no account identity or private browser snapshot is published. These numbers are UI-observed and **not reconciled CSV totals**. The prior September 28–October 25 period overlaps the new 28-day window; no before/after percentage or causal treatment result is calculated.

## Export limitation and decision

The CSV download action timed out and reset the browser kernel. A single attempt to recover the existing tab also timed out. The latest matching named performance ZIPs in Downloads are still October 28; no November export was found. Do not repeat the download solely because the observation expired, assume completion, or claim that daily/page/device data was obtained. Browser work was closed with its completion summary. No paid connector was retried, account changed, sitemap submitted or indexing request made.

Area's earliest review date has passed, but a calendar date alone does not supply the post-change exact-query/page data needed for a title rewrite. Keep its title stable until a current Area query/page report is readable. The changed top-row mix and recent low-volume observation make measurement and indexing diagnosis a higher priority than another keyword expansion.

Next: obtain completed daily data across late October and early November, then read the NS indexing overview and inspect a small set of affected URLs if indicated. Confirm the break date, geography and current query/page coverage before attributing it to content, algorithms, demand or technical access. Public HTTP 200/self-canonical checks from October 29 cannot establish today's Google index status. A user-provided current Search Console CSV export would also unblock this analysis; the separate US Keyword Planner file remains pending.

No website content or indexing setting is changed by this evidence update. The 1,000 daily organic visits objective remains active and unproven. This turn is progress through newly observed data and an evidence-based reprioritization, not a completed growth result.

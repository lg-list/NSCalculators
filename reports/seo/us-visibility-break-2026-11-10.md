# US visibility break — November 10, 2026

Previous turn was progress: 26004462dc deployed conversion-result semantics with successful exact-commit Pages and 12 live browser checks. This turn returns to first-party measurement rather than treating engineering releases as traffic growth.

## Verified observation

Rendered Search Console, NS domain, Web text, USA, October 12-November 8: **2 clicks / 5,512 impressions**, displayed average position 64.2. All 28 daily rows were read over three pages and transcribed into `exports/us-search-daily-observation-2026-11-10.json`. The rows sum exactly to both headline counts. No account identity, raw private UI or credentials are included.

November 2-8: **0 clicks / 5 impressions**, with 3 impressions on November 2, 2 on November 5 and zero on the other five days. The page table shows no data. Do not attribute those five impressions to a named page, infer why the table is empty, or claim that displayed position 3 demonstrates ranking recovery.

The visible boundary is October 26-27: October 25 had 675 impressions, October 26 had 164, October 27 zero and October 28 one. Every day October 29-November 1 is zero. This is materially different evidence from comparing overlapping 28-day totals. It predates November's conversion fixes and cannot be their consequence. It does not establish the exact hour, Google penalty, sitewide deindexing or a causal deployment.

Top visible 28-day queries include 401k calculator (132 impressions), trade-in calculator (108), personal loan calculator (57), trade in value calculator (48), boat loan calculator (46), new vs used car calculator (40), trade in car values calculator (37), calculate 401k (36), trade in car loan calculator (30) and car trade in value (29); each visible row has zero clicks. These are query observations, not verified query/page pairs or market search volumes. No US Keyword Planner export newer than the existing October 28 Search Console files was found in the bounded Downloads inventory.

## Triage and decision

The November 6 indexing snapshot previously showed 290 of 305 sitemap URLs indexed, with two pre-restoration noindex records, eleven discovered-not-indexed examples, one crawled-not-indexed and one historical GitHub canonical selection. That report does not establish a comparable historical indexing trend and cannot explain this performance break by itself.

Git history contains numerous October 26-27 calculator improvements and a shared asset optimization release (f1b797434e, October 26 20:06 +08:00). A focused diff from d2546d1b33 through f07dec8071 found no added/removed canonical/noindex/robots configuration; the matching canonical line was only an Area CSV export reference. This bounded text check is not an exhaustive deployment, rendering or host configuration audit. Do not roll back a release merely because its date is near the daily transition. Google reporting dates and commit timezone are not aligned sufficiently for an hourly causal claim.

Public Playwright HTTP recheck completed for all 305 current sitemap destinations: no response/canonical/noindex/title/description/H1 failures or duplicate titles. Evidence: `exports/public-indexation-recheck-2026-11-10.json`. This evaluates current public HTML signals only, not current Google inclusion, robots path-rule semantics, historical availability or rendered functionality. Keep it separate from the Google observation. Do not remove intentional quality noindex gates, bulk-refresh dates, submit indexing, or expand pages in reaction to a low-impression label.

Priority now: (1) reconcile an equal-window US before/after page breakdown around October 27 and inspect Google's stored canonical/crawl evidence for formerly visible URLs; (2) read Search Console manual-action/security reports without changing settings; (3) check historical deployed artifacts for a reproducible technical regression if those findings identify one; (4) use verified US query/page demand for further calculator upgrades. Preserve current title experiments until current comparable evidence exists. The existing site remains available; a current HTTP pass would not rule out a historical outage or ranking suppression. No new keyword pages, public SEO claims or formula changes in this measurement turn. Goal remains active and far from established 1,000/day.

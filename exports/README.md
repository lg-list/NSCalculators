# Keyword Data Scope

The source geography was audited on 2026-10-20. The existing Keyword Planner
statistics and paid forecast both target **China**, not the United States.
Do not use their volumes, bids or priority labels as US demand validation.

| File | Meaning and permitted use |
| --- | --- |
| `keyword-stats-positive.json` | Historical China averages, August 2025-July 2026; preserved unchanged. Not US volume. |
| `keyword-stats-provenance.json` | Verified source geography, periods, original-file hashes and a canonical-JSON fingerprint of the derived rows. |
| `seo-keyword-strategy-2026-09-05.json` | Historical strategy; its intended US audience was incorrectly combined with China metrics. See its correction block before using it. |
| `seo-priority-keywords.csv` | Historical all-route mapping, with legacy China-based volume and priority fields. Not a current US priority queue. |
| `seo-priority-keywords-indexable.csv` | Canonical URL mapping with explicit metric country and a separate US-volume column. A blank US value means unknown, not zero. Legacy priority labels are not US ranks. |
| `keyword-page-map.json` | Historical source-volume-to-page mapping. Country and period are explicit; `us_monthly_searches` is null until US data is verified. |

The original statistics export has 2,354 keyword rows, 175 positive-volume rows,
and a 9,650 sum of its China monthly averages. The old derived positive JSON has
174 rows and a 9,600 sum: `f 150 bed dimensions` was excluded historically.
Neither sum estimates US market size or visits; close variants can also overlap.
The excluded term's working calculator is not removed by this audit.

The forecast models an October 2026 China paid-search campaign with a $30 daily
budget. Its 381.76 clicks, 6,468.97 impressions and $930 cost are modeled campaign
outputs, not organic demand, actual clicks or actual spending. Device rows and
the China location row repeat the same campaign breakdown; do not add them to
the campaign-total row.

## Current US Decisions

Use explicitly country-filtered US Search Console data for observed query and
page performance. Search Console impressions describe this site's visibility,
not the whole market's monthly searches. Omitted/anonymized query coverage must
be retained when interpreting a query shortlist.

Before restoring Keyword Planner-based US prioritization, obtain historical
metrics with United States targeting, Google network, the latest 12-month date
range, keywords and average monthly searches. Preserve the source and verify
its location row/settings before changing the provenance metadata. A new or
modified metric file with unmatched provenance is treated as unknown geography.

Ads competition measures advertiser activity; it is not organic SEO difficulty.
Homepage featured tools are editorial selections, not a claim about measured
popularity. Existing indexable routes are deliberately preserved in this
correction rather than deindexed because US volume is unknown.

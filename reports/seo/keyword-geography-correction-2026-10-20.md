# Keyword Geography Correction

Audited: 2026-10-20. Intended audience: United States.

## Material Finding

The earlier strategy combined a US target audience with China keyword metrics.
That interpretation is withdrawn. Low numbers in these files do not establish
low US demand, and the paid forecast does not estimate organic traffic.

No advertising account, campaign, billing setting or external submission was
changed during this audit.

## Evidence

| Source | Observed scope | Meaning |
| --- | --- | --- |
| `Keyword Stats 2026-09-02 at 10_40_43.csv` | Period August 2025-July 2026; segmentation includes China, with the same 9,650 total as All | Historical metrics for the selected China targeting, not US volume |
| `Keyword Forecasts 2026-09-05 at 09_28_21.csv` | China, location ID 2156; October 2026; Google Search; $30/day budget | Paid campaign forecast, not natural search demand or actual spend |

The statistics file has 2,354 keyword rows and 175 positive-volume rows. The
previous derived JSON has 174 rows, totaling 9,600, because `f 150 bed dimensions`
was omitted historically. This audit does not remove that working calculator.

The forecast's campaign-total row models 381.76 clicks, 6,468.97 impressions and
$930 cost. Device and location breakdowns repeat that total; they must not be
added to it. Original file hashes and derived-data fingerprints are recorded in
`exports/keyword-stats-provenance.json`.

Google's [Keyword Planner documentation](https://support.google.com/google-ads/answer/3022575?hl=en)
states that historical averages depend on selected geography and network, while
forecasts account for advertising conditions including budget. Its competition
column concerns advertisers, not organic ranking difficulty. USD currency alone
does not establish US geographic targeting.

## Corrections Applied

- Preserved raw historical values while adding explicit source country, period
  and separate US-volume fields to current mappings. Unknown US volume is
  blank/null, never an invented zero.
- Data fingerprints prevent a modified file from silently inheriting a verified
  geographic label. Missing or unmatched provenance receives unknown geography.
- Removed China volume and Ads competition from US keyword scoring. A US volume
  score requires verified US provenance; Ads competition no longer discounts it.
- Replaced the homepage's implicit foreign-volume popularity ranking with
  explicitly editorial featured tools. Layout, theme and calculation code stay
  unchanged.
- Kept the existing reviewed indexable pages stable. A geography correction is
  not a reason to mass-deindex useful tools.
- Added a US-filtered Search Console measurement queue separately from the
  historical Keyword Planner mapping. Search Console impressions remain site
  visibility, not total keyword market demand.

## Current Evidence and Next Action

The settled US Search Console window of September 20-October 17 has 4 clicks and
4,760 impressions. Named query/page rows cover 67.33% of impressions and only
25% of clicks, so an apparent absence in that query table is not zero demand.
Recently changed priority pages need a settled post-deployment observation
window rather than repeated same-day snippet edits.

Obtain a new historical-metrics export with **United States**, **Google** network,
and the latest 12-month range. Include keywords and average monthly searches,
and preserve the location evidence with the source. Do not substitute the
campaign forecast for historical metrics. Do not re-label the China file as US.

Until that export is verified, use US-filtered Search Console and demonstrated
user-task gaps for improvements. No new high-volume US cluster or 1,000 daily
visit forecast is justified by the old China data.

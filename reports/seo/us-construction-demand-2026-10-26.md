# US Construction Keyword Demand Review

Date: October 26, 2026. This research changes the next work queue; it does not change public HTML or establish a traffic gain.

## Source and Method

Used the local Codex in-app browser to inspect Google Trends Explore with **United States / Past 12 months / All categories / Web Search**. All four English search terms were verified in the rendered UI. English interface language is not a search-language filter. No Ads account, paid service, external submission or private-account setting was changed.

First compared unquoted terms, then edited the same report's input fields to quoted consecutive phrases. Google's [search tips](https://support.google.com/trends/answer/4359582?hl=en) explain that quoted phrases can still have words before or after; they are not an exact whole-query filter. Google's [data FAQ](https://support.google.com/trends/answer/4365533?hl=en) explains normalization and sampling: the indexes below are not monthly searches, traffic, CPC, share of market or organic difficulty.

Archive: `exports/us-construction-trends-2026-10-26.json`. It contains the public source URLs, exact UI filters, 53 weekly rows converted from displayed English dates to ISO dates, relative averages, separately typed related-query observations and exclusions. The ordered weekly-row JSON has matching FNV-1a-32 fingerprint `ee38dc88` in the browser extraction and local archive; this is a transcription check, not a cryptographic security claim. All dates advance exactly seven days. The week starting October 25 may be incomplete and is excluded from calculated means, leaving 52 weeks.

## What the Comparison Shows

| Consecutive phrase | Displayed average index | Calculated mean of 52 complete weeks | Decision |
| --- | ---: | ---: | --- |
| area calculator | 11 | 11.2115 | Keep leading site-level quick-win observation queue |
| square footage calculator | 15 | 15.0000 | Review distinct floor/roof task routing |
| flooring calculator | 1 | 0.6731 | Retain existing workflow; do not infer zero market volume |
| concrete calculator | 77 | 77.2500 | Next broader demand-backed existing-tool audit |

These four series use one common comparison scale. Concrete's complete-week index remains between 45 and 100, with high spring/early-summer values in this single-year sample. This is descriptive, not a seasonal forecast or proof that the head term is easy to rank for.

The unquoted report displayed averages 50/10/6/54 and surfaced unrelated area/retailer/calculator-associated searches. Constraining the phrases changes the comparison and its normalization. Do **not** describe Area as losing a percentage of demand by subtracting 50 and 11, or divide indexes across the two reports to estimate volume. Related-query widgets can still surface different intents even when a head phrase is quoted.

## Actionable Long Tails and Exclusions

- Concrete associated Rising queries include `80lb bag of concrete` (+190%), `concrete calculator app` (+70%) and `80lb concrete bag` (+60%). These are relative changes without an absolute base. Audit the existing `/concrete-volume-calculator/` for actual volume, units, bag-yield and full-package behavior before changing content. A manufacturer-specific bag example needs a verified primary yield source; do not create 40/60/80-lb clone pages or make structural strength recommendations.
- Square-footage associated Rising queries include `roof square footage calculator` (+50%), `lawn square footage calculator` (+50%) and `roofing square footage calculator` (+40%). Check whether existing Square Footage/Roof Pitch workflows support the task and route users accordingly; a pitch angle alone is not roof area, and measured rectangles are not a satellite/map drawing tool.
- Area associated Rising queries include `rhombus area formula` (+140%) and `lawn area calculator` (+80%). Check existing formula/input coverage before claiming those intents are served. Do not turn one related-query observation into a new indexable page.
- Flooring's visible related widget is **Top**, not Rising: square feet / vinyl / cost / laminate show indexes 100/96/80/71 within that widget. These are neither growth percentages nor on the same scale as the time-series average. Keep one existing coverage/boxes/cost workflow until a distinct material-specific need is validated.
- Exclude `concrete cowboy` (entertainment), Schengen queries (travel-day/geographic intent), `bsa` (ambiguous/possible medical intent), and Home Depot navigation (retailer brand, no affiliation). Related terms are not automatic publishing instructions.

## Priority and Publication Boundary

Machine-readable queue: `exports/us-construction-keyword-map-2026-10-26.json`. It maps primary/secondary candidates to **four existing URLs**, separates evidence from editorial decisions, sets monthly search volume and organic difficulty to null, disables auto-publishing and gives each brief a functional/source/testing gate.

Keep two distinct priority lenses: the existing Area query has observed US GSC exposure near page one (590 impressions, position 8.29 in September 24-October 21), while Trends suggests Concrete deserves the next broader demand/functionality audit. Trends does not replace those site-level rankings or justify churning recently revised Area snippets. The next settled observation window remains October 25-31 only after both GSC and GA4 make it available and processed.

The owner agreed to upload an actual US historical Keyword Planner CSV; it has not arrived or been validated. Do not fill unknown monthly volumes with Trends indexes, treat Ads competition as organic difficulty, or revive the old China-targeted metrics. No public keyword-signal blocks, new pages, indexed thin content, backlinks, ads or traffic-uplift claims were added.

## Verification

Validated JSON syntax, 53 unique weekly dates, seven-day spacing, all four values per row as integers in 0-100, 52 complete weeks and recalculated means. Browser/local row fingerprints match. All four mapped calculator targets exist and remain indexable; related guide/tool paths are checked against the current build. Existing public calculator/CSS assets, titles, canonicals and 285/303 calculator/sitemap scope are unchanged. Run the existing regression and build gates before committing; verify the resulting Pages job and unchanged live priority URLs after deployment.

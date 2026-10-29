# Used-car comparable benchmark and channel chart — October 29

Previous turn made progress with a full public audit of all 305 sitemap URLs. That found no public HTTP/HTML indexation-signal defect; it did not recover Google indexing data. This turn addresses an existing verified US task rather than creating a new keyword page.

## Evidence and actual gaps

The October 24 exact-query Pages observation, September 24–October 21 US Web, linked `car price estimate` to Used Car Value (25 impressions, zero clicks; query aggregate position 11.7). See `used-car-condition-2026-10-24.md` and original query/page evidence. This is a small sample and is not a fresh October 29 report or US market search volume. The existing title and targeting remain stable.

The page required a single user-entered retail benchmark without helping summarize comparable asking prices. More seriously, its generic chart displayed retail $20,400, private-party $19,176 and trade-in $17,952 as slices totaling $57,528. Those are alternative channel estimates, not additive components. The new bar chart compares independent amounts and has no total/percentage center label.

## Delivered functionality and scope

An optional collapsed tool accepts 3–20 USD asking prices, one per line. It supports plain dollars or correctly grouped US dollar amounts and up to two decimal places, rejects nonpositive, malformed, nonfinite or excessive amounts, and limits input size. Blank lines are ignored. Median is calculated from sorted integer cents; an even-sample half-cent is rounded upward to a cent. The $21k/$22k/$24k example gives $22k; adding $60k gives $23k. Outliers are not automatically removed and the tool cannot determine which listings are comparable.

Draft edits do not update the benchmark. The explicit apply button changes only that field, reports the entered count/range and recalculates using unchanged adjustments. Invalid input preserves the previous benchmark with a corrective status. Clear removes draft prices and stale applied status. Enter in the textarea inserts a line break. No listing service, vehicle API, VIN feed or external price request is added. Inputs are not placed in a URL, persisted, or included in new analytics events.

Original guidance explains consistent year/model/trim/mileage/condition/locality and selling channel, duplicate listings, asking versus transaction prices and double adjustments. [KBB's own valuation FAQ](https://www.kbb.com/faq/values/), freshly reviewed October 29, independently distinguishes selling channels and vehicle-specific inputs. This tool does not reproduce KBB data, provide an offer or certify appraisal/rollover/insurance values. The median is our transparent summary of user-selected inputs, not a sourced market estimator.

Scoped compact spacing and labels retain 16px number inputs and the current theme. Calculate and the primary answer are visible on the tested 320px mobile screen. No title, description, canonical, route, sitemap or indexation-policy changes. The new helper adds about 1.85KB decoded to the shared runtime; no performance improvement is claimed for this feature. Build hashes update for both registered specialized files as well as the full asset.

## Verification

- 93 median, rounding, US-format, count/size and invalid-input cases; 80 existing used-car numerical/validation cases preserved.
- 137 Python tests, including page copy and independent-channel bar-chart contract; all 40 JavaScript suites pass.
- Browser at 1366/390/320: default/poor-condition estimates, explicit median application, draft preservation, unchanged adjustments, invalid-list preservation, Clear, textarea Enter, bar-chart type, zero/blank/error recovery and no horizontal overflow/runtime errors. Screenshots inspected at 320px. Browser suite is tracked as `scripts/verify_used_car_browser.cjs`.
- Final build passes internal links, indexation/schema and full/specialized/CSS fingerprints: 305 sitemap entries, maximum depth 3. All deployments require the exact workflow and production browser checks before claiming release.

No ranking/CTR uplift, field CWV improvement or 1,000-daily-organic-visitor result is established. Await a completed post-change Search Console window; no paid tool, outreach, account change or external submission was used.

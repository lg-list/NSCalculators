# Remaining sitemap exclusions — November 9, 2026

Previous turn was progress: commit 1c236e8847 deployed truthful Gravel/Mulch lastmod dates and independently verified live output. This continuation investigates the other 13 sitemap exclusions rather than repeating the aggregate counts.

## First-party findings

The November 6 sitemap-scoped Google report lists 11 discovered-not-indexed URLs, one crawled-not-indexed URL and one other-canonical URL. All examples are now captured in `exports/indexing-exclusion-details-2026-11-09.json`. These are property-wide indexing records, not American search volumes or a current performance trend.

Stored URL Inspection for Mortgage Payoff shows a successful smartphone crawl on October 14, indexing allowed and the correct new-domain user canonical, but Google selected the old GitHub Pages URL. Independent current Playwright HTTP checks show the old address already returns 301 to HTTP on the custom domain and ultimately reaches the matching HTTPS page with status 200 and self-canonical. This is a historical migration conflict; the observation does not prove Google has accepted the migration now. Do not remove a useful destination page or change Pages/account settings speculatively. Public evidence is in `exports/indexing-exclusions-public-2026-11-09.json`.

All 13 current destination responses are 200, in the sitemap, self-canonical, with one H1/title/description and no meta/header noindex. The 11 discovered examples have no applicable crawl date in the report. No claims of crawl-budget exhaustion, penalties or poor quality can be inferred from those labels alone. No account changes, validation, indexing requests or sitemap submissions were performed.

## Evidence-based improvement

Watts to Kilowatts is the only crawled-not-indexed page in this sitemap scope (October 15 last crawl). Its current copy was an interchangeable conversion template, including recipes and unrelated measurement warnings. Replace that text with power-specific guidance, explicit decimal SI conversion, common W/kW values, an original 1,500 W / two-hour example, kW-versus-kWh explanation, an illustrative energy-charge calculation and contextual links to the reverse conversion and electrical current tools. Rewrite its title/description to describe its actual conversion intent. No search-volume estimate is invented; selection is based on observed exclusion plus a confirmed content gap, not promised traffic upside.

Primary references checked November 9: [NIST SI prefixes](https://www.nist.gov/pml/owm/metric-si-prefixes) for decimal kilo and symbols; [EIA measuring electricity](https://www.eia.gov/energyexplained/electricity/measuring-electricity.php) for power versus energy. The $0.20/kWh price and device draw are explicitly illustrative, not market data. Nameplate/runtime limitations and VA-versus-real-power distinction prevent overstating the conversion's use. No calculation-engine, style or indexability expansion. Add a truthful November 9 lastmod for this significant content change, preserving the two October 26 restoration dates.

## Verification and next priorities

139 Python tests pass. The isolated build validates 140,812 internal links; production optimization leaves runtime and CSS fingerprints unchanged. Indexation (305 URLs), schema, calculator and stylesheet resource checks pass. Local Playwright checks at widths 1366, 390 and 320 verify no horizontal overflow, source/contextual links and results for 1,500 W, 60 W and 1,000 W; no page errors. XML contains exactly the two prior restoration dates plus this page's November 9 date. Exact-commit Pages deployment and live content checks gate release. This is not a complete engine boundary audit or proof of Google reindexing.

Next: monitor Mortgage Payoff's selected canonical on a later crawl; inspect the 11 discovered pages for specific functional/content gaps using observed US query demand where available; keep high-impression title experiments stable without comparable post-release query/page data. Remaining generic dashboard semantics and converter Clear behavior require a separate functional audit. A richer page does not guarantee inclusion, rankings or the 1,000/day target. Goal remains active and unachieved.

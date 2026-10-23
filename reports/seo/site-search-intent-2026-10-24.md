# Site Search Intent Matching

Release date: 2026-10-24. Initial checks: 2026-10-23.

## Evidence and Limits

An attempted public Google Trends comparison explicitly selected the United States and past 12 months. Google returned HTTP 429; no trend series or keyword demand was obtained. No rate-limit bypass, account change or paid service was attempted. Do not infer new US volumes or priorities from this failed request.

The existing US Search Console baseline for September 20 through October 17 recorded 24 impressions for `car price estimate` on the used-car page, average position 10.96. This is historical site visibility, not current market volume or proof that visitors typed the same words into site search. The other phrases below are usability test cases, not claimed search-log observations or volume-validated opportunities.

Production homepage tests showed no results for `gas cost calculator`, `elapsed time calculator` and `calculator mortgage`. A subsequent inspection of the live search-index data confirmed zero matches under the old exact-substring algorithm for all four phrases, including `car price estimate`, even though the corresponding tools already existed. Initial UI output for that first phrase was still blank while the index loaded; the separate artifact/data check resolves that timing limitation rather than treating the blank as a completed response.

## Change

- Normalize case, punctuation, whitespace and diacritics; match every query token against word prefixes, independent of word order. Rank exact titles and primary keywords ahead of looser matches, with deterministic tie-breaking and an eight-result limit. This is token matching, not an AI semantic or typo-correction system.
- Use current page meta descriptions for existing indexable tools in the internal search dataset. This makes existing wording such as used-car price estimates and elapsed time discoverable without publishing keyword variants as additional pages. Working noindex converters retain their existing descriptions and deduplicated representation.
- Compile the index once per page load rather than renormalizing all entries on each keystroke. Render titles and descriptions with DOM text nodes rather than HTML interpolation.
- Support Enter to open the leading result, arrow-key movement and Escape dismissal. Ignore stale asynchronous results, including responses that arrive after Escape.
- Distinguish a failed search-index request from a genuine empty result. The next query can retry; a successfully loaded index is reused. Added a region label and input/result association while retaining native links and focus behavior.
- Updated the independent homepage search-script cache version from `20261019d` to `20261023a`. No CSS, calculator bundle, title, canonical, indexation policy or sitemap scope changed.

## Verification

- 59 Python tests pass, including three description, discovery-scope and rendered asset-version regressions.
- 24 new JavaScript search cases pass: 10 actual-index query/ranking checks, four blank/no-result cases, three unavailable-route checks and seven synthetic normalization/ranking checks. The previous 453 JavaScript calculation and chart checks are retained.
- Playwright checks five queries at 1366, 390 and 320px; the leading results are Used Car Value, Trip Fuel Cost, Time Duration, Mortgage and the primary Millimeters to Rods route. Checks cover result limits, keyboard navigation, Enter navigation to a working calculator, clearing, overflow and page errors. Reviewed the mobile result screenshot.
- Controlled request-failure tests return a visible loading error instead of zero results; a second request recovers, Escape prevents late reopening, and subsequent queries reuse that loaded data. Simulations are test evidence, not a production outage claim.
- Full isolated build: 5,005 calculator routes, 284 indexable calculators, 302 sitemap URLs and 140,684 validated internal links. Search still represents exactly 2,456 unique routes and does not promote unfinished tools.
- Live pre-release index: 677,890 decoded UTF-8 bytes; updated artifact: 692,705 bytes, approximately 2.2% more due to refreshed descriptions. No payload reduction is claimed. A single Node lab run compiled the updated dataset in 31.15ms and ran 100 queries in 36.34ms; these are not mobile field metrics or a Core Web Vitals verdict.

This fixes an observed internal-discovery barrier. It does not establish higher Google rankings, conversion lift or progress to 1,000 daily organic visits. Fresh US search data remains needed for outcome measurement. No external indexing submission, outreach, spending or account modification was made.

# Shared Number Formatter Reuse

## Decision and Scope

October 24, 2026. The prior Ratio release was progress: committed, deployed and production-tested. This continuation follows the existing mobile-performance screening rather than changing another search snippet. That screening did not justify a renderer rewrite or minification dependency. No new loading or field Core Web Vitals failure is established here.

Code inspection found the shared F, USD and MONEY helpers constructing formatters repeatedly during every result/table update. A controlled browser comparison reproduced an avoidable synchronous calculation/rendering cost, especially for loan schedules. Reuse one number formatter per requested decimal precision and one currency formatter per requested currency, constructed lazily. This changes presentation implementation, not formulas, scheduling, event names, locale, currency options, defaults, layout or plugins.

## Controlled Lab Evidence

Chromium, 390 x 844 viewport, mobile/touch context and 4x CPU throttling. Both variants used the same generated HTML/CSS/JavaScript, except the three formatter helpers and their caches. All resources were routed locally; Analytics and other external requests were blocked. No synthetic production visits were generated. Network loading, geographic latency and cold first paint were not measured.

For each page, three fresh contexts per variant, seven synchronous `calc(engine)` invocations per context after initial loading. Variant order alternated between context pairs. The 21 calls per variant/page are repeated observations clustered within three contexts, not 21 independent phones or users. Timing includes calculation and synchronous DOM/canvas work; it does not include the following paint or constitute an Event Timing/INP measurement.

| Existing page | Original median (ms) | Cached median (ms) |
| --- | ---: | ---: |
| Mortgage | 18.8 | 7.0 |
| Loan | 72.6 | 11.4 |
| Area | 7.1 | 5.1 |

These are observations from this runner, not a guaranteed speedup or a ranking/traffic result. No field LCP, CLS or INP pass is claimed, and the previous mobile-performance report remains a separate screening baseline.

## Regression Evidence

- Added 366 output/reuse checks against the original formatting expressions, covering decimal precision 0-12, finite/nonfinite values, negative zero, rounding boundaries, large numbers, default USD, GBP/EUR/CAD and JPY/KWD formatting options. Invalid precision/currency behavior remains explicit. A 1,000-iteration repeat test constructs no additional formatter for already-used settings.
- All 82 Python and 1,605 JavaScript cases, including analytics context, pass on the generated site. This coverage is not certification of every formula on every URL.
- Browser text equivalence compares the entire calculator-layout text before and after the formatting-only change: seven pages (Mortgage, Loan, Area, Trade-In, Ratio, Body Fat, Fuel Cost), three widths (1366/390/320), 48 default/changed-input/model states including all three loan models. All hashes match; no browser errors or horizontal overflow. Screenshots were inspected locally.
- All 302 sitemap URLs retain canonical/index eligibility and crawl paths within three clicks. Scope remains 284 indexable calculators; 140,687 internal links validate. All 4,902 calculator script references and 5,026 stylesheet references match their generated asset versions. CSS remains unchanged.

The site still needs settled US Search Console and GA4 organic-session evidence to evaluate growth. The daily-1,000 organic-visit target is not achieved. No new pages, submissions, purchases, outreach or account changes were made. Deployment and production equivalence are verified after push in the execution close-out, not inferred from local tests.

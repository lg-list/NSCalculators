# Repeated mobile loading screen — October 29, 2026

Previous turn made progress: retirement task navigation commit `75de2cfe1fa0d0e24b0b96dd91113725b49a9cd3` deployed successfully in Pages run 40889416480, with all 12 production page/viewport checks passing. This turn measures the current production assets rather than assuming that a larger shared bundle is a field performance failure.

## Method and observations

`scripts/measure_calculator_loading.cjs` visits three production pages three times each in separate Chromium contexts. It uses 390×844 mobile emulation, 4× CPU slowdown, disabled cache, 150ms emulated latency, 1.6Mbps download and 750Kbps upload. Analytics, Tag Manager and Cloudflare Insights are blocked. PerformanceObservers remain active until 1.5 seconds after network idle. Initial JavaScript coverage is collected in the same run and adds instrumentation overhead. These are loading samples, not interaction or INP measurements, and this runner is not a controlled US region or physical phone.

Raw observations, profile, URLs and versions: `exports/mobile-loading-2026-10-29.json`.

| Page | Observed LCP range, ms | Median LCP, ms | TTFB range, ms | Longest loading task range, ms | Initial input top, px |
|---|---:|---:|---:|---:|---:|
| Area | 1120–1820 | 1672 | 572.5–847.1 | 142–175 | 500.25 |
| Mortgage | 904–1740 | 1220 | 277.2–966.8 | 208–224 | 305.41 |
| 401(k) | 932–2616 | 2068 | 269.4–1944.4 | 182–207 | 353.56 |

All nine responses were HTTP 200, with zero observed runtime errors, horizontal overflow or layout shifts during the limited observation window. A short window with no shifts does not prove full-lifetime CLS. LCP varied considerably, including one 2616ms 401(k) observation alongside a 1944ms TTFB; these samples do not isolate a server or script root cause.

All samples served calculator version `718d9bfce62c3877`: 500,087 decoded response bytes and 141,647 encoded bytes. CSS version `89eaa86f0de2ffbd` was 99,093 decoded and 15,714 encoded bytes. Transfer encoding and caching can differ elsewhere. JavaScript coverage uses source characters, not response bytes: 499,902 total characters, with 30,918 (Area), 31,244 (Mortgage) and 33,810 (401k) covered during initial loading. About 93% initially uncovered is evidence to investigate deferred engine loading, **not** permission to delete code: later controls, modes and events were not exercised for this measurement.

## Decision and next action

Do not modify the shared renderer or drop functions based on loading coverage alone. The current bundle already uses conservative build-time minification with global/property names preserved. No measured before/after experiment or field CWV evidence proves an additional compression or splitting change beneficial yet.

The next performance engineering candidate is a dependency-aware engine-loading prototype, isolated from production until it preserves initial answers, all mode changes, Clear, Enter and chart updates across every affected engine. Compare repeated throttled loading and interaction samples before choosing it for deployment. Do not substitute an artificially narrow smoke test for the full shared runtime contract.

This release adds a reproducible diagnostic and evidence only; public calculation, layout, metadata, canonical and indexation behavior are unchanged. The October 20 screen had different asset versions and only one sample per URL, so numerical differences here are not attributed to a regression or improvement. No field CWV pass, INP result, ranking benefit or traffic uplift is claimed. US keyword-volume data and later completed Search Console windows remain necessary for growth prioritization. No paid tools, account changes, external submissions or outreach were used.

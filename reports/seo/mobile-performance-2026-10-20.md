# Mobile Performance Screening: 2026-10-20

## Decision

Do not rewrite the calculator renderer, add a minification dependency, or change
input scheduling on the strength of bundle size alone. This screening did not
reproduce a slow first viewport or slow mortgage interactions. Continue measuring
and prioritize observed search-intent and calculation-quality gaps.

This is not a Core Web Vitals pass, a Lighthouse score, or evidence of better
rankings. CrUX field data remains unavailable in the connected tooling; no account
settings or credentials were changed.

## Method

- Public production URLs at commit `6b1f0a1d85`.
- Playwright Chromium, 390 x 844 viewport, touch/mobile emulation, fresh browser
  contexts and disabled browser cache through request interception.
- CPU throttled 4x; loading tests used 150 ms emulated latency, 1.6 Mbps download
  and 750 Kbps upload. Actual routing from this runner was not a controlled US
  regional test. CPU throttling is not a physical low-end-phone benchmark.
- Google Analytics and Google Tag Manager requests were blocked to avoid adding
  synthetic visits to campaign analytics.
- One navigation per URL; observations continued for 1.5 seconds after network
  idle. No scrolling or form interaction occurred during the loading samples.
- Largest Contentful Paint and layout shifts came from PerformanceObserver.
  No shifts were observed; these short samples do not establish lifetime CLS.
- Mortgage gesture measurements were a separate CPU-throttled run after loading,
  without network throttling. Event Timing used a 16 ms reporting threshold.
  Values below that threshold may be absent, not zero.

## Loading Observations

| URL path | FCP (ms) | Observed LCP (ms) | TTFB (ms) | Observed layout shifts | First input top (px) | Horizontal overflow |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `/` | 1060 | 1060 | 620.7 | 0 | 231.8 | No |
| `/area-calculator/` | 1448 | 1448 | 635.3 | 0 | 573.6 | No |
| `/car-trade-in-value-calculator/` | 1016 | 1016 | 484.9 | 0 | 408.6 | No |
| `/mortgage-calculator/` | 1288 | 1288 | 550.3 | 0 | 305.4 | No |

The first input was visible within the tested 844 px viewport on all four pages.
That does not imply that every field or the entire calculator fits one viewport.
Each sampled LCP element was introductory paragraph text, not a chart or image.

The shared calculator bundle was 457,797 decoded bytes and 119,334 encoded bytes
in these responses. The stylesheet was 87,590 decoded bytes and 14,014 encoded
bytes. These are observed response sizes, not a claim that every edge or browser
uses the same content encoding. No payload reduction was made in this audit.

## Mortgage Interaction Observations

| Gesture sequence | Longest reported event duration (ms) |
| --- | ---: |
| Calculate click 1 | 56 |
| Focus price, End, ArrowUp 1 | 64 |
| Calculate click 2 | 40 |
| Focus price, End, ArrowUp 2 | 64 |
| Calculate click 3 | 40 |

The longest initial loading task was 225 ms on the mortgage page under 4x CPU
throttling. It was not a 225 ms input event. The controlled gestures did not
reproduce that duration: event processing for Calculate was about 18-25 ms and
price increments about 36-40 ms, with reported event durations up to 64 ms.

Google's [INP documentation](https://web.dev/articles/inp) distinguishes loading
tasks from interaction latency, explains that lab results depend on the gestures
tested, and bases field evaluation on real-user page visits. These few gestures
do not establish field INP or cover every mortgage option or device.

## Follow-Up

- Preserve this as a screening baseline, not a numerical performance target.
- Re-run representative workflows after substantial layout, chart, or engine
  changes and compare repeated samples under the same profile.
- Use real-user evidence, when available, before prioritizing an INP rewrite.
- Test additional calculator modes and slower devices if users report delays.
- Do not attribute future traffic changes to this audit: it changed no public
  layout, calculation, content, or indexing policy.

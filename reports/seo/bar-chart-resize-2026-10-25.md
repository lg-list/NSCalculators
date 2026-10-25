# Avoid Height-Only Result Rebuilds

Date: October 25, 2026

## Reproduction and Scope

The production generic bar-chart resize listener called renderGenericFromEngine on every window resize, even when the chart's CSS width and device-pixel ratio were unchanged. This rebuilds summary cards and result tables as well as recalculating the projection. Browser viewport-height changes can occur during mobile browser UI or keyboard transitions, depending on browser behavior; the reproduction uses a controlled viewport resize, not a claim that every phone keyboard triggers a layout-viewport event.

Verified before the change on Area, Ratio and Fuel Cost at 1366, 390 and 320 CSS-pixel widths: changing only height from 844 to 600 produced one full generic render and one summary mutation in every state. All nine states retained the same answers, so the rebuild was unnecessary.

These existing pages have independently observed US Search Console demand. No new keyword volume, traffic attribution or ranking increase is inferred. This interaction refinement does not alter their titles or competing URLs.

## Change

Remember the actual CSS width and pixel ratio when each generic bar canvas is drawn, using a WeakMap keyed by the existing canvas. The existing animation-frame-coalesced resize listener now checks that geometry before requesting a result rebuild. Hidden, zero-width and absent bar charts do no work. Actual width or pixel-density changes still redraw at the new size. Calculation-triggered renders remain unchanged even at the same width, so changed input values are not suppressed.

No new library, visible design, formula, analytics setting, event, URL, indexation rule or CSS change. No delay/debounce was added to Calculate or input handling. The optimization is limited to generic bar charts; it does not claim to optimize all pie/line charts or eliminate all repeated calculation paths.

## Verification

- 95 Python unit tests pass.
- All JavaScript checks pass, including 12 new resize assertions in the existing chart suite: same-size/height-only, width change and remembered width, DPR change and backing pixels, hidden/revealed, zero-width, burst coalescing and absent canvas behavior.
- Local Playwright checks all nine page/viewport combinations above. Height-only changes produce zero generic renders and zero summary mutations; actual width changes produce one render. Full calculator-layout text is unchanged, chart pixels remain nonblank, canvas backing width matches CSS width times DPR, and no horizontal overflow or page errors occur.
- The same harness supports post-deployment verification: `node doc-work/verify-bar-resize.cjs --live`. Local captures and the harness remain in ignored doc-work, not production assets.
- Static gates validate 302 sitemap URLs, 285 apps, 296 breadcrumb trails, 1,161 breadcrumb destinations, 4,902 calculator-script references and 5,026 unchanged stylesheet references. JS fingerprint: 902d5ca224c38406; CSS: 61fa30ec0ab878ea.

Operation counts demonstrate avoided work, not measured field INP, LCP, CLS or Google ranking improvement. Current field CWV and a sufficiently sized post-release US organic window remain unavailable in this run. Preserve the separate GA4 and Search Console baselines and review the October 25-31 observation window when available.

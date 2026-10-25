# Bottleneck Calculator reliability review

Date: 2026-10-25. Scope: existing `/bottleneck-calculator/` only; preserve theme, plugins, canonical, snippet and indexation scope.

## Evidence and priority

An exact US Web Search Console query filter (`cpu calculator`, September 24 through October 21) and the Pages tab confirm this URL received one click from one impression at position 58. See `exports/us-cpu-query-observation-2026-10-25.json`. This is not inferred from separate query/page exports, not US monthly keyword volume, and not sufficient to move this cluster above the stronger Area opportunity. No new PC pages or hardware database were created.

Live reproduction found two reliability problems: planning uncertainty of 80% was silently capped at 50%, and 200 measured FPS against a 144 FPS target was described as within 5% of target and possibly frame-capped. The former misrepresented an assumption; the latter inferred something not established by the inputs.

## Changes

- Extracted a pure evidence calculation with strict finite numeric inputs and active-mode validation. Targets require at least 1 FPS, matching the existing input. Utilization is 0-100%; planning uncertainty is 0-50%, with out-of-range assumptions rejected, not clamped.
- Guarded nonfinite derived ranges and reciprocal frame-time ceilings. Positive very small or large supported outputs use scientific notation instead of rounding to a false zero.
- Distinguished target reached from near target (within 5% below); neither establishes a frame cap. Existing below-target frame-time and utilization heuristics are preserved, not presented as laboratory-validated hardware diagnoses.
- Disabled hidden mode inputs and added post-Clear recomputation, removing stale summaries and charts after invalid or empty inputs.
- Added original matched-benchmark and target-status examples. The uncertainty band is an entered assumption, not a statistical confidence interval. No universal bottleneck percentage, CPU/GPU model prediction or exact upgrade recommendation is claimed.

## Verification

- 84 dedicated JavaScript evidence, wording, range and validation scenarios pass; all existing JavaScript suites pass.
- 103 Python regression tests pass.
- Isolated build: 303 sitemap URLs, maximum navigation depth 3; schema contract checks 286 applications, 297 breadcrumb lists and 1,165 breadcrumb targets. All 4,903 calculator-script and 5,027 stylesheet references match versioned assets.
- Local Playwright checks at 1366px, 390px and 320px: first-screen Calculate, target/near-target distinctions, rejected 80% uncertainty with stale chart hidden, recovered 108-132 FPS planning range, disabled inactive inputs, Clear recovery, nonblank chart pixels, self-canonical, no page overflow or JavaScript errors. Analytics requests are blocked during QA.
- Calculator JavaScript fingerprint: `e231bb8b9a33f0f7`; CSS remains `cd300833995da830`.

## Measurement and release boundary

Do not use the incomplete October 24-25 search window to evaluate this change. Await settled, comparable US reporting before attributing ranking or traffic effects; a successful release does not establish growth or achievement of the 1,000 daily-visit aspiration. No Search Console submission, advertising, outreach or account/security setting change is part of this release. Deployment and live verification must be checked against the resulting commit before reporting completion.

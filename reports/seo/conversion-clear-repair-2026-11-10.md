# Conversion Clear repair — November 10, 2026

Previous turn was progress: 305172871b deployed power-specific content and captured the remaining sitemap exclusions. This turn follows the explicitly deferred converter Clear concern with reproducible public browser evidence.

On the live Watts to Kilowatts, Kilowatts to Watts, Days to Seconds and Kilograms to Stones pages, entering 1500, calculating, clearing and re-entering 1500 changed every result to `0 target units`. Clear removed both hidden constants, `factor` and `target`. This is a deterministic functional defect, not a ranking inference. Baselines are preserved in `exports/conversion-clear-before-2026-11-10.json`.

The shared Clear loop now preserves hidden inputs only when the active engine is `linear_convert`. Editable values still clear, and other engines retain their existing reset behavior. No conversion factors, numerical formulas, URL/indexability settings, theme, accounts or external submissions change. Existing sitemap dates are preserved: no automatic refresh of dates across thousands of pages for a shared maintenance fix.

Validation: 139 Python tests and all 41 JavaScript suites pass. Isolated production build validates 140,812 links; indexation stays at 305 sitemap URLs. Schema and fingerprint checks pass for 4,905 calculator and 5,027 stylesheet references. Playwright tests four conversion types at widths 1366, 390 and 320: all 12 Clear/recalculate checks pass, visible input blanks as expected, both constants persist, answers match the original result, no horizontal overflow or page errors. Local evidence: `exports/conversion-clear-local-2026-11-10.json`; repeatable verifier: `scripts/verify_conversion_clear_browser.cjs` (use `--live --baseline` for observation without fixed-state assertions; `--live` enforces the repair).

Exact-commit deployment and the same live browser checks gate release. These representative checks do not certify every converter's definition or every other calculator. Generic dashboard semantics remain a separate quality concern. No traffic increase, Google recrawl or 1,000/day attainment is claimed; the growth goal remains active.

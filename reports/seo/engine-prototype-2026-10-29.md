# Per-engine renderer prototype — October 29, 2026

Previous turn progressed dependency analysis at commit c174fe726e, with successful Pages run 40891249708 and 12 production navigation checks. This turn implements an isolated transformation rather than another inventory-only review.

## Actual candidate

`tools/asset-optimizer/prototype-engine.cjs` parses the optimized full runtime with Acorn and specializes literal engine-comparison branches inside `renderGenericFromEngine`. It preserves helpers, the main calculation dispatcher, event listeners and all unknown conditions. Nested functions are left intact to avoid treating shadowed parameters as the outer engine. A guard explicitly rejects another renderer engine instead of silently generating the wrong results. Generated source is parsed again. The CLI requires distinct input/output paths and does not edit HTML or deploy candidates.

For engine `401k_advanced`, the current optimized control is 500,087 bytes and the actual generated candidate is 315,148 bytes (184,939 bytes / 36.98% smaller). Identical local gzip settings produce 141,082 versus 92,598 bytes (34.36% smaller). These are file/compression measurements, not observed network transfer or faster LCP/INP. There are 26 statically resolved branches. Runtime/property names are preserved and no functions are removed using loading coverage.

Reproduction:

```powershell
node tools/asset-optimizer/test-prototype.cjs
node tools/asset-optimizer/prototype-engine.cjs doc-work/discovery-build/assets/calculator.js 401k_advanced doc-work/k401-candidate.js
node scripts/test_k401_projection.cjs doc-work/k401-candidate.js
$env:NS_K401_CANDIDATE='doc-work/k401-candidate.js'
node scripts/verify_k401_browser.cjs
Remove-Item Env:NS_K401_CANDIDATE
```

The optional browser override is local-only and is rejected with `--live`. Normal production verification continues to use the actual site's asset. The candidate is routed directly to the local browser without changing tracked or generated production assets.

## Verification completed

- Synthetic transform fixture: selected and default branches, unknown runtime conditions, nested parameter shadowing, wrong-engine rejection and unsupported renderer rejection.
- All 323 401(k) projection, withdrawal, boundary and DOM adapter scenarios pass against the candidate.
- Playwright at 1366×844, 390×844 and 320×844 passes all three 401(k) modes, default result, signed loss, blank/invalid values, fractional-age rules, 59.49/59.5, calendar-year assumption, shortfall, zero, Clear, Enter and employer match. No runtime error or horizontal overflow. Screenshots and check JSON remain in ignored working output.

## Still required before production

This is a real candidate milestone, **not a production rollout**. One page's mode coverage does not validate 151 dispatch cases or the rest of the site. The transform is not a general lexical binding/effect analyzer; reassignment and block-shadowing assumptions require additional guards before a build-time release. It currently specializes only the renderer and is not asynchronous code loading.

Before shipping: add engine-to-page build selection with fingerprint validation, explicitly guard unsupported AST patterns and fallback to the full control, verify all affected engines and page-specific nested modes, and repeat comparable loading plus interaction measurements with and without the candidate. No measured performance improvement, field CWV pass or SEO/traffic uplift is claimed. Public pages and indexation remain unchanged; no spending, account changes, submissions or outreach occurred.

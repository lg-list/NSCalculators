# Shared runtime dependency investigation — October 29

Previous turn was progress: a reproducible repeated mobile measurement was committed as `a63705fc8c489b46fe5cfe4dd529056c837a67a8`, Pages run 40890477539 succeeded and production navigation verification passed. This follow-up inspects the current optimized JavaScript rather than deleting initially uncovered functions.

## Verified structural findings

Running `node tools/asset-optimizer/inspect-dependencies.cjs` against isolated build version `718d9bfce62c3877` found 499,902 source characters, 358 top-level statements and 296 named top-level function declarations. These are character/AST measurements, not encoded network bytes or field performance results.

| Function | Source characters | Conservative named-function references |
|---|---:|---:|
| renderGenericFromEngine | 185714 | 111 |
| calc | 45138 | 112 |
| retirementProjection | 9276 | 4 |
| socialSecurityProjection | 7825 | 5 |
| k401Projection | 7822 | 5 |

The `calc` switch has 151 cases including default. The shared renderer and calculation dispatcher contain references to many different engines. A basic dependency closure rooted at either entry retains other engines; a loading-only coverage purge would remove paths that mode changes and later events may invoke. Therefore a function-name whitelist is not a safe production splitting mechanism.

## Delivered tooling and implementation decision

Added an analysis-only Acorn inventory tool using the already installed asset-optimizer dependency. It records function sizes/references and switch cases, refuses an identical input/output path and never rewrites JavaScript or HTML. A synthetic fixture checks function dependencies, dispatch labels and owning function. The tool's identifier references are deliberately conservative and do not resolve lexical bindings, callbacks, computed properties or async initialization. It is not a tree-shaker or proof of safe deletion.

The next implementation requires engine-specific dispatch/render boundaries before removing unrelated engine code. Keep the current full bundle as the control; prototype in isolated output and exercise initial answer, every mode, invalid input, Clear, Enter, charts and table toggles for each affected engine. Then repeat loading and interaction measurements with the same profile. No reduced bundle has passed these requirements, so none was published in this turn. This is an investigation milestone, not a completed performance optimization or claim of improved Core Web Vitals.

No production source, calculator behavior, metadata, URLs or indexation changed. No spending, outreach, account changes or external submission. The US SEO goal remains active; the latest completed Search Console evidence still cannot measure the recent releases' impact.

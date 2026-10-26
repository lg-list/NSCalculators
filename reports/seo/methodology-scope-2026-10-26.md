# Review Scope and Reproducible Methodology

Date: October 26, 2026. Existing routes: `/methodology/` and `/about/`.

## Audit findings

The initial sitemap check found no `<lastmod>` field in the generator; it was already omitting dates rather than publishing each build date as a significant update. No freshness-date defect was reproduced. [Google's sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap) expects lastmod values to be accurate when used; it is not a reason to invent dates or add unsupported historical timestamps. The sitemap stays unchanged.

Live Methodology had only broad selection/calculation/review prose and did not explain which scope passing checks establishes. About used “Each calculator includes” without distinguishing the review history or unavailable models. The improvement is clearer, inspectable coverage, not a claim that all calculators have now been audited.

[Google's people-first content guidance](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) discusses original value, clear sourcing/site background and explaining how content is produced, while warning against invented expertise. It does not make this wording a ranking guarantee or certify the site. No author credentials, expert byline, source endorsement or external approval is inferred from cited organizations.

## Public changes

- Existing Methodology explains selecting a task-specific model, selected-tool/scenario review limits and AI-assisted development. Disclosure concerns drafting code/explanations/checks during development; it does not say users' inputs are sent to an AI service or imply professional certification.
- Three original examples link directly to real tools: non-overlapping 12 x 14 and 8 x 8 ft rectangles total 232 ft²; a 20 x 10 ft / 3 in loose gravel layer is 50 ft³ with weight unknown before density; a 10% allowance makes 55 ft³, requiring 28 two-ft³ mulch bags with 56 ft³ purchased, 5 ft³ allowance and 1 ft³ package excess beyond base volume.
- Rounding and unknown-price explanations are explicitly scoped to those workflows rather than promised for every legacy tool. Editable rates/prices are examples, not current quotes. Tool-specific sources, assumptions and exclusions remain important.
- Corrections link to the existing Contact/Privacy pages, identifying public GitHub reporting and anonymized examples. No private mailbox or confidential channel is fabricated. A verified owner-controlled private route and truthful operator identity remain unresolved owner inputs, not solved by this copy.
- About now links to the methodology and states differing review coverage. No title/theme/plugin/calculation changes, new URL, publication date, rating or endorsement.

This is user-facing model guidance and reproducible evidence, not a public keyword-research block, test-count badge or promise of AdSense compliance.

## Verification

Before editing, public live Playwright reproduced 232 ft² net area, 50 ft³ gravel with missing-density guidance and 28 mulch bags after the entered 10% allowance. Local generated-page checks repeat those examples through real controls, follow About → Methodology → Area and verify privacy/scope language, canonical/indexability and no page overflow at 1366, 390 and 320px. Mobile screenshot reviewed. Ignored harness: `doc-work/verify-methodology.cjs`, supports `--live` after deployment.

All 115 existing Python tests pass. Isolated full build validates 140,786 internal links; sitemap/schema/asset gates retain 287 indexable calculators, 305 sitemap URLs, maximum depth 3, 288 apps, 299 breadcrumb trails and 1,173 breadcrumb targets. Final calculator `9cfdaa4c9bd672b2` remains 473,169 bytes across 4,905 references; CSS `137a61e00f1a1a4a` remains across 5,027 references. These identical asset hashes confirm no calculator/CSS change, not universal formula correctness. Tracked `dist/` is untouched; CI builds and checks the deployment.

No external submission, account change, outreach or spend. The prepared Iowa State recommendation remains unapproved/unsent; continuing the goal is not approval. No measured traffic, field CWV, ranking or advertising-review improvement is claimed. The 1,000 daily organic-visit objective remains unachieved/unverified.

# Tip Calculator: Exact-Cent Splits

## Evidence and Priority

October 24, 2026. Read the signed-in Search Console Pages breakdown with the exact query `tip calculator`, United States, Web, September 24-October 21. The visible report identifies only `https://nscalculators.com/tip-calculator/`: 16 impressions, zero clicks. Query-level average position is 39.6. This confirms an existing relevant URL, not US market search volume, significant traffic, or a higher opportunity score than Area. No raw account captures or full query export are published.

Live browser reproduction before deployment accepted 2.5 people on the default $80 bill and 20% tip and returned $38.40 per person. A $100 total split three ways showed only $33.33 each, leaving one cent unpaid. The old pie also included per-person payment alongside the full bill and tip, duplicating money in its denominator.

The preceding goal work was progress: the approved GA4 Site search change was saved and SDK-verified. This continuation addresses a different reproduced calculator defect, not another analytics setting change.

## Implementation

- Preserve the existing URL, default $80 / 20% / two-person answer, visual theme, plugins and index scope.
- Parse nonnegative decimal money (up to two places) and percentages (up to four places). Reject blanks, negatives, malformed values, fractional or zero payers, and unsupported overflow explicitly instead of silently substituting a value.
- Integer arithmetic rounds the tip once, half-cent up, then splits total cents. A remainder assigns one extra cent to the required number of people. Dollar formatting of the main answer, split, cards and table uses the integer cents rather than a floating-point division.
- Example: $100 with zero tip and three people becomes one payment of $33.34 and two of $33.33. Suggested shares reconcile exactly; people decide who covers the extra cent.
- Pie inputs are only bill and tip. Invalid/cleared/zero totals hide the chart, and invalid or cleared inputs remove the previous result cards and details.
- Original explanation covers rounding, receipts with included gratuity/service charges and the entered bill's tax basis. The tool does not infer tax, subtract included gratuity, allocate individual orders, or prescribe tipping etiquette.

## Verification

Added 467 JavaScript cases covering decimal boundaries, half-cent rounding, exact allocation invariants, supported large-cent formatting, malformed inputs and dashboard clearing. Added a Python page-contract regression and the JavaScript suite to deployment CI.

Local generated site: 81 Python tests and 1,181 JavaScript cases including analytics context scenarios pass. Indexation contract remains 302 sitemap URLs, all reachable within three clicks through eligible HTML links. Existing 284 indexable calculators and 140,687 internal links remain unchanged. Asset gates validate every calculator/stylesheet reference.

Playwright at 1366px, 390px and 320px verifies default and unequal split outputs, fractional-payer rejection, half-cent rounding, Clear/recovery, a colored nonblank compact canvas and no horizontal page overflow or JavaScript errors. The Calculate control remains in the initial 844px viewport. Synthetic browser tests block Analytics collection.

Deployment verification is recorded in the execution close-out after push; local tests alone are not evidence of production deployment. No ranking or traffic lift is claimed, and the daily-1,000 organic-visit objective remains unachieved. No external submissions, purchases, outreach or additional account changes were made.

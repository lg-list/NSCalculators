# Calculator Keyboard Submission

Date: 2026-10-24

## Evidence and Scope

The completed US Search Console window identifies Area, Ratio and Fuel Cost as observation priorities. Inspection of their shared calculator implementation found no Enter-key submission: numeric/text fields sit in sections, not native forms, and only click handlers called Calculate. This is an interaction improvement, not a demonstrated ranking or traffic increase. Titles, descriptions, formulas, theme and indexation scope are unchanged.

## Change

Enter in an editable text or number input now clicks its existing Calculate button. Reusing the click path preserves calculation, rendering, validation and existing submit analytics rather than implementing a second calculation path. Loan inputs are scoped to their own model panel, not the first calculator button on the page.

No interception of native forms, multiline text, select menus, checkboxes, radios, date/time/month pickers, search boxes, buttons, modifier chords, repeated keydown, consumed events or IME composition. Hidden/disabled controls and hidden/disabled Calculate buttons do not submit. No field values are added to analytics.

## Verification

- Added 34 isolated keyboard regression cases; wired into the GitHub Pages deployment gate.
- All 66 Python tests and all JavaScript suites pass, including the existing 530 calculation/search/chart cases and the 34 new keyboard cases.
- Local Playwright: Area, Ratio, Fuel Cost and Loan at 1366, 390 and 320 pixels. Enter clicks exactly once; Shift+Enter and select-key events do not trigger Calculate. All three loan models submit from their visible inputs. No uncaught page errors or horizontal overflow.
- Inspected the 390-pixel loan screenshot: layout and result remain intact.
- Isolated build: 5,005 calculator routes, 284 indexable calculators, 140,684 validated internal links. Sitemap scope is unchanged.
- 4,902 calculator script references resolve to content version `654394a5a336a72a`; 5,026 stylesheet references retain `4c8a30aec0dca952`.

No Search Console submissions, account changes, spending, outreach or new thin pages. Measure engagement and search outcomes only after deployment and a settled reporting interval; do not attribute the historical four US clicks to this change.

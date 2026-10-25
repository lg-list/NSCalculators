# Reproducible Room Area Records

Date: October 25, 2026

## Priority and Reproduction

The validated US GSC baseline for September 24-October 21 reports 590 impressions, zero clicks and position 8.29 for the exact named query area calculator. This is historical query visibility, not monthly market volume or evidence of demand for CSV downloads. Keep the highest-visibility existing tool useful while waiting for a post-release performance window; do not create more near-duplicate pages or repeatedly change its snippet.

Production reproduction: add a 20 ft by 14 ft outline, then subtract an 8 ft by 6 ft cutout. The result is 232 sq ft, but each saved object contains only shape, squareMeters and operation. The list shows 280 and 48 sq ft without their original dimensions. After entering the next shape, those measurements are no longer available in the room record. The existing measured irregular-room guide already uses this exact verification workflow.

## Change

Saved sections now retain independent copies of the validated source measurements, their original units and the formula, alongside the existing canonical square-meter area and add/subtract operation. Include only required dimensions, not derived diagonals/diameters/arc lengths; a sector explicitly records its central angle in degrees. Subsequent input or unit changes do not rewrite previous measurements. The area algorithms and aggregation rules remain unchanged.

The saved-section list displays these measurements, and a Lucide download command produces a local CSV for recorded room sections only. A valid stored total can be exported even when the unsaved current shape differs. Empty or invalid totals do not produce a file; matching deductions may validly produce zero net area. Clear and Remove reset/update the record and download state.

CSV columns: record type, section number, operation, shape, measurements, formula, selected-unit area, area unit, square meters and canonical source URL. Section rows are distinct from Added/Deducted/Net summary rows so consumers can filter record types rather than sum subtotals into the answer. Measurement numbers preserve the calculator's native parsed Number values; derived areas use up to 15 significant digits, not arbitrary-precision surveying arithmetic. Output is quoted CSV with CRLF and a UTF-8 BOM for unit symbols. Text cells that could start spreadsheet formulas receive a text prefix.

The export uses Blob/object URLs and a temporary download anchor; no upload endpoint, measurement query parameter or new Analytics event was introduced. Existing measurement/Calculate events are unchanged. Browser tests block Analytics to avoid synthetic traffic, so this is not a comprehensive privacy/consent audit of the whole site. The command reports that a CSV was prepared, not that the browser saved it successfully. The actual file download is independently tested below.

Only the existing Area route receives the UI. Its original domain copy now emphasizes retaining dimensions/units and checking cutout placement. Title, metadata, canonical, snippets, sitemap/index scope and theme remain stable. No overlap, spatial containment, material waste, persistent storage or CSV re-import feature is claimed.

## Verification

- 102 Python tests pass, including one new static UI/method/scope check.
- All existing JavaScript suites pass. The new suite covers 37 scenario groups: all nine output units, nine shape modes, deep-copy independence, mixed source units, tiny measurements, zero net, invalid/missing measurement records, quote/comma/newline handling, formula-prefix protection, and download success/failure/cleanup. It uses Python's standard CSV reader with explicit UTF-8 rather than a second ad hoc parser.
- Local Playwright at 1366/390/320 downloads and parses actual files with expected names and UTF-8 BOMs. Checks the 280 - 48 sq ft example, adding one square meter while retaining the original foot dimensions, converting the selected output unit, excluding a different unsaved shape, zero net, immutable sector angle, invalid deductions, Remove/Clear recovery, no horizontal overflow, initial first-screen Calculate and unchanged self-canonical/indexability. Generated CSVs/screenshots and the harness remain ignored in doc-work.
- Exported mixed-unit example: 280 sq ft - 48 sq ft + 1 sq m = 22.55350528 sq m. Original records remain 20 x 14 ft, 8 x 6 ft and 1 x 1 m. An unsaved 20 x 20 m shape is not included.
- Full static gates: 303 sitemap URLs reachable within three clicks, 285 indexable calculator records, 286 apps, 297 breadcrumb trails, 1,165 breadcrumb targets and 140,741 internal links. JS 819aa8e67efcfb10 matches 4,903 references; scoped CSS cd300833995da830 matches 5,027 references.
- Download glyph is the static Lucide 0.468.0 icon, with its ISC notice retained in the emitted markup. No icon JavaScript package or extra network dependency is added. Source: [Lucide download SVG](https://cdn.jsdelivr.net/npm/lucide-static@0.468.0/icons/download.svg) and [package license](https://cdn.jsdelivr.net/npm/lucide-static@0.468.0/LICENSE).

Post-deployment repeat: `node doc-work/verify-area-records.cjs --live`. This verifies a practical reusable result record, not search lift, acquired links, field CWV or completion of the US traffic goal.

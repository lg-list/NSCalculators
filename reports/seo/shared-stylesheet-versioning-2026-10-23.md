# Shared Stylesheet Versioning

Date: 2026-10-23

## Evidence and Change

Live browser inspection of Home, Mortgage, Wheel Offset, Area, Time Duration, and Body Fat found five date-based stylesheet URLs serving identical 90,368-byte CSS (SHA-256 prefix `c6dea991aa920bec`). These fragmented cache keys also depended on manually updating page-specific versions after CSS changes.

Replaced page-specific CSS dates with the first 16 SHA-256 characters of the exact generated UTF-8 stylesheet. The generator caches this value per build and writes deterministic bytes. A deployment gate verifies every shared stylesheet reference against the artifact, rejecting stale, missing, or duplicate version parameters. Unstyled redirect aliases are intentionally exempt.

CSS declarations, calculator JavaScript, titles, canonicals, robots policy, and indexability are unchanged. This is not a visual redesign or a new indexed page.

## Local Verification

- 50 Python regression tests pass, including five stylesheet tests covering byte identity, automatic invalidation, formerly pinned pages, base paths, and invalid artifact versions.
- Full isolated build: 5,005 calculator pages, 284 indexable calculators, 302 sitemap URLs, and 140,684 validated internal links.
- Artifact gate: 5,026 stylesheet references share `c6dea991aa920bec`.
- Existing JavaScript asset gate: 4,902 references retain `17afe927c787b8e5`.
- Playwright: six representative pages at 1366, 390, and 320 pixels use one CSS URL, load styles, preserve checked results, and have no page overflow or browser errors. Reviewed 320-pixel Home, Mortgage, and Body Fat screenshots.

Browser routing disables HTTP caching, so these checks establish URL/content consistency, not observed cache hits, saved network bytes, field Core Web Vitals, or ranking improvement. Fresh US Search Console data remains unavailable; no demand or traffic gains are inferred. No external submission or account modification was made.

# Irregular Room Visual Explanation

Date: 2026-10-24. Existing guide: `/guides/calculate-square-footage-irregular-room/`.

## Decision and Evidence

The US Search Console baseline supports prioritizing the Area cluster: `area calculator` has 590 observed impressions in September 24-October 21. This is not a market-volume estimate for the guide or proof of demand for a new article. Kept the current guide, URL, title and description rather than creating a competing L-shaped-room page.

The existing guide explains the same 232 sq ft room through two methods but previously had no floor-plan visual or side-by-side arithmetic check. Added an original, scaled measurement diagram and a compact comparison table so a reader can see which corner is missing and why both methods agree.

## Content and Asset

The diagram's enclosing dimensions are 20 x 14 ft. Its upper-right cutout is 8 x 6 ft. The remaining floor is section A, 12 x 14 ft = 168 sq ft, plus section B, 8 x 8 ft = 64 sq ft. Thus 280 - 48 = 168 + 64 = 232 sq ft.

The SVG is an exact geometric illustration, not an AI-generated photograph, a copied competitor graphic, a survey or a plan of an actual customer's property. Rectangle geometry uses one consistent scale. A and B labels, a dashed cutout, caption, alt text, SVG title/description and an HTML table communicate the same relationships without relying only on color. No scripts or external image dependency are embedded in the asset.

The image has explicit intrinsic dimensions, a responsive aspect ratio, lazy loading and asynchronous decoding. It appears in the worked-example section, not before the calculator or as an oversized hero. Scoped figure CSS retains the existing theme. These choices avoid unnecessary asset-induced layout instability but do not establish field Core Web Vitals improvement.

Added the exact Add/Subtract workflow next to the example, including clearing the total between methods to prevent double-counting. This extends the existing tool/guide relationship with helpful interpretation, not a visible keyword list or invented popularity claim.

## Verification

- 80 Python tests pass. Two new methods verify the SVG's actual rectangle coordinates, scale, shared edges, non-overlapping areas and both arithmetic methods, as well as accessible image dimensions/loading and the matching guide/table text.
- Local Playwright at 1366, 390 and 320 px: image loaded with the correct natural 360 x 350 size and aspect ratio; diagram endpoint returned 200; table present; no page error or page-level horizontal overflow. Inspected the 320 px figure screenshot: dimensions, section labels, cutout and caption are readable and not clipped.
- Isolated build remains 5,005 calculator routes / 284 indexable calculators. All 302 sitemap URLs pass the indexation/crawl-path contract. 140,687 internal links validate.
- All 5,026 stylesheet references match the new content version `8b362bd240e9a932`. The shared calculator bundle and formulas are unchanged.

No new article, keyword-volume claim, account change, payment, outreach, sitemap submission or indexing request. No ranking or traffic outcome is yet measured. The separately recorded GA4 automatic-site-search setting still awaits explicit owner approval; this content release does not change it.

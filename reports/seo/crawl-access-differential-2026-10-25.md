# Separate Script Denials From Google Crawl Status

Observed October 25, 2026. This resolves a diagnostic ambiguity, not a new website outage. No production content, canonical, robots, firewall, account setting or external submission changed.

## Reproducible Request Difference

Used Playwright APIRequestContext GET requests with separate anonymous contexts and the same three public URLs. Changing the userAgent option alone gave:

| Request identification | robots.txt | sitemap.xml | Area Calculator |
| --- | --- | --- | --- |
| Playwright default | 200 | 200 | 200 |
| Python-urllib/3.13 | 403 | 403 | 403 |
| Googlebot user-agent string only | 200 | 200 | 200 |

The Python-identified sitemap response has a Cloudflare-branded Access denied title. Responses report the Cloudflare server. The exact rule was not inspected and must remain unknown. The Googlebot-string request came from the local testing environment, not Google's verified network: it is only a user-agent differential test, never evidence that a genuine Google crawler can fetch the page now.

No CAPTCHA was solved, authenticated session copied, origin network bypassed, allowlist created or security protection changed. This owned-site diagnostic does not authorize routinely misrepresenting audit clients as Googlebot. Future routine checks should retain normal browser/Playwright identification, report actual failures honestly and corroborate crawler claims with Search Console or verified crawl logs.

Cloudflare's [403 documentation](https://developers.cloudflare.com/support/troubleshooting/http-status-codes/4xx-client-error/error-403/) distinguishes branded denials and possible security causes; it does not identify this site's rule. Its [IP verification documentation](https://developers.cloudflare.com/bots/reference/bot-verification/ip-validation/) explains that verified-bot checks involve more than a supplied user-agent name. Do not disable security protections to remove a diagnostic-only symptom.

## Actual Google Record

Opened the existing signed-in domain property's Sitemaps report, read only. The visible sitemap row reports:

- URL: https://nscalculators.com/sitemap.xml
- Submitted: October 19, 2026
- Last read: October 23, 2026
- Status: Success
- Discovered pages: 302; videos: 0

The public sitemap now has 303 URLs after the October 25 New vs Used tool release. The recorded Google fetch predates that addition. This mismatch is not by itself a submission failure, and the old record does not confirm that Google has discovered or indexed the new page. No request to validate, resubmit or index a URL was made.

The public robots file currently allows `/` for `User-agent: *` and references the canonical HTTPS sitemap. All three default-Playwright requests return the expected document content types; no browser challenge marker was observed. These spot checks are not a global network/crawler audit. Google's [HTTP status documentation](https://developers.google.com/crawling/docs/troubleshooting/http-status-codes) also notes that a successful response does not guarantee indexing.

## Next Action

Retain the stable current canonical/robots/sitemap configuration. A Python-client 403 alone must not trigger new test sitemap files, canonical flips, repeated external submissions or a domain migration. If a future Search Console fetch fails, record its URL, last attempt and response classification, then request owner approval for any account/security change after reviewing the responsible rule or verified crawl logs. Do not infer an old failure's original cause from today's experiment.

Minimal machine-readable aggregate evidence: `exports/crawl-access-observation-2026-10-25.json`. No account identity, response IP, full denied-page body or raw account capture is published. The US growth objective remains active and unmet; the next settled performance window remains more useful than further sitemap churn.

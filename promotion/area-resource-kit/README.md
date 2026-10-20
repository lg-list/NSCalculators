# Area Calculator Editorial Review Kit

Prepared 2026-10-20. **Research and drafts only. Nothing has been sent.**
This is not a backlink agreement, an acceptance prediction, or an automated
outreach queue. Do not send without the owner's explicit approval of the
recipient, message, sender identity and any personal contact information.

## Audience and Qualification

Target English-language educators and US-facing DIY editors whose existing
resources explain geometric area or measuring an irregular floor. The resource
must help an actual calculation task, not merely offer a place to put a link.
Exclude paid placements, reciprocal-link requests, direct competing calculators,
unverifiable contact routes and proposals requiring invented credentials.

| Review order | Candidate | Public evidence and contact route | Why it fits | Material uncertainty |
| --- | --- | --- | --- | --- |
| 1 | TeachersFirst | [Subject/grade catalog](https://teachersfirst.org/matrix.cfm); [contact form](https://teachersfirst.org/contact.cfm) | A potential classroom arithmetic check after students derive area | No explicit acceptance promise or current request; form has a phone field requiring owner-controlled details |
| 2 | Bob Vila | [Flooring measurement article](https://www.bobvila.com/articles/how-much-flooring-do-i-need/); [editorial contact](https://www.bobvila.com/contacts/) | An optional worked check alongside its explanation of measuring separate pieces | An older article, not a solicitation; unknown editorial interest and unverified sender/email readiness |

These are **conditional editorial-fit candidates**, not hot leads or verified
email recipients. Public contact pages were checked; inbox deliverability was
not tested. No private contact information was collected. TeachersFirst's
historical `.com` site redirected to `.org` during verification.

HomeschoolMath returned 403 during direct verification and was not shortlisted;
no access-control workaround was attempted. Flooring calculator competitors and
advertising routes were excluded rather than padded into the shortlist.

## Demonstration

Primary destination: [Area Calculator](https://nscalculators.com/area-calculator/).
Supporting walkthrough:
[Irregular Room Square Footage](https://nscalculators.com/guides/calculate-square-footage-irregular-room/).

The same L-shaped floor can be checked two ways:

- Enclosing rectangle minus corner: 20 x 14 - 8 x 6 = 232 sq ft.
- Non-overlapping rectangles: 12 x 14 + 8 x 8 = 168 + 64 = 232 sq ft.

The live UI demo adds the two rectangles, switches the total to square meters
(21.55350528), switches back to square feet, removes one section and clears the
total. It also checks an **exact** 4 in by 4 in square: 16/144 = 1/9 sq ft.
Actual tile dimensions may differ from nominal product labels; this geometric
check is not a manufacturer-specific coverage claim.

`demo-checks.json` records the live results and capture timestamp.
`area-demo-desktop.png` and `area-demo-mobile.png` are unedited screenshots of
the real tool with those inputs. The current shape's answer and accumulated room
total are separate UI values. The mobile image focuses on the room total, not
every control above it. These are not screenshots of publisher endorsements.

To reproduce with the existing local Node/Playwright installation:

```powershell
node promotion/area-resource-kit/capture-demo.cjs
```

The script accesses only the public NS Calculators site, blocks third-party
tracking, changes browser-local calculator inputs and writes local artifacts.
It contains no contact-form submission or email-sending code and is not part
of the production website. Do not infer field Core Web Vitals from this demo.

## Before Any Contact

- Owner approves each recipient and the final wording, not a bulk campaign.
- Owner supplies a legitimate sender name/reply route and any required form
  fields; do not guess a phone number or claim an unprovisioned mailbox works.
- Recheck the contact page and policies immediately before contact. Use only
  an appropriate public business channel.
- Do not claim teacher review, curriculum alignment, human-only authorship,
  market leadership, traffic results or professional certification.
- Ask for editorial evaluation, never a guaranteed link, exact-match anchor,
  dofollow attribute, payment, exchange, or repeated automated follow-ups.
- Respect a refusal. If a recipient finds a genuine defect, fix it before
  further promotion rather than treating a listing as the main objective.

No new public route, tracking code, account, submission or advertising spend
is introduced by this kit. A potential earned mention is not a forecast of
1,000 daily organic visits.

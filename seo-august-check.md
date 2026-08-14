# GSC Health Check — digme.co.za (August 2026)

**Date run:** 14 August 2026 (4 weeks post-fix)

## Sitemap

New sitemap read successfully: last read Aug 5, 2026, **36 pages discovered** (target ~37 — effectively confirmed, down from the old 107-URL Squarespace sitemap). No errors reported.

## Indexing progress

The Pages (indexing) report and the Performance report are both showing **"Processing data, please check again in a day or so"** for this property — no aggregate crawled-not-indexed / discovered-not-indexed counts were available today. This looks like a temporary GSC data-processing gap rather than a site issue (spot-checked URLs below are indexing fine), but it means the 32/31 baseline comparison can't be done yet. Worth a quick re-check in a few days before the October audit.

## Canonical pickup (URL Inspection)

- **/about** — clean. Last crawl Jul 28 (post-fix). Declared canonical `https://digme.co.za/about`, Google-selected = inspected URL. Correct.
- **/articles-and-blogs/emp201-deadline-south-africa-paye-penalties** (the real path — `/blog/...` is a legacy non-existent path) — indexed, resolves correctly.
- **/blog/emp201-deadline-south-africa-paye-penalties** (legacy path, checked as given) — not indexed as its own URL; Google correctly treats it as an alternate and points its canonical to the real `/articles-and-blogs/...` URL. Working as intended, not a bug.
- **/bookkeeping** — the *indexed* version Google has on file still shows the **old canonical (`https://www.digme.co.za/bookkeeping`)**, because last crawl was Jul 6 — before the mid-July fix went live. The **live test** confirms the current live page now declares the correct canonical (`https://digme.co.za/bookkeeping`), so this will resolve once Google recrawls. I submitted a re-index request for this URL while inspecting it.

## www redirect

Confirmed: `https://www.digme.co.za` → `https://digme.co.za/` redirects correctly.

## Bottom line

Fixes are live and mostly picked up. Sitemap is clean. Canonical tags are correct on the pages checked, though at least one (bookkeeping) is still waiting on a fresh Googlebot crawl to update in the index. No new coverage errors seen. The stalled indexing/performance reports are the one loose end — recheck before the October re-audit to make sure the crawled-not-indexed and discovered-not-indexed counts actually dropped as expected.

# Analyst Target Price Ingestion

This app does not require paid analyst-estimate APIs for the MVP target-price field.
Instead, a server-side Vercel Cron route scans public finance/news RSS feeds every
two days, extracts clearly stated broker/analyst target prices, and writes the
structured result to Supabase.

## Schedule

- Route: `/api/cron/analyst-target-prices`
- Cron: `0 6 */2 * *`
- Taipei time: about 14:00 every two days

The route requires:

- `CRON_SECRET`
- `SUPABASE_URL` or `NEXT_PUBLIC_SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY` or `SUPABASE_SECRET_KEY`

The frontend only needs read access:

- `SUPABASE_URL` or `NEXT_PUBLIC_SUPABASE_URL`
- `SUPABASE_PUBLISHABLE_KEY` or `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`

## Tables

Run `supabase/schema.sql` in the Supabase SQL editor. It creates:

- `analyst_target_price_news`
- `analyst_target_price_ingestion_runs`

`analyst_target_price_news` is public-read through RLS because it contains only
extracted public-news fields. Writes are intentionally server-only.

## Sources

Default sources:

- CNA finance RSS
- CNA technology RSS
- Anue/Cnyes Taiwan stock RSS

Optional sources:

- `TARGET_PRICE_NEWS_RSS_URLS`: comma/newline separated RSS URLs
- `TARGET_PRICE_NEWS_ARTICLE_URLS`: comma/newline separated public article URLs
- `TARGET_PRICE_NEWS_MAX_ARTICLES`: default `40`
- `TARGET_PRICE_FETCH_ALL_ARTICLES`: set `true` only when the source permits
  higher fetch volume

Do not bypass paywalls, login walls, or restricted data. Store the article URL
and a short excerpt, not full copyrighted articles.

## Frontend Priority

The individual stock page target-price field uses this order:

1. Supabase public-news extracted target price
2. Local imported broker research PDFs
3. Current page news-text extraction
4. Pending/provider-needed placeholder

Paid providers such as FactSet, LSEG I/B/E/S, Bloomberg, or FMP remain optional
future integrations but are not required for the current free-news workflow.

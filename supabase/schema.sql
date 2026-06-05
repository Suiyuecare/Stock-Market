create extension if not exists pgcrypto;

create table if not exists public.watchlist_items (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  symbol text not null,
  name text not null,
  price numeric(14, 4) not null default 0,
  change_percent numeric(8, 4) not null default 0,
  target_price numeric(14, 4) not null default 0,
  created_at timestamptz not null default now()
);

create table if not exists public.journal_entries (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  entry_key text not null,
  content text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (user_id, entry_key)
);

alter table public.watchlist_items enable row level security;
alter table public.journal_entries enable row level security;

drop policy if exists "Allow public read watchlist" on public.watchlist_items;
drop policy if exists "Allow public insert watchlist" on public.watchlist_items;
drop policy if exists "Allow public read journal" on public.journal_entries;
drop policy if exists "Allow public upsert journal" on public.journal_entries;
drop policy if exists "Users can read own watchlist" on public.watchlist_items;
drop policy if exists "Users can insert own watchlist" on public.watchlist_items;
drop policy if exists "Users can update own watchlist" on public.watchlist_items;
drop policy if exists "Users can delete own watchlist" on public.watchlist_items;
drop policy if exists "Users can read own journal" on public.journal_entries;
drop policy if exists "Users can insert own journal" on public.journal_entries;
drop policy if exists "Users can update own journal" on public.journal_entries;
drop policy if exists "Users can delete own journal" on public.journal_entries;

create policy "Users can read own watchlist"
on public.watchlist_items
for select
to authenticated
using ((select auth.uid()) = user_id);

create policy "Users can insert own watchlist"
on public.watchlist_items
for insert
to authenticated
with check ((select auth.uid()) = user_id);

create policy "Users can update own watchlist"
on public.watchlist_items
for update
to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

create policy "Users can delete own watchlist"
on public.watchlist_items
for delete
to authenticated
using ((select auth.uid()) = user_id);

create policy "Users can read own journal"
on public.journal_entries
for select
to authenticated
using ((select auth.uid()) = user_id);

create policy "Users can insert own journal"
on public.journal_entries
for insert
to authenticated
with check ((select auth.uid()) = user_id);

create policy "Users can update own journal"
on public.journal_entries
for update
to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

create policy "Users can delete own journal"
on public.journal_entries
for delete
to authenticated
using ((select auth.uid()) = user_id);

create table if not exists public.analyst_target_price_news (
  id uuid primary key default gen_random_uuid(),
  dedupe_key text not null unique,
  symbol text not null,
  company_name text,
  broker text,
  rating text,
  target_price_mean numeric(14, 4) not null check (target_price_mean > 0),
  target_price_low numeric(14, 4),
  target_price_high numeric(14, 4),
  currency text not null default 'TWD',
  source_name text not null,
  source_url text not null,
  article_title text not null,
  summary_excerpt text,
  published_at timestamptz,
  captured_at timestamptz not null default now(),
  confidence numeric(5, 4) not null default 0.5 check (confidence >= 0 and confidence <= 1),
  extraction_method text not null default 'public_news_regex_v1',
  raw_text_hash text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists analyst_target_price_news_symbol_published_idx
on public.analyst_target_price_news (symbol, published_at desc, captured_at desc);

create index if not exists analyst_target_price_news_source_idx
on public.analyst_target_price_news (source_name, captured_at desc);

create table if not exists public.analyst_target_price_ingestion_runs (
  id uuid primary key default gen_random_uuid(),
  started_at timestamptz not null,
  finished_at timestamptz not null default now(),
  status text not null check (status in ('success', 'partial', 'skipped', 'failed')),
  source_count integer not null default 0,
  scanned_count integer not null default 0,
  extracted_count integer not null default 0,
  inserted_count integer not null default 0,
  error_message text,
  created_at timestamptz not null default now()
);

alter table public.analyst_target_price_news enable row level security;
alter table public.analyst_target_price_ingestion_runs enable row level security;

drop policy if exists "Public can read analyst target price news" on public.analyst_target_price_news;

create policy "Public can read analyst target price news"
on public.analyst_target_price_news
for select
to anon, authenticated
using (true);

grant select on public.analyst_target_price_news to anon, authenticated;

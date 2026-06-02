create extension if not exists pgcrypto;

create table if not exists public.watchlist_items (
  id uuid primary key default gen_random_uuid(),
  symbol text not null,
  name text not null,
  price numeric(14, 4) not null default 0,
  change_percent numeric(8, 4) not null default 0,
  target_price numeric(14, 4) not null default 0,
  created_at timestamptz not null default now()
);

create table if not exists public.journal_entries (
  id uuid primary key default gen_random_uuid(),
  entry_key text not null unique,
  content text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.watchlist_items enable row level security;
alter table public.journal_entries enable row level security;

drop policy if exists "Allow public read watchlist" on public.watchlist_items;
drop policy if exists "Allow public insert watchlist" on public.watchlist_items;
drop policy if exists "Allow public read journal" on public.journal_entries;
drop policy if exists "Allow public upsert journal" on public.journal_entries;

create policy "Allow public read watchlist"
on public.watchlist_items
for select
to anon
using (true);

create policy "Allow public insert watchlist"
on public.watchlist_items
for insert
to anon
with check (true);

create policy "Allow public read journal"
on public.journal_entries
for select
to anon
using (true);

create policy "Allow public upsert journal"
on public.journal_entries
for all
to anon
using (true)
with check (true);

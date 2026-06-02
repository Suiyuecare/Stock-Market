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

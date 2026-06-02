create extension if not exists pgcrypto;

create table if not exists market_sessions (
  id uuid primary key default gen_random_uuid(),
  market text not null,
  session_date date not null,
  phase text not null,
  status text not null default 'pending',
  created_at timestamptz not null default now(),
  unique (market, session_date, phase)
);

create table if not exists instruments (
  id uuid primary key default gen_random_uuid(),
  symbol text not null unique,
  market text not null,
  name text not null,
  sector text,
  currency text not null default 'TWD',
  created_at timestamptz not null default now()
);

create table if not exists daily_prices (
  id uuid primary key default gen_random_uuid(),
  instrument_id uuid not null references instruments(id) on delete cascade,
  trade_date date not null,
  open numeric(18, 4),
  high numeric(18, 4),
  low numeric(18, 4),
  close numeric(18, 4) not null,
  volume bigint,
  created_at timestamptz not null default now(),
  unique (instrument_id, trade_date)
);

create table if not exists news_events (
  id uuid primary key default gen_random_uuid(),
  source text not null,
  title text not null,
  url text,
  published_at timestamptz,
  raw_text text,
  parsed_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists prediction_signals (
  id uuid primary key default gen_random_uuid(),
  instrument_id uuid references instruments(id) on delete cascade,
  signal_date date not null,
  horizon text not null,
  score numeric(8, 4) not null,
  confidence numeric(8, 4) not null,
  drivers jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now()
);

insert into instruments (symbol, market, name, sector, currency)
values
  ('2330', 'TW', '台積電', '半導體', 'TWD'),
  ('2454', 'TW', '聯發科', '半導體', 'TWD'),
  ('NVDA', 'US', 'NVIDIA', 'AI / Semiconductors', 'USD'),
  ('AAPL', 'US', 'Apple', 'Consumer Technology', 'USD')
on conflict (symbol) do nothing;

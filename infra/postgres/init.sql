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

create table if not exists fundamental_metrics (
  id uuid primary key default gen_random_uuid(),
  instrument_id uuid not null references instruments(id) on delete cascade,
  metric_date date not null,
  revenue_growth numeric(10, 4),
  gross_margin numeric(10, 4),
  operating_margin numeric(10, 4),
  eps numeric(12, 4),
  pe_ratio numeric(12, 4),
  pb_ratio numeric(12, 4),
  roe numeric(10, 4),
  created_at timestamptz not null default now(),
  unique (instrument_id, metric_date)
);

create table if not exists institutional_trading (
  id uuid primary key default gen_random_uuid(),
  instrument_id uuid not null references instruments(id) on delete cascade,
  trade_date date not null,
  foreign_net_buy bigint not null default 0,
  investment_trust_net_buy bigint not null default 0,
  dealer_net_buy bigint not null default 0,
  margin_balance bigint,
  short_balance bigint,
  created_at timestamptz not null default now(),
  unique (instrument_id, trade_date)
);

create table if not exists technical_indicators (
  id uuid primary key default gen_random_uuid(),
  instrument_id uuid not null references instruments(id) on delete cascade,
  trade_date date not null,
  ma_5 numeric(18, 4),
  ma_20 numeric(18, 4),
  ma_60 numeric(18, 4),
  rsi_14 numeric(10, 4),
  k_9 numeric(10, 4),
  d_9 numeric(10, 4),
  macd numeric(18, 4),
  macd_signal numeric(18, 4),
  macd_histogram numeric(18, 4),
  obv numeric(24, 4),
  volume_price_divergence numeric(10, 4),
  created_at timestamptz not null default now(),
  unique (instrument_id, trade_date)
);

create table if not exists us_market_linkage (
  id uuid primary key default gen_random_uuid(),
  session_date date not null,
  nasdaq_score numeric(10, 4),
  sox_score numeric(10, 4),
  sp500_score numeric(10, 4),
  vix_score numeric(10, 4),
  tsm_adr_score numeric(10, 4),
  nvda_score numeric(10, 4),
  amd_score numeric(10, 4),
  aapl_score numeric(10, 4),
  avgo_score numeric(10, 4),
  mu_score numeric(10, 4),
  msft_score numeric(10, 4),
  meta_score numeric(10, 4),
  googl_score numeric(10, 4),
  amzn_score numeric(10, 4),
  created_at timestamptz not null default now(),
  unique (session_date)
);

create table if not exists news_events (
  id uuid primary key default gen_random_uuid(),
  source text not null,
  title text not null,
  url text,
  published_at timestamptz,
  raw_text text,
  parsed_json jsonb not null default '{}'::jsonb,
  sentiment text,
  impact_score numeric(10, 4),
  related_symbols text[] not null default '{}',
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

create table if not exists factor_scores (
  id uuid primary key default gen_random_uuid(),
  instrument_id uuid not null references instruments(id) on delete cascade,
  signal_date date not null,
  category text not null,
  factor_name text not null,
  score numeric(10, 4) not null,
  weight numeric(10, 4) not null,
  explanation text not null,
  created_at timestamptz not null default now()
);

create table if not exists risk_scores (
  id uuid primary key default gen_random_uuid(),
  instrument_id uuid not null references instruments(id) on delete cascade,
  signal_date date not null,
  total numeric(10, 4) not null,
  volatility numeric(10, 4) not null,
  liquidity numeric(10, 4) not null,
  concentration numeric(10, 4) not null,
  event numeric(10, 4) not null,
  explanation text not null,
  created_at timestamptz not null default now(),
  unique (instrument_id, signal_date)
);

insert into instruments (symbol, market, name, sector, currency)
values
  ('2330', 'TW', '台積電', '半導體', 'TWD'),
  ('2454', 'TW', '聯發科', '半導體', 'TWD'),
  ('2317', 'TW', '鴻海', '電子代工', 'TWD'),
  ('2308', 'TW', '台達電', '電源管理', 'TWD'),
  ('NVDA', 'US', 'NVIDIA', 'AI / Semiconductors', 'USD'),
  ('AMD', 'US', 'AMD', 'Semiconductors', 'USD'),
  ('AAPL', 'US', 'Apple', 'Consumer Technology', 'USD'),
  ('AVGO', 'US', 'Broadcom', 'Semiconductors', 'USD'),
  ('MU', 'US', 'Micron', 'Memory', 'USD'),
  ('MSFT', 'US', 'Microsoft', 'Cloud / AI', 'USD'),
  ('META', 'US', 'Meta', 'Internet', 'USD'),
  ('GOOGL', 'US', 'Google', 'Internet', 'USD'),
  ('AMZN', 'US', 'Amazon', 'Cloud / Commerce', 'USD')
on conflict (symbol) do nothing;

insert into us_market_linkage (
  session_date, nasdaq_score, sox_score, sp500_score, vix_score, tsm_adr_score,
  nvda_score, amd_score, aapl_score, avgo_score, mu_score, msft_score, meta_score, googl_score, amzn_score
)
values (
  current_date, 0.42, 0.55, 0.24, -0.31, 0.48,
  0.62, 0.34, 0.18, 0.47, 0.22, 0.19, 0.12, 0.16, 0.15
)
on conflict (session_date) do nothing;

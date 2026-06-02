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

create table if not exists stock_master (
  stock_id text primary key,
  stock_name text not null,
  market_type text not null,
  industry text,
  sub_industry text,
  supply_chain_tags text[] not null default '{}',
  is_listed boolean not null default false,
  is_otc boolean not null default false
);

create table if not exists price_daily (
  trade_date date not null,
  stock_id text not null references stock_master(stock_id) on delete cascade,
  open numeric(18, 4),
  high numeric(18, 4),
  low numeric(18, 4),
  close numeric(18, 4) not null,
  volume bigint,
  turnover_value numeric(24, 4),
  primary key (trade_date, stock_id)
);

create table if not exists fundamental_monthly (
  data_month date not null,
  stock_id text not null references stock_master(stock_id) on delete cascade,
  revenue numeric(24, 4),
  revenue_mom numeric(10, 4),
  revenue_yoy numeric(10, 4),
  revenue_acc_yoy numeric(10, 4),
  primary key (data_month, stock_id)
);

create table if not exists fundamental_quarterly (
  fiscal_year integer not null,
  quarter integer not null check (quarter between 1 and 4),
  stock_id text not null references stock_master(stock_id) on delete cascade,
  eps numeric(12, 4),
  gross_margin numeric(10, 4),
  operating_margin numeric(10, 4),
  net_margin numeric(10, 4),
  debt_ratio numeric(10, 4),
  operating_cash_flow numeric(24, 4),
  inventory numeric(24, 4),
  accounts_receivable numeric(24, 4),
  primary key (fiscal_year, quarter, stock_id)
);

create table if not exists institutional_trading_daily (
  trade_date date not null,
  stock_id text not null references stock_master(stock_id) on delete cascade,
  foreign_net bigint not null default 0,
  investment_trust_net bigint not null default 0,
  dealer_net bigint not null default 0,
  dealer_self_net bigint not null default 0,
  dealer_hedge_net bigint not null default 0,
  total_institutional_net bigint not null default 0,
  foreign_net_ratio numeric(10, 4),
  investment_trust_net_ratio numeric(10, 4),
  dealer_net_ratio numeric(10, 4),
  primary key (trade_date, stock_id)
);

create table if not exists technical_indicators_daily (
  trade_date date not null,
  stock_id text not null references stock_master(stock_id) on delete cascade,
  ma5 numeric(18, 4),
  ma20 numeric(18, 4),
  ma60 numeric(18, 4),
  rsi14 numeric(10, 4),
  k_value numeric(10, 4),
  d_value numeric(10, 4),
  ema12 numeric(18, 4),
  ema26 numeric(18, 4),
  dif numeric(18, 4),
  dea numeric(18, 4),
  macd_hist numeric(18, 4),
  macd_bar_tw numeric(18, 4),
  obv numeric(24, 4),
  volume_ma5 numeric(24, 4),
  volume_ma20 numeric(24, 4),
  bearish_volume_divergence boolean not null default false,
  bullish_volume_divergence boolean not null default false,
  volume_price_score numeric(10, 4),
  macd_score numeric(10, 4),
  technical_score numeric(10, 4),
  primary key (trade_date, stock_id)
);

create table if not exists us_market_daily (
  trade_date date not null,
  symbol text not null,
  symbol_type text not null,
  open numeric(18, 4),
  high numeric(18, 4),
  low numeric(18, 4),
  close numeric(18, 4) not null,
  volume bigint,
  return_1d numeric(10, 4),
  ma20 numeric(18, 4),
  ma60 numeric(18, 4),
  rsi14 numeric(10, 4),
  dif numeric(18, 4),
  dea numeric(18, 4),
  macd_hist numeric(18, 4),
  volume_price_signal numeric(10, 4),
  primary key (trade_date, symbol)
);

create table if not exists us_tw_supply_chain_map (
  us_ticker text not null,
  us_company_name text not null,
  tw_stock_id text not null references stock_master(stock_id) on delete cascade,
  tw_stock_name text not null,
  relation_type text not null,
  supply_chain_tag text not null,
  sensitivity_weight numeric(10, 4) not null default 0,
  impact_lag_days integer not null default 0,
  confidence numeric(10, 4) not null default 0,
  primary key (us_ticker, tw_stock_id, relation_type, supply_chain_tag)
);

create table if not exists news_events (
  id uuid primary key default gen_random_uuid(),
  event_time timestamptz not null,
  market text not null,
  stock_id text references stock_master(stock_id) on delete set null,
  related_symbol text,
  related_industry text,
  source text not null,
  title text not null,
  summary text,
  sentiment_score numeric(10, 4),
  event_type text,
  impact_score numeric(10, 4),
  confidence numeric(10, 4)
);

create table if not exists factor_scores_daily (
  trade_date date not null,
  stock_id text not null references stock_master(stock_id) on delete cascade,
  fundamental_score numeric(10, 4),
  chip_score numeric(10, 4),
  macro_score numeric(10, 4),
  technical_score numeric(10, 4),
  news_score numeric(10, 4),
  us_market_score numeric(10, 4),
  target_price_score numeric(10, 4),
  risk_score numeric(10, 4),
  bullish_score numeric(10, 4),
  risk_adjusted_score numeric(10, 4),
  probability_up_1d numeric(10, 4),
  probability_up_5d numeric(10, 4),
  probability_up_20d numeric(10, 4),
  top_positive_factors jsonb not null default '[]'::jsonb,
  top_negative_factors jsonb not null default '[]'::jsonb,
  top_risk_factors jsonb not null default '[]'::jsonb,
  confidence numeric(10, 4),
  primary key (trade_date, stock_id)
);

insert into stock_master (stock_id, stock_name, market_type, industry, sub_industry, supply_chain_tags, is_listed, is_otc)
values
  ('2330', '台積電', 'TWSE', '半導體', '晶圓代工', array['AI', 'foundry', 'TSM_ADR'], true, false),
  ('2454', '聯發科', 'TWSE', '半導體', 'IC設計', array['mobile', 'edge-ai'], true, false),
  ('2317', '鴻海', 'TWSE', '電子代工', 'EMS', array['AI-server', 'Apple'], true, false),
  ('2308', '台達電', 'TWSE', '電源管理', '電源供應器', array['AI-server', 'energy'], true, false)
on conflict (stock_id) do nothing;

insert into price_daily (trade_date, stock_id, open, high, low, close, volume, turnover_value)
values
  (current_date, '2330', 1080, 1095, 1075, 1088, 32100000, 34900000000),
  (current_date, '2454', 1330, 1350, 1320, 1342, 8200000, 11000000000),
  (current_date, '2317', 165, 168, 163, 166, 41000000, 6800000000),
  (current_date, '2308', 395, 402, 392, 400, 7200000, 2880000000)
on conflict (trade_date, stock_id) do nothing;

insert into us_market_daily (trade_date, symbol, symbol_type, open, high, low, close, volume, return_1d, ma20, ma60, rsi14, dif, dea, macd_hist, volume_price_signal)
values
  (current_date, 'NASDAQ', 'index', 19000, 19180, 18920, 19120, null, 0.42, 18800, 18450, 61, 120, 88, 32, 0.18),
  (current_date, 'SOX', 'index', 5200, 5280, 5180, 5265, null, 0.55, 5120, 4980, 64, 44, 31, 13, 0.22),
  (current_date, 'VIX', 'risk', 14, 14.4, 13.7, 13.9, null, -0.31, 15, 16, 42, -0.2, -0.1, -0.1, -0.08),
  (current_date, 'NVDA', 'stock', 140, 144, 139, 143, 280000000, 0.62, 136, 128, 68, 3.4, 2.9, 0.5, 0.25)
on conflict (trade_date, symbol) do nothing;

insert into us_tw_supply_chain_map (us_ticker, us_company_name, tw_stock_id, tw_stock_name, relation_type, supply_chain_tag, sensitivity_weight, impact_lag_days, confidence)
values
  ('NVDA', 'NVIDIA', '2330', '台積電', 'customer', 'AI', 0.85, 1, 0.8),
  ('AAPL', 'Apple', '2317', '鴻海', 'customer', 'Apple', 0.75, 1, 0.75),
  ('TSM_ADR', 'TSM ADR', '2330', '台積電', 'adr', 'foundry', 0.9, 0, 0.9)
on conflict (us_ticker, tw_stock_id, relation_type, supply_chain_tag) do nothing;

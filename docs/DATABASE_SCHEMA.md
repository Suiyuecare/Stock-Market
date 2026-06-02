# Database Schema

The local Docker schema lives in `infra/postgres/init.sql`.

This MVP schema uses explicit domain table names for Taiwan stocks, US linkage, news events, and final daily factor scores. It is optimized for explainable factor analysis rather than trade execution.

## `stock_master`

Taiwan stock master.

- `stock_id`
- `stock_name`
- `market_type`
- `industry`
- `sub_industry`
- `supply_chain_tags`
- `is_listed`
- `is_otc`

## `price_daily`

Taiwan daily price.

- `trade_date`
- `stock_id`
- `open`
- `high`
- `low`
- `close`
- `volume`
- `turnover_value`

Primary key:

- `(trade_date, stock_id)`

## `fundamental_monthly`

Monthly fundamentals.

- `data_month`
- `stock_id`
- `revenue`
- `revenue_mom`
- `revenue_yoy`
- `revenue_acc_yoy`

Primary key:

- `(data_month, stock_id)`

## `fundamental_quarterly`

Quarterly fundamentals.

- `fiscal_year`
- `quarter`
- `stock_id`
- `eps`
- `gross_margin`
- `operating_margin`
- `net_margin`
- `debt_ratio`
- `operating_cash_flow`
- `inventory`
- `accounts_receivable`

Primary key:

- `(fiscal_year, quarter, stock_id)`

## `institutional_trading_daily`

Institutional trading.

- `trade_date`
- `stock_id`
- `foreign_net`
- `investment_trust_net`
- `dealer_net`
- `dealer_self_net`
- `dealer_hedge_net`
- `total_institutional_net`
- `foreign_net_ratio`
- `investment_trust_net_ratio`
- `dealer_net_ratio`

Primary key:

- `(trade_date, stock_id)`

## `technical_indicators_daily`

Technical indicators.

- `trade_date`
- `stock_id`
- `ma5`
- `ma20`
- `ma60`
- `rsi14`
- `k_value`
- `d_value`
- `ema12`
- `ema26`
- `dif`
- `dea`
- `macd_hist`
- `macd_bar_tw`
- `obv`
- `volume_ma5`
- `volume_ma20`
- `bearish_volume_divergence`
- `bullish_volume_divergence`
- `volume_price_score`
- `macd_score`
- `technical_score`

Primary key:

- `(trade_date, stock_id)`

## `us_market_daily`

US market data.

- `trade_date`
- `symbol`
- `symbol_type`
- `open`
- `high`
- `low`
- `close`
- `volume`
- `return_1d`
- `ma20`
- `ma60`
- `rsi14`
- `dif`
- `dea`
- `macd_hist`
- `volume_price_signal`

Primary key:

- `(trade_date, symbol)`

## `us_tw_supply_chain_map`

US-Taiwan supply chain mapping.

- `us_ticker`
- `us_company_name`
- `tw_stock_id`
- `tw_stock_name`
- `relation_type`
- `supply_chain_tag`
- `sensitivity_weight`
- `impact_lag_days`
- `confidence`

## `news_events`

News events.

- `event_time`
- `market`
- `stock_id`
- `related_symbol`
- `related_industry`
- `source`
- `title`
- `summary`
- `sentiment_score`
- `event_type`
- `impact_score`
- `confidence`

## `factor_scores_daily`

Final factor scores.

- `trade_date`
- `stock_id`
- `fundamental_score`
- `chip_score`
- `macro_score`
- `technical_score`
- `news_score`
- `us_market_score`
- `target_price_score`
- `risk_score`
- `bullish_score`
- `risk_adjusted_score`
- `probability_up_1d`
- `probability_up_5d`
- `probability_up_20d`
- `top_positive_factors`
- `top_negative_factors`
- `top_risk_factors`
- `confidence`

Primary key:

- `(trade_date, stock_id)`

## Operational Tables

### `market_sessions`

Tracks scheduled market processing phases.

- `id`
- `market`
- `session_date`
- `phase`
- `status`
- `created_at`

## Migration Direction

The MVP uses init SQL for local Docker. Before production, move schema changes to explicit migrations with Alembic or another migration tool.

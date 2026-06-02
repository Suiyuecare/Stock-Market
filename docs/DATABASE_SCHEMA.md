# Database Schema

The local Docker schema lives in `infra/postgres/init.sql`.

The SQLAlchemy models live in `backend/app/models/`.

Alembic migrations live in `backend/alembic/`.

This MVP schema uses explicit domain table names for Taiwan stocks, US linkage, news events, and final daily factor scores. It is optimized for explainable factor analysis rather than trade execution.

## `data_availability_ledger`

Data availability ledger for point-in-time correctness.

This table records when each source dataset is officially published, ingested by
the system, and safe to use for signal generation. Backtests and signal jobs must
only use rows where:

```text
available_for_signal_at <= signal_generated_at
```

This prevents look-ahead bias, such as using monthly revenue before its official
publication date.

- `id`
- `source`
- `dataset_name`
- `symbol`
- `data_date`
- `published_at`
- `ingested_at`
- `available_for_signal_at`
- `revision_number`
- `checksum`
- `raw_payload_path`

Uniqueness:

- `(source, dataset_name, symbol, data_date, revision_number)`

## `feature_store_daily`

Point-in-time feature store for daily factor values.

All factor inputs should be materialized here before scoring. Signal generation
and backtests should read the feature values that were available at the signal
time instead of recalculating against mutable source data.

Backtests and signal jobs must only use rows where:

```text
available_for_signal_at <= signal_generated_at
```

- `trade_date`
- `stock_id`
- `feature_group`
- `feature_name`
- `feature_value`
- `feature_version`
- `calculated_at`
- `available_for_signal_at`

Primary key:

- `(trade_date, stock_id, feature_group, feature_name, feature_version)`

## `labels_daily`

Point-in-time labels for training, backtesting, and signal evaluation.

Labels should be generated after the required future window is complete and
should never be used as features. The table supports multiple optimization
targets, including absolute return, relative return versus benchmark, take
profit / stop loss path labels, and risk-adjusted labels.

- `trade_date`
- `stock_id`
- `label_name`
- `label_value`
- `horizon_days`
- `label_version`
- `forward_return`
- `benchmark_return`
- `excess_return`
- `max_favorable_excursion`
- `max_adverse_excursion`
- `transaction_cost`
- `minimum_excess_return`
- `calculated_at`
- `available_for_signal_at`

Primary key:

- `(trade_date, stock_id, label_name, horizon_days, label_version)`

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

## `signals`

Generated point-in-time model signals.

- `signal_id`
- `generated_at`
- `trade_date`
- `stock_id`
- `horizon_days`
- `probability_up`
- `bullish_score`
- `risk_score`
- `risk_adjusted_score`
- `confidence`
- `signal_rank`
- `selected_for_watchlist`
- `rejection_reason`
- `model_version`
- `feature_version`

Primary key:

- `signal_id`

## `signal_outcomes`

Realized outcomes after each signal's holding window closes.

- `signal_id`
- `entry_date`
- `entry_price`
- `exit_date`
- `exit_price`
- `gross_return`
- `net_return`
- `benchmark_return`
- `excess_return`
- `win_absolute`
- `win_relative`
- `hit_take_profit`
- `hit_stop_loss`
- `max_favorable_excursion`
- `max_adverse_excursion`
- `holding_days`

Primary key:

- `signal_id`

## `signal_performance_stats`

Aggregated win-rate, calibration, and risk statistics by model, strategy, horizon, and segment.

- `model_version`
- `strategy_version`
- `horizon_days`
- `market_regime`
- `industry`
- `probability_bucket`
- `risk_bucket`
- `trade_count`
- `win_rate`
- `win_rate_lower_bound`
- `avg_net_return`
- `median_net_return`
- `profit_factor`
- `max_drawdown`
- `sharpe`
- `calibration_error`

Primary key:

- `(model_version, strategy_version, horizon_days, market_regime, industry, probability_bucket, risk_bucket)`

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

The MVP now includes an Alembic baseline migration:

```bash
cd backend
PYTHONPATH=. alembic -c alembic.ini upgrade head
```

Sample CSV loading is implemented in `app.services.data_providers.csv_seed_loader`. The loader maps early sample CSV column names into the production table names, such as `symbol` to `stock_id` and `foreign_net_buy` to `foreign_net`.

To load sample data into the configured database:

```bash
cd backend
PYTHONPATH=. python -m app.services.data_providers.seed_sample_data
```

# Database Schema

The initial schema lives in `infra/postgres/init.sql`.

## Tables

### `market_sessions`

Tracks scheduled market processing phases.

Columns:

- `id`
- `market`
- `session_date`
- `phase`
- `status`
- `created_at`

Unique key:

- `(market, session_date, phase)`

### `instruments`

Instrument master table.

Columns:

- `id`
- `symbol`
- `market`
- `name`
- `sector`
- `currency`
- `created_at`

Unique key:

- `symbol`

### `daily_prices`

Daily OHLCV data.

Columns:

- `id`
- `instrument_id`
- `trade_date`
- `open`
- `high`
- `low`
- `close`
- `volume`
- `created_at`

Unique key:

- `(instrument_id, trade_date)`

### `news_events`

Raw and parsed news/event records.

Columns:

- `id`
- `source`
- `title`
- `url`
- `published_at`
- `raw_text`
- `parsed_json`
- `created_at`

### `prediction_signals`

Model output and explainability payload.

Columns:

- `id`
- `instrument_id`
- `signal_date`
- `horizon`
- `score`
- `confidence`
- `drivers`
- `created_at`

## Future Tables

- `users`
- `watchlists`
- `watchlist_items`
- `factor_values`
- `model_runs`
- `backtest_runs`
- `provider_ingestion_logs`

## Migration Direction

The MVP uses init SQL for local Docker. Before production, move schema changes to explicit migrations with a migration tool such as Alembic.

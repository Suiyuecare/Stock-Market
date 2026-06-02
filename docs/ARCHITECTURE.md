# Architecture

## System Overview

```mermaid
flowchart LR
  Sources["Market Data / News Sources"] --> Jobs["Background Jobs"]
  Jobs --> Parser["LLM News Parser"]
  Jobs --> FactorEngine["Factor Engine"]
  Parser --> DB[(PostgreSQL)]
  FactorEngine --> DB
  DB --> API["FastAPI"]
  Redis[(Redis)] --> Jobs
  API --> Web["Next.js Dashboard"]
```

## Components

### Frontend

- Next.js app router
- React server components for API-backed dashboard data
- Client component for lightweight-charts
- Reads API through `NEXT_PUBLIC_API_BASE_URL`

### Backend

- FastAPI service under `/api`
- Pydantic schemas as API contracts
- Route modules under `backend/app/api/`
- Pydantic schemas under `backend/app/schemas/`
- Scoring modules under `backend/app/services/scoring/`
- Indicator modules under `backend/app/services/indicators/`
- Backtest Lab under `backend/app/services/backtest_lab.py`
- Probability Calibration under `backend/app/services/probability_calibration.py`
- Market Regime Engine under `backend/app/services/market_regime_engine.py`
- Signal Selection Layer under `backend/app/services/signal_selection_layer.py`
- Portfolio Risk Engine under `backend/app/services/portfolio_risk_engine.py`
- Explainability Report Builder under `backend/app/services/explainability_report.py`
- Model Monitoring Engine under `backend/app/services/model_monitoring.py`
- Signal Quality Evaluator under `backend/app/services/signal_quality_evaluator.py`
- Provider interfaces under `backend/app/services/data_providers/`
- pytest contract tests

### API Surface

The MVP API can run with mock/sample data or official open-data providers. Production deployment should set the active provider mode explicitly so the UI can label whether a payload is live official data, delayed official data, or demo data.

- `GET /api/stocks`
- `GET /api/stocks/{stock_id}`
- `GET /api/stocks/{stock_id}/scores`
- `GET /api/stocks/{stock_id}/technical`
- `GET /api/stocks/{stock_id}/institutional`
- `GET /api/stocks/{stock_id}/news`
- `GET /api/rankings/top-probability`
- `GET /api/rankings/institutional-buying`
- `GET /api/rankings/macd-golden-cross`
- `GET /api/rankings/volume-price-divergence`
- `GET /api/us-market/radar`
- `GET /api/risk/high-risk`
- `GET /api/monitoring/readiness`
- `GET /api/monitoring/alerts`

All scoring endpoints return explainable research payloads and the standard disclaimer. They must not return direct investment advice.

### Database

- PostgreSQL
- Seed schema in `infra/postgres/init.sql`
- Tables for instruments, daily prices, news events, market sessions, and prediction signals

### Cache / Queue

- Redis is included for cache and queue-ready architecture
- APScheduler is used for the first scheduling skeleton
- Celery is included so high-volume ingestion can move to queue workers later

### Background Jobs

- `tw-after-close`: after Taiwan market close, processes daily Taiwan data
- `us-premarket-linkage`: before US open, computes US linkage signals
- `news-event-parser`: normalizes news into structured impact signals

Implemented MVP job behavior still uses mock providers first, but scheduled runs now persist write-ready artifacts when a database session is provided:

- `daily_after_market_job` updates mock Taiwan prices, institutional/chip data, technical indicators, final factor scores, and data availability ledger rows.
- `pre_open_us_market_job` updates mock US market linkage proxy rows, calculates per-stock USMarketScore, generates a pre-open radar ranking, and writes data availability ledger rows.
- `news_ingestion_job` ingests mock provider news, classifies events through the parser interface, writes normalized news events, and writes data availability ledger rows.

Direct function calls can still return artifacts without persistence for tests and local inspection. The scheduler wrappers create a SQLAlchemy session and persist artifacts into PostgreSQL. The provider layer now includes official open-data fetchers for TWSE/MOPS company profiles, monthly revenue, material information, and CNA RSS parsing. The next deployment phase should switch scheduled jobs from mock providers to those open-data providers and keep writing artifacts into PostgreSQL with data availability ledger records.

### Operations Monitoring

The MVP includes a lightweight observability baseline that works without external monitoring keys:

- `job_runs` records every scheduled job execution, duration, status, result summary, and error message.
- `alert_events` records operational alerts such as failed scheduled jobs, provider failures, readiness problems, and unresolved launch issues.
- `OperationsMonitor.run_job` wraps scheduled jobs with structured logging, job run persistence, failure capture, and alert emission.
- `GET /api/monitoring/readiness` reports database reachability, scheduled-job status, open alert count, and the latest job runs.
- `GET /api/monitoring/alerts` lists unresolved operational alerts.

Sentry, Vercel log drains, email, SMS, and push notifications remain optional provider integrations. Without their environment variables, the app still records alerts in PostgreSQL and logs structured events for Vercel/runtime log inspection.

### Backtest Lab

Backtesting is intentionally separate from the live scoring modules. The lab consumes point-in-time signal observations, applies an explicit configuration, and reports research metrics without changing model logic.

Supported MVP controls:

- holding period
- entry probability threshold
- transaction cost and slippage
- take-profit and stop-loss exits
- market state, sector, market-cap, and liquidity filters
- chronological time-series split windows

Required result metrics include win rate, trade count, average and median return, expectancy, max drawdown, Profit Factor, Sharpe Ratio, Sortino Ratio, max single loss, max consecutive losses, average holding days, turnover, sector win rate, and market-state win rate.

Backtests must use features and labels that were available at the signal timestamp. Do not use revised fundamentals, later-published labels, or future market data when simulating historical signals.

### Probability Calibration

Probability calibration is independent from the scoring formula. It compares historical predicted probabilities with realized labels and reports whether the displayed probability is trustworthy.

Supported MVP outputs:

- Calibration Curve buckets such as 60%-65%, 65%-70%, and 70%-75%
- Brier Score for probability accuracy
- Probability Bucket Backtest with sample count, average predicted probability, actual win rate, calibration error, and reliability status
- segment filters for horizon, sector, and market state

If a bucket predicts 80% but the realized win rate is near 55%, the bucket should be marked overconfident and reviewed before showing high-confidence language in the UI.

### Market Regime Engine

The market regime engine classifies the current environment and emits dynamic factor-weight guidance. It is separate from the raw scoring modules so the app can change factor emphasis without rewriting each factor.

MVP regimes:

- bull market
- bear market
- range market
- high-volatility market
- low-volatility market
- foreign inflow and foreign outflow
- US technology strength and weakness

Examples:

- bull markets increase technical breakout, institutional flow, and fundamental momentum weights
- bear markets increase the RiskScore multiplier and reduce trend-following confidence
- range markets emphasize technical structure, volume-price divergence, and support/resistance context
- US technology strength increases USMarketScore sensitivity for semiconductor and electronics supply-chain names

### Signal Selection Layer

The signal selection layer runs after probability scoring, calibration, risk scoring, and regime analysis. Its job is to decide whether a signal should be shown as a primary research candidate, downgraded, marked high risk, or excluded.

Selection checks:

- probability threshold
- RiskScore threshold
- calibration sample count
- model confidence
- liquidity score
- major negative news or material event flags
- high-risk event windows such as earnings, conference calls, and ex-dividend periods
- factor conflict checks such as positive US linkage but weak Taiwan institutional/chip score

The layer intentionally supports a no-signal decision. The system should prefer fewer, higher-confidence research signals over broad daily lists.

### Portfolio Risk Engine

The portfolio risk engine turns selected research signals into a simulated risk-aware watchlist. It does not place orders or provide personalized portfolio advice.

MVP controls:

- single-stock maximum weight
- sector maximum weight
- maximum holding count
- maximum new signals per day
- drawdown and volatility deleveraging
- consecutive-loss deleveraging
- high-VIX exposure reduction
- weak US futures electronics exposure reduction

Example: if 30 high-scoring names are all in AI server supply chains, the engine caps sector exposure and keeps only the highest-ranked subset instead of allowing the watchlist to become one concentrated theme.

### Explainability Report

The explainability report is the audit trail for every research signal. It records how the signal was generated and what the user saw.

Required trace fields:

- `signal_id`
- generation timestamp
- data sources, versions, and fields used
- point-in-time data availability
- model and scoring versions
- score calculation details
- positive, negative, and risk factor explanations
- historical calibration or similar-condition win-rate summary
- selection decision and portfolio risk context
- user-visible text and disclaimer

The report should be generated before rendering a stock detail page so the UI explanation and backend calculation remain traceable.

### Model Monitoring

Model monitoring runs after daily labels, backtests, calibration, and operations metrics are available. It tracks whether the model is still behaving like its historical baseline.

Monitored metrics:

- recent 20-day and 60-day win rates
- recent 20-day average return and max drawdown
- prediction calibration error
- sector win-rate changes
- factor contribution drift
- data latency
- API failure rate
- news parsing error rate

If the recent 20-day win rate falls below the historical mean by more than two standard deviations, the engine marks `possible_model_decay`, lowers the signal-strength multiplier, and recommends retraining or recalibration review.

### Signal Quality Evaluation

Signal quality evaluation runs on backtest outputs before a signal definition is treated as production-worthy. It checks whether the signal has more than a high win rate.

Required checks:

- high enough win rate
- positive expectancy after costs
- positive average return after costs
- acceptable drawdown
- sufficient sample count
- Profit Factor above threshold

This prevents strategies such as many small wins and a few large losses from being accepted just because the headline win rate looks high.

## Runtime

Local development is Docker Compose:

- `postgres`
- `redis`
- `api`
- `worker`
- `frontend`

## Data Flow

1. Jobs ingest market and news inputs.
2. Parser and factor engine normalize raw data.
3. Prediction signals are stored in PostgreSQL.
4. FastAPI exposes signals and market summaries.
5. Next.js dashboard renders signals and charts.

## Deployment Notes

Phase 1 can deploy frontend and API separately. Keep the API stateless. Background jobs need a runtime that supports scheduled workers.

For production, choose managed PostgreSQL and Redis, and make sure data-source licenses allow the intended use.

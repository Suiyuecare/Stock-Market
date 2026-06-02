# Codex Tasks

This file breaks the project into safe implementation tasks for Codex.

## Task 1: Repo Foundation

Status: done

- Create scaffold
- Add README and AGENTS.md
- Add docs
- Add Docker Compose
- Add FastAPI health and signal endpoints
- Add Next.js dashboard skeleton
- Add pytest smoke tests

## Task 1.5: MVP Factor Skeleton

Status: done

- Add technical indicators
- Add factor engine
- Add US linkage scoring
- Add risk scoring
- Add mock provider data
- Add ranking and stock detail API routes
- Add dashboard sections for ranking, linkage, detail, factor explanation, risk, and news
- Add indicator and scoring tests

## Task 1.6: Repository Structure Alignment

Status: done

- Move backend toward models/schemas/api/services/tests layout
- Split scoring modules into separate files
- Split technical indicators into separate files
- Add provider interface placeholders
- Add frontend page routes and reusable dashboard components
- Add sample CSV data files

## Task 2: Database Access Layer

Goal:

- Replace placeholder market data service with PostgreSQL-backed queries.

Acceptance:

- `/api/market/summary` reads `instruments`
- `/api/predictions/signals` reads `prediction_signals`
- Tests cover empty and seeded database cases

## Task 3: Data Provider Interfaces

Goal:

- Add provider abstraction for TW daily data and US premarket data.

Acceptance:

- Interfaces do not depend on one vendor
- Mock provider tests pass
- Provider errors are logged and surfaced to job status

## Task 4: Factor Engine Baseline

Goal:

- Implement deterministic factor normalization and weighted scoring.

Acceptance:

- Unit tests for each factor
- Signal drivers include positive and negative contributors
- Scores are stable for fixed fixture input

## Task 5: News Parser

Goal:

- Implement OpenAI-compatible parser behind `NewsParser`.

Acceptance:

- No API key committed
- Parser returns strict JSON shape
- Rule-based fallback remains available
- Tests use fixtures, not live API calls

## Task 6: Frontend Dashboard

Goal:

- Connect dashboard to real API outputs and improve states.

Acceptance:

- Loading, empty, and error states
- Responsive layout
- Chart renders without console errors

## Task 7: Win-Rate Optimization And Backtesting

Goal:

- Build the complete point-in-time win-rate optimization loop.

Acceptance:

- Data availability timestamps are enforced.
- Feature snapshots are stored before signal generation.
- Labels use `up_5d_relative` as the main target.
- Walk-forward validation uses embargo windows and minimum trade counts.
- Strategy optimization ranks configurations by objective score, not raw win rate.
- Outputs include win-rate lower bound, average net return, Profit Factor, max drawdown, Sharpe ratio, calibration error, best parameter set, best/worst market regime, top positive factor combinations, and top failure patterns.
- Results are stored in `backtest_runs`, `backtest_results`, `strategy_parameters`, and `signal_performance_stats`.
- Tests prove no look-ahead bias in fixtures.

## Task 7.1: Performance Stats Engine

Goal:

- Aggregate signal outcomes into model/strategy/horizon/segment statistics.

Acceptance:

- Stats are grouped by market regime, industry, liquidity bucket, probability bucket, and risk bucket.
- Wilson lower-bound win rate is calculated.
- Calibration error is included.
- Tests cover small-sample penalty and segment grouping.

## Task 7.2: Strategy Optimizer

Goal:

- Search over thresholds, holding periods, stop-loss/take-profit settings, top-k limits, industry caps, factor weights, market regime filters, US linkage filters, MACD/volume-price filters, and institutional filters.

Acceptance:

- Constraint checks include total trades, trades per fold, positive average net return, Profit Factor above 1.2, max drawdown below limit, and confidence threshold.
- Best strategy version is selected by objective score.
- Rejected strategies include reasons.
- Tests cover a high raw win-rate small-sample strategy losing to a more robust lower-bound strategy.

## Task 7.3: Explainability And Monitoring Integration

Goal:

- Connect optimized strategy outputs to signal reports and model monitoring.

Acceptance:

- Every signal report can show factor combination, reference data, model version, feature version, strategy version, and signal outcome status.
- Monitoring checks recent win rate, calibration error, factor contribution drift, API/data delay, and parsing failures.
- Possible model decay reduces signal strength and emits an alert.

## Task 8: Deployment

Goal:

- Add deploy plan for frontend, API, DB, Redis, and worker.

Acceptance:

- Environment variables documented
- Scheduled worker runtime selected
- CI runs backend tests

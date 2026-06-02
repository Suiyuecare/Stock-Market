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

## Task 7: Backtesting

Goal:

- Add backtest tables and baseline backtest command.

Acceptance:

- Backtest result stored by model version
- Basic performance metrics available
- No look-ahead bias in fixtures

## Task 8: Deployment

Goal:

- Add deploy plan for frontend, API, DB, Redis, and worker.

Acceptance:

- Environment variables documented
- Scheduled worker runtime selected
- CI runs backend tests

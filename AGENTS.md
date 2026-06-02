# AGENTS.md

Repo-specific guidance for Codex and other coding agents.

## Product Direction

This repository is a Taiwan-US stock prediction web system. Do not start with a mobile app. The first serious milestone is a Web App + API + PostgreSQL + Redis + scheduled jobs foundation.

The first MVP is:

- Taiwan market after-close daily workflow
- US premarket linkage workflow
- Prediction signal dashboard
- Watchlist and model-driver summaries
- News/event parsing through an LLM provider interface

Do not build full real-time intraday trading in the first version. Realtime market data has licensing, cost, and reliability constraints.

## Tech Stack

- Frontend: Next.js / React
- Backend API: Python FastAPI
- Database: PostgreSQL
- Cache / Queue: Redis
- Background jobs: APScheduler first; Celery-compatible design when queue execution is needed
- AI parser: OpenAI-compatible provider interface
- Charts: TradingView lightweight-charts or Recharts
- Local runtime: Docker Compose
- Tests: pytest for backend; add frontend tests when UI logic becomes non-trivial

## Engineering Rules

- Keep API contracts typed with Pydantic models.
- Keep frontend API types aligned with backend response schemas.
- Keep financial model logic deterministic and testable.
- Separate data ingestion, feature/factor calculation, prediction scoring, and presentation.
- Never hard-code secret keys. Use `.env.example` for names only.
- Prefer explicit, legal, documented market-data providers. Do not scrape sources with unclear terms.
- Add tests for factor calculations, parser output normalization, and API contracts.

## MVP Boundaries

Allowed in MVP:

- Daily OHLCV storage
- Market/session status
- US/TW linkage signals
- Rule-based scoring baseline
- LLM news parser interface
- Background job skeletons

Not in MVP:

- Full realtime tick streaming
- Brokerage order execution
- Options/futures strategy execution
- Mobile app
- Paid data redistribution features

## Before Finishing Work

Run what is available locally:

```bash
PYTHONPATH=backend pytest backend/tests
```

If Docker is available:

```bash
docker compose up --build
```

Report any commands that could not run.

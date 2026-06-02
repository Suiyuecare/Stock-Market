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
- Provider interfaces under `backend/app/services/data_providers/`
- pytest contract tests

### API Surface

The MVP API uses mock/sample data until licensed market providers are connected.

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

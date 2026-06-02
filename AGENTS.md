# AGENTS.md

## Project overview

This project is a Taiwan + US stock factor analysis and prediction web app.

The system analyzes Taiwan stocks using:

1. Fundamental factors
2. Liquidity and institutional/chip factors
3. Macroeconomic factors
4. Technical factors
5. News and sentiment factors
6. US market linkage factors
7. Analyst target price / valuation factors
8. Risk scoring

The app must output explainable scores and probabilities, not direct buy/sell advice.

## Product rules

Do not use words such as:

- guaranteed profit
- must buy
- must sell
- 100% accurate
- insider tip

Use terms such as:

- probability
- factor score
- risk score
- historical backtest
- research signal
- educational analysis

## Engineering rules

- Use clear modular architecture.
- Add tests for all scoring functions.
- Keep data providers abstracted behind interfaces.
- Use mock data for MVP.
- Never commit API keys or secrets.
- Use `.env.example` for required environment variables.
- Prefer readable code over clever code.
- Write docstrings for non-trivial scoring logic.
- Keep frontend pages simple but useful.
- Every API response should include enough explanation for the UI to show why a score was generated.

## Backend stack

Preferred:

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- pytest

## Frontend stack

Preferred:

- React / Next.js
- TypeScript
- Simple dashboard UI
- Charts for price, MACD, volume, and factor scores

## Core scoring modules

Implement the scoring modules as separate files:

- `fundamental_score.py`
- `chip_score.py`
- `technical_score.py`
- `us_market_score.py`
- `news_score.py`
- `macro_score.py`
- `target_price_score.py`
- `risk_score.py`
- `final_prediction_score.py`

Each scoring function should return:

```json
{
  "score": 0,
  "positive_factors": [],
  "negative_factors": [],
  "risk_factors": [],
  "confidence": 0
}
```

## MVP boundaries

Allowed in MVP:

- Daily OHLCV storage
- Market/session status
- Taiwan after-close workflow
- US premarket linkage workflow
- Rule-based scoring baseline
- LLM news parser interface
- Background job skeletons

Not in MVP:

- Full realtime tick streaming
- Brokerage order execution
- Options/futures strategy execution
- Mobile app
- Paid data redistribution features

## Before finishing work

Validation:

- Run tests.
- Run type checks if configured.
- Update docs if architecture or APIs changed.
- Explain what changed.
- Mention any assumptions or missing data.

Run what is available locally:

```bash
PYTHONPATH=backend pytest backend/app/tests
```

If frontend dependencies are installed:

```bash
cd frontend
pnpm run build
```

If Docker is available:

```bash
docker compose up --build
```

Report any commands that could not run.

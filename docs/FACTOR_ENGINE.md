# Factor Engine

## Purpose

The factor engine converts raw market, macro, and news inputs into normalized prediction drivers. It should be deterministic, explainable, and testable before adding machine learning complexity.

## MVP Prediction Horizon

- Primary horizon: next Taiwan trading session
- Secondary horizon: short swing, 3 to 5 sessions
- Current MVP uses placeholder rule-based scoring

## Initial Factor Groups

### Taiwan After-Close Factors

- Daily return
- Gap from previous close
- Volume relative to recent average
- Sector breadth
- Foreign investor flow when a legal data source is available

### US Premarket Linkage Factors

- NASDAQ futures direction
- S&P 500 futures direction
- Philadelphia Semiconductor Index movement
- Major US tech stock moves
- ADR spread for Taiwan-linked names such as TSM
- USD/TWD and DXY direction

### News/Event Factors

- Company-specific news
- Sector news
- Macro and rate news
- Export control and geopolitical news
- Earnings guidance and analyst revisions

### Risk Factors

- Technical volatility
- Liquidity
- Concentration
- News/event risk
- VIX / US risk proxy

## Scoring Contract

Each factor should produce:

```json
{
  "type": "us-tech",
  "label": "NASDAQ futures positive",
  "value": 0.42,
  "weight": 0.28,
  "direction": "positive",
  "confidence": 0.61,
  "source": "provider-name"
}
```

Prediction signals aggregate factors into:

- `score`: normalized directional score from -1 to 1 or 0 to 1, depending on model version
- `confidence`: quality and agreement of factors
- `drivers`: top positive and negative reasons

## Baseline Model

Start with a rule-based weighted score:

```text
score = sum(normalized_factor_value * factor_weight)
confidence = data_quality * factor_agreement * recency_weight
```

Only after baseline backtests are available should the project add ML models.

## Implemented MVP Modules

- `app.services.indicators`
- `app.services.scoring`
- `app.services.data_providers.mock_provider`

Implemented indicators:

- MA 5 / 20 / 60
- RSI 14
- KD 9
- MACD
- OBV
- Volume-price divergence

Implemented factor categories:

- Fundamental quality
- Institutional flow
- Technical structure
- US market linkage
- News sentiment
- Risk score adjustment

## Testing Requirements

- Unit test each factor normalization function.
- Snapshot test parser outputs for fixed news examples.
- Backtest score behavior over historical periods before showing strong labels in UI.

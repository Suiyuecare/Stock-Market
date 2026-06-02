# Factor Engine

## Purpose

The factor engine converts raw market, fundamental, institutional, technical, news, and risk inputs into deterministic, explainable scores.

The factor engine should calculate scores from `0` to `100`.

Scores must be used as research signals and educational analysis only. The system must not output direct investment advice such as buy, sell, guaranteed profit, or 100% accurate predictions.

## Main Modules

### 1. FundamentalScore

Inputs:

- Monthly revenue YoY
- Monthly revenue MoM
- Accumulated revenue YoY
- EPS growth
- Gross margin trend
- Operating margin trend
- Debt ratio
- Operating cash flow
- Industry momentum

### 2. ChipScore

Inputs:

- Foreign investor net buy/sell
- Investment trust net buy/sell
- Dealer net buy/sell
- Consecutive net-buy days
- Net buy ratio relative to volume
- Margin trading if available
- Institutional synchronization

### 3. TechnicalScore

Inputs:

- MA5, MA20, MA60 trend
- MACD DIF/DEA/histogram
- MACD golden cross / death cross
- MACD bullish divergence / bearish divergence
- Volume-price divergence
- RSI
- KD
- OBV
- Breakout / breakdown

### 4. USMarketScore

Inputs:

- Nasdaq return
- SOX return
- S&P 500 return
- VIX change
- TSM ADR implied premium/discount
- Nvidia, AMD, Apple, Broadcom, Micron movement
- US futures movement
- US news sentiment
- US-Taiwan supply chain sensitivity

MVP formula:

```text
USMarketScore =
  0.20 * USIndexScore
+ 0.25 * USSemiconductorAIScore
+ 0.20 * USSupplyChainStockScore
+ 0.15 * ADRScore
+ 0.10 * USMacroLiquidityScore
+ 0.10 * USNewsSentimentScore
```

Industry rules:

- Semiconductor stocks use high sensitivity to SOX, SMH/SOXX, TSM ADR, NVDA, AMD, AVGO, ASML, and AMAT.
- AI server stocks use high sensitivity to NVDA, AMD, AVGO, MSFT, META, GOOGL, and AMZN.
- Apple supply chain stocks use high sensitivity to AAPL and Apple guidance/news.
- Memory stocks use high sensitivity to MU and memory-related news.
- Financial stocks use higher sensitivity to US yields, Fed/liquidity proxies, S&P 500, and VIX.
- Domestic demand stocks use lower US market sensitivity, so strong US moves only add a small score impact.

### 5. NewsScore

Inputs:

- Taiwan company material news
- Earnings news
- Revenue news
- Industry news
- US company news
- Event type
- Sentiment score
- Confidence

### 6. RiskScore

Inputs:

- 20-day volatility
- Beta
- Max drawdown
- Liquidity
- Institutional selling
- Margin overheat
- Negative news
- Financial weakness
- US market risk
- VIX increase

### 7. FinalPredictionScore

Inputs:

- FundamentalScore
- ChipScore
- TechnicalScore
- USMarketScore
- NewsScore
- MacroScore
- TargetPriceScore
- LiquidityScore
- RiskScore

## MVP Formula

All component scores should be normalized to `0` to `100` before aggregation.

```text
BullishScore =
  0.20 * FundamentalScore
+ 0.18 * ChipScore
+ 0.17 * TechnicalScore
+ 0.15 * USMarketScore
+ 0.12 * NewsScore
+ 0.08 * MacroScore
+ 0.05 * TargetPriceScore
+ 0.05 * LiquidityScore
```

```text
RiskAdjustedScore =
  BullishScore - 0.35 * RiskScore
```

## Probability Outputs

The engine should output:

- `probability_up_1d`
- `probability_up_5d`
- `probability_up_20d`

For MVP, map `RiskAdjustedScore` to probability using a logistic function or a calibrated rule-based scale. Later, replace it with a trained ML model after enough historical data, labels, and backtests are available.

## Scoring Contract

Each scoring module should return enough explanation for the API and UI to show why a score was generated.

```json
{
  "score": 0,
  "positive_factors": [],
  "negative_factors": [],
  "risk_factors": [],
  "confidence": 0
}
```

Where:

- `score` is normalized from `0` to `100`.
- `positive_factors` explains the strongest favorable drivers.
- `negative_factors` explains the strongest unfavorable drivers.
- `risk_factors` explains risk-specific issues.
- `confidence` is normalized from `0` to `100` and reflects data quality, freshness, agreement, and provider reliability.

## Implemented MVP Modules

Current code is scaffolded around:

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

Implemented MACD outputs:

- EMA12
- EMA26
- DIF
- DEA
- MACD histogram
- Taiwan-style MACD bar, calculated as `2 * (DIF - DEA)`
- Golden cross / death cross
- Zero-axis cross up / zero-axis cross down
- Bullish MACD divergence / bearish MACD divergence

Implemented volume-price states:

- Price up + volume up
- Price up + volume down
- Price down + volume down
- Price down + volume up
- Price new high without volume/OBV/MACD confirmation
- Price new low without MACD/OBV making a new low

Implemented technical score sub-scores:

- `trend_score`
- `volume_price_score`
- `macd_score`
- `rsi_score`
- `kd_score`
- `breakout_score`

Implemented factor categories:

- Fundamental quality
- Institutional flow
- Technical structure
- US market linkage
- News sentiment
- Risk score adjustment

Implemented US market linkage factors:

- Nasdaq, QQQ, S&P 500, US futures
- SOX, SMH/SOXX, NVDA, AMD, AVGO, ASML, AMAT, MU
- AAPL, MSFT, META, GOOGL, AMZN
- TSM ADR return and implied premium/discount
- VIX and US yield/liquidity proxies
- US news sentiment, Apple guidance, and memory news sentiment
- Taiwan stock supply-chain tags
- US-TW sensitivity mapping with confidence weighting

Implemented institutional/chip factors:

- `foreign_net_ratio = foreign_net / volume`
- `investment_trust_net_ratio = investment_trust_net / volume`
- `dealer_net_ratio = dealer_net / volume`
- `institutional_net_ratio = total_institutional_net / volume`
- Consecutive foreign net-buy days
- Consecutive investment trust net-buy days
- Foreign and investment trust simultaneous net buying
- Foreign, investment trust, and dealer synchronized buying
- Foreign, investment trust, and dealer synchronized selling
- Foreign buying while investment trust is selling
- Investment trust accumulation
- Investment trust continuous selling while price is below MA20
- Institutional reversal from buying to selling

## Implementation Notes

- MVP data providers use mock/sample data first so the app can run without paid data licenses.
- Real providers should be added behind provider interfaces.
- Do not hardcode API keys or secrets.
- Do not scrape paid or restricted data sources.
- Keep scoring deterministic and unit-testable before introducing machine learning.
- Backtest score behavior over historical periods before showing stronger labels in the UI.

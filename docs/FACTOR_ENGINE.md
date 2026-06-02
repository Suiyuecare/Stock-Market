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

### 8. MarketRegimeEngine

Inputs:

- Taiwan index 20-day and 60-day return
- Taiwan index MA60 trend state
- 20-day volatility and volatility percentile
- Foreign investor 20-day net flow
- Nasdaq, SOX, VIX, and TSM ADR momentum

Regimes:

- bull market
- bear market
- range market
- high-volatility market
- low-volatility market
- foreign inflow market
- foreign outflow market
- US technology strength
- US technology weakness

The regime engine returns factor-weight adjustments instead of direct investment advice. For example, bear markets raise the RiskScore multiplier, range markets increase technical/volume-price context, and US technology strength increases USMarketScore impact for electronics and semiconductor-linked stocks.

### 9. SignalSelectionLayer

Inputs:

- predicted probability
- RiskScore
- confidence
- calibration sample count
- liquidity score
- chip score
- USMarketScore
- major negative event flag
- high-risk event window flag, such as earnings, conference call, or ex-dividend windows

The selection layer decides whether a signal enters the primary watchlist, high-risk watchlist, low-confidence watchlist, or is excluded. It gives the system a no-signal option, which is necessary when probability is high but liquidity, risk, sample size, or event risk is unacceptable.

Examples:

- high probability and acceptable risk: primary watchlist
- high probability and high RiskScore: high-risk watchlist
- high probability and low calibration sample count: low-confidence watchlist
- high probability and poor liquidity: excluded
- US linkage positive but Taiwan chip score weak: low-confidence watchlist

### 10. PortfolioRiskEngine

Inputs:

- selected research signals
- proposed simulated weights
- sector and electronics exposure tags
- current drawdown
- portfolio volatility
- consecutive losses
- VIX level
- US futures movement

Controls:

- maximum single-stock weight
- maximum sector weight
- maximum holding count
- maximum new signals per day
- max drawdown deleveraging
- max volatility deleveraging
- consecutive-loss deleveraging
- high-VIX exposure reduction
- weak US futures electronics exposure reduction

The portfolio engine is for simulated research exposure, not order placement. It can reduce a broad list of high-scoring names into a smaller watchlist that respects concentration and market-risk limits.

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

Each indicator keeps a numeric function for compatibility and exposes an explainable analysis function:

- `analyze_moving_averages`
- `analyze_rsi`
- `analyze_kd`
- `analyze_obv`
- `analyze_macd`
- `analyze_volume_price_divergence`

`build_technical_indicators` returns the legacy numeric fields plus a `signals` object containing the explainable payload for each indicator.

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

Implemented final prediction score:

- `calculate_final_prediction_score` combines FundamentalScore, ChipScore, TechnicalScore, USMarketScore, NewsScore, MacroScore, TargetPriceScore, LiquidityScore, and RiskScore.
- Component inputs are normalized to `0` to `100`, including legacy `-1` to `1` score payloads.
- `BullishScore` follows the MVP weighted formula.
- `RiskAdjustedScore` subtracts `0.35 * RiskScore`.
- `probability_up_1d`, `probability_up_5d`, and `probability_up_20d` are mapped from `RiskAdjustedScore` with an MVP logistic curve.
- API signal payloads keep the legacy `probability_up` field mapped to `probability_up_1d` for frontend compatibility.
- The response includes `explanation.component_scores`, `top_positive_factors`, `top_negative_factors`, `top_risk_factors`, and normalized confidence.

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

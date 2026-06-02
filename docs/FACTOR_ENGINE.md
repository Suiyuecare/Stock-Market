# Factor Engine

## Purpose

The factor engine converts raw market, fundamental, institutional, technical, news, and risk inputs into deterministic, explainable scores.

The factor engine should calculate scores from `0` to `100`.

Scores must be used as research signals and educational analysis only. The system must not output direct investment advice such as buy, sell, guaranteed profit, or 100% accurate predictions.

## Final Design Principle

The system should not look like it predicts well only because it has many data sources. It should prove when a signal is valid, when it fails, and why it was selected.

The core workflow is:

1. record when data becomes available
2. store point-in-time features
3. generate labels only after the future window closes
4. validate with walk-forward out-of-sample splits
5. optimize thresholds and factor combinations by objective score
6. calibrate probabilities
7. apply market-regime, risk, liquidity, and confluence filters
8. track signal outcomes
9. update performance statistics
10. monitor model decay
11. produce an explainability report for every signal

Maximum-win-rate evaluation should optimize:

```text
WinRateLowerBound
+ AverageNetReturnScore
+ ProfitFactorScore
+ CalibrationScore
+ StabilityScore
- MaxDrawdownPenalty
```

Raw win rate is supporting context only. A signal is stronger when it has enough samples, positive net expectancy after costs, acceptable drawdown, stable behavior across years and market regimes, and clear factor confluence.

## Main Modules

### 0. Target Variables

Target variables define what the model is trying to predict. The MVP supports three horizons:

- `up_1d`
- `up_5d`
- `up_20d`

Formal timing:

```text
signal_time = t day after market close
entry_price = t+1 open or t+1 VWAP
exit_price = t+h close
net_return = exit_price / entry_price - 1 - fee - transaction_tax - slippage
```

Target definitions:

```text
y_abs_h = 1 if net_return_h > 0 else 0
y_rel_h = 1 if net_return_h > benchmark_return_h + cost_buffer + minimum_excess_return else 0
y_tp_sl_h = 1 if the path touches take-profit before stop-loss else 0
```

The primary MVP model target is `y_rel_5d`, because it asks whether a stock can outperform the Taiwan weighted index after costs and a minimum excess-return hurdle.

### 0.1 Universe Filters

Universe filters remove low-quality samples before model training, backtesting, and signal generation.

Default filters:

```yaml
universe_filters:
  min_listing_days: 250
  min_close_price: 10
  min_avg_turnover_20d_twd: 50000000
  exclude_full_delivery_stocks: true
  exclude_disposition_stocks: true
  exclude_attention_stocks_for_conservative_mode: true
  exclude_low_liquidity: true
  exclude_recent_extreme_gap: true
  exclude_missing_fundamental_data: true
```

These filters reduce misleading backtests from illiquid names, special-risk stocks, short listing histories, low-price stocks, and missing fundamental data.

### 0.2 Trade Management Variables

Trade management defines simulated entry and exit rules so win rate is measurable.

```yaml
trade_management:
  entry_method: next_open
  exit_method: fixed_horizon_or_tp_sl
  holding_days: [1, 5, 20]
  stop_loss_method: atr_or_percent
  stop_loss_pct_range: [0.03, 0.08]
  take_profit_pct_range: [0.05, 0.15]
  trailing_stop_enabled: true
  trailing_stop_atr: 1.5
  max_holding_days: 20
  cooldown_days_after_loss: 3
```

The engine should report three win definitions:

- fixed-horizon win: hold `h` days and net return is positive
- take-profit / stop-loss win: take-profit is touched before stop-loss
- relative win: fixed-horizon return beats benchmark return plus costs

### 0.3 Cost Variables

Backtests, labels, and simulated trade-management results must deduct costs before calculating win rate or expected return. Costs are configurable because stocks, ETFs, day trading, futures, brokers, liquidity buckets, and order sizes can have different fee, tax, and slippage assumptions.

```yaml
cost_model:
  commission_rate_buy: configurable
  commission_rate_sell: configurable
  transaction_tax_rate: configurable
  slippage_bps_large_cap: 3
  slippage_bps_mid_cap: 8
  slippage_bps_small_cap: 15
  min_fee: configurable
```

The cost model reports:

- buy-side commission
- sell-side commission
- sell-side transaction tax
- buy-side slippage
- sell-side slippage
- total cost amount
- total cost rate for return calculations

No backtest should report raw gross-return win rate as the primary result, because short-horizon strategies are easily overstated when transaction cost, tax, and liquidity slippage are ignored.

### 0.4 Validation Variables

Validation prevents the model from proving itself with contaminated or statistically weak samples. The MVP uses walk-forward validation rather than random splits, because stock signals are time-series data.

```yaml
validation:
  split_method: walk_forward
  train_window_days: 756
  validation_window_days: 126
  test_window_days: 126
  retrain_frequency: monthly
  embargo_days: 5
  min_trades_per_fold: 100
  min_total_trades: 500
  evaluate_by_market_regime: true
  evaluate_by_industry: true
  evaluate_by_liquidity_bucket: true
```

`embargo_days` creates a gap between train, validation, and test windows. This is required when predicting 5-day or 20-day returns because overlapping label periods can leak future information across adjacent windows.

Each validation run should report:

- fold windows and sample counts
- validation and test trade counts
- whether each fold passes `min_trades_per_fold`
- whether total test samples pass `min_total_trades`
- results by market regime, industry, and liquidity bucket
- warnings when the validation design is too weak to trust

### 0.5 Objective Score

Strategy selection should not optimize raw win rate alone. A tiny sample with a high observed win rate can be less reliable than a large sample with a lower but statistically stable win rate.

The MVP uses a Wilson lower-bound win rate plus return, profit factor, calibration, stability, and drawdown terms:

```text
AdjustedWinScore =
  WilsonLowerBoundWinRate
+ AverageNetReturnScore
+ ProfitFactorScore
- MaxDrawdownPenalty
- TurnoverPenalty

ObjectiveScore =
  0.40 * WinRateLowerBound
+ 0.20 * AverageNetReturnScore
+ 0.15 * ProfitFactorScore
+ 0.10 * CalibrationScore
+ 0.10 * StabilityScore
- 0.05 * MaxDrawdownPenalty
```

Components:

- `WinRateLowerBound`: Wilson confidence lower bound, used to discount small samples
- `AverageNetReturnScore`: average trade net return after costs
- `ProfitFactorScore`: gross profits divided by gross losses
- `CalibrationScore`: whether predicted probabilities match realized outcomes
- `StabilityScore`: whether performance is stable across years, industries, liquidity buckets, and market regimes
- `MaxDrawdownPenalty`: larger drawdowns reduce the objective score

The app should rank strategy configurations by `ObjectiveScore` and keep raw win rate as supporting context.

### 0.6 Factor Weight Profiles

Initial scoring uses manual factor weights. Later versions can replace these with model-learned weights after enough point-in-time labels, validation folds, and monitoring data exist.

General Taiwan stocks:

```text
FinalScore =
  0.20 * FundamentalScore
+ 0.18 * ChipScore
+ 0.17 * TechnicalScore
+ 0.15 * USMarketScore
+ 0.12 * NewsScore
+ 0.08 * MacroScore
+ 0.05 * TargetPriceScore
+ 0.05 * LiquidityScore
- 0.35 * RiskScore
```

Electronics, semiconductor, and AI supply-chain stocks:

```text
FinalScore =
  0.17 * FundamentalScore
+ 0.17 * ChipScore
+ 0.16 * TechnicalScore
+ 0.25 * USMarketScore
+ 0.10 * NewsScore
+ 0.05 * MacroScore
+ 0.05 * TargetPriceScore
+ 0.05 * LiquidityScore
- 0.35 * RiskScore
```

Domestic demand, traditional industry, and construction stocks:

```text
FinalScore =
  0.25 * FundamentalScore
+ 0.20 * ChipScore
+ 0.20 * TechnicalScore
+ 0.05 * USMarketScore
+ 0.15 * NewsScore
+ 0.10 * MacroScore
+ 0.05 * TargetPriceScore
- 0.35 * RiskScore
```

Bear or high-volatility markets:

```text
FinalScore =
  0.18 * FundamentalScore
+ 0.15 * ChipScore
+ 0.12 * TechnicalScore
+ 0.10 * USMarketScore
+ 0.10 * NewsScore
+ 0.05 * MacroScore
+ 0.05 * TargetPriceScore
+ 0.05 * LiquidityScore
- 0.55 * RiskScore
```

In bear markets, the goal is not to find more stocks. The system should raise thresholds, increase risk penalties, and reduce the number of generated signals.

### 0.8 Daily Model Pipeline

The MVP signal pipeline runs in ten steps:

1. Daily after-close feature snapshot
2. Generate t+1 tradable signals from t-day data
3. Predict `up_1d`, `up_5d`, and `up_20d`
4. Apply probability calibration
5. Apply risk filtering
6. Apply liquidity filtering
7. Apply industry concentration limits
8. Generate the research watchlist
9. Backtest realized outcomes after horizons close
10. Update win-rate performance statistics

The pipeline writes to:

- `signals`
- `signal_outcomes`
- `signal_performance_stats`

### 0.9 Bullish Confluence Signal

High-win-rate candidates should be treated as multi-factor confluence, not single-indicator triggers.

Bullish confluence requires:

- fundamental improvement
- bullish institutional/chip score
- bullish technical score
- no high-level volume-price divergence
- no MACD death cross or bearish MACD divergence
- supportive US market linkage
- no major negative news
- RiskScore below the high-risk threshold
- sufficient liquidity

MVP thresholds:

```yaml
bullish_confluence:
  min_fundamental_score: 60
  min_chip_score: 65
  min_technical_score: 65
  min_us_market_score: 55
  min_news_score: 50
  max_risk_score: 55
  min_liquidity_score: 50
  reject_macd_death_cross: true
  reject_macd_bearish_divergence: true
  reject_high_price_volume_divergence: true
  reject_three_institutions_sync_sell: true
  reject_major_negative_news: true
```

This intentionally produces fewer signals than a single-factor system, but each accepted signal has more aligned evidence and fewer obvious risk conflicts.

### 0.10 Signal Anti-Patterns

The system should avoid single-indicator signal design. These are not sufficient by themselves:

- MACD golden cross only
- foreign investor net buying only
- NVDA spike only
- positive news only
- technical breakout only
- highest model probability only

The correct signal gate requires:

- high model probability
- low risk
- enough historical samples
- multi-factor agreement
- positive expected value after transaction costs and slippage
- stable performance across different years
- no material failure across market regimes

Signals that rely on a single narrative should be rejected or downgraded even when the headline indicator looks strong.

### 0.7 MVP Initial Strategy Defaults

The MVP starts with a conservative preset designed for 5-day relative win-rate reliability:

```yaml
strategy_objective:
  primary: maximize_out_of_sample_win_rate_lower_bound
  secondary:
    - positive_expected_value
    - profit_factor_above_1_2
    - max_drawdown_below_limit
    - enough_trade_samples

label:
  main_target: up_5d_relative
  auxiliary_targets:
    - up_1d_absolute
    - up_20d_relative
  benchmark: TAIEX
  min_excess_return: 0.003
  entry_price: next_open
  exit_price: close_after_horizon
  include_transaction_costs: true
  include_slippage: true

universe:
  min_listing_days: 250
  min_close_price: 10
  min_avg_turnover_20d_twd: 50000000
  exclude_full_delivery: true
  exclude_disposition: true
  exclude_missing_data: true

signal_filter:
  min_probability_up_5d: 0.60
  min_confidence: 0.60
  max_risk_score: 55
  min_risk_adjusted_score: 50
  top_k_per_day: 20
  max_per_industry: 5
  require_no_major_negative_news: true

technical_filter:
  allow_macd_golden_cross: true
  allow_macd_above_zero: true
  reject_macd_bearish_divergence: true
  reject_high_price_volume_divergence: true
  require_volume_confirmation_for_breakout: true

chip_filter:
  require_institutional_net_buy: false
  prefer_foreign_and_trust_sync_buy: true
  min_institutional_net_ratio: 0.03
  reject_three_institutions_sync_sell: true

us_market_filter:
  use_us_market_score: true
  min_us_market_score_for_electronics: 55
  reject_high_vix_spike: true
  reject_us_futures_sharp_reversal_for_high_beta_electronics: true

risk_management:
  stop_loss_type: atr_or_percent
  stop_loss_pct: 0.06
  take_profit_pct: 0.10
  trailing_stop_enabled: true
  max_holding_days: 5
  cooldown_days_after_loss: 3

validation:
  method: walk_forward
  train_window_days: 756
  validation_window_days: 126
  test_window_days: 126
  retrain_frequency: monthly
  min_trades_per_fold: 100
  min_total_trades: 500
  evaluate_by_industry: true
  evaluate_by_market_regime: true
```

The preset intentionally limits signal count, avoids low-quality universe samples, rejects high-risk technical and news conditions, and lowers confidence in electronics signals when US linkage turns sharply weaker.

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

Core feature variables:

- `revenue_yoy`
- `revenue_mom`
- `revenue_yoy_acceleration`
- `revenue_3m_yoy_avg`
- `eps_yoy`
- `eps_qoq`
- `gross_margin_delta_qoq`
- `gross_margin_delta_yoy`
- `operating_margin_delta`
- `debt_ratio`
- `operating_cash_flow_quality`
- `inventory_growth_vs_revenue_growth`
- `accounts_receivable_growth_vs_revenue_growth`
- `industry_growth_score`
- `fundamental_turnaround`
- `quality_growth`

### 2. ChipScore

Inputs:

- Foreign investor net buy/sell
- Investment trust net buy/sell
- Dealer net buy/sell
- Consecutive net-buy days
- Net buy ratio relative to volume
- Margin trading if available
- Institutional synchronization

Core feature variables:

- `foreign_net_ratio`
- `investment_trust_net_ratio`
- `dealer_net_ratio`
- `institutional_net_ratio`
- `foreign_consecutive_buy_days`
- `trust_consecutive_buy_days`
- `dealer_consecutive_buy_days`
- `institutional_sync_buy`
- `institutional_sync_sell`
- `foreign_reversal_to_buy`
- `trust_accumulation_score`
- `dealer_hedge_pressure`
- `tdcc_large_holder_ratio`
- `tdcc_large_holder_ratio_delta`
- `margin_balance_delta`
- `short_interest_delta`
- `borrow_sell_balance_delta`
- `chip_alignment_score`

`chip_alignment_score` captures multi-factor resonance across foreign buying, investment trust buying, dealer not selling, institutional buy ratio, and rising large-holder ratio.

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

Core feature variables:

- trend: `ma5_above_ma20`, `ma20_above_ma60`, `ma20_slope`, `ma60_slope`, `price_above_ma20`, `price_above_ma60`, `breakout_20d_high`, `breakout_60d_high`
- volume and momentum: `volume_ma20_ratio`, `obv_slope`, `rsi14`, `kd_k`, `kd_d`, `atr_pct`, `volatility_20d`
- MACD: `macd_dif`, `macd_dea`, `macd_hist`, `macd_hist_slope_3d`, `macd_golden_cross`, `macd_death_cross`, `macd_above_zero`, `macd_below_zero`, `macd_bullish_divergence`, `macd_bearish_divergence`
- volume-price divergence: `price_up_volume_up`, `price_up_volume_down`, `price_down_volume_down`, `price_down_volume_up`, `new_high_volume_not_confirmed`, `new_high_obv_not_confirmed`, `new_high_macd_not_confirmed`, `new_low_macd_bullish_divergence`, `new_low_obv_bullish_divergence`, `volume_price_score`

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

Core feature variables:

- US returns: `nasdaq_return_1d`, `sox_return_1d`, `sp500_return_1d`, `qqq_return_1d`, `smh_return_1d`, `vix_change_1d`
- key stocks: `tsm_adr_return_1d`, `tsm_adr_premium_discount`, `nvda_return_1d`, `amd_return_1d`, `avgo_return_1d`, `aapl_return_1d`, `mu_return_1d`, `msft_return_1d`, `meta_return_1d`, `googl_return_1d`, `amzn_return_1d`
- macro and futures: `nq_futures_return_preopen`, `es_futures_return_preopen`, `us10y_change`, `dxy_change`, `usd_twd_change`
- derived linkage: `us_tw_beta_20d`, `us_tw_beta_60d`, `beta_to_sox`, `beta_to_nasdaq`, `beta_to_nvda`, `beta_to_tsm_adr`, `us_supply_chain_sensitivity`, `us_market_alignment_score`

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

Core feature variables:

- `news_sentiment_score`
- `news_impact_score`
- `news_confidence`
- `positive_news_count_24h`
- `negative_news_count_24h`
- `news_volume_spike`
- `event_type`
- `event_novelty_score`
- `source_reliability_score`
- `material_news_flag`
- `earnings_news_flag`
- `revenue_news_flag`
- `guidance_news_flag`
- `capex_news_flag`
- `tariff_risk_flag`
- `export_control_risk_flag`
- `lawsuit_risk_flag`
- `default_risk_flag`
- `already_reflected_in_price`
- `supply_chain_linkage_score`
- `fundamental_consistency_score`
- `news_effective_score`

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

Core feature variables:

- `risk_score`
- `volatility_20d`
- `atr_pct`
- `beta_to_taiex`
- `beta_to_sox`
- `max_drawdown_60d`
- `max_drawdown_120d`
- `liquidity_score`
- `gap_risk`
- `limit_up_down_risk`
- `margin_overheat_score`
- `institutional_selling_risk`
- `negative_news_risk`
- `financial_risk`
- `valuation_overheat_score`
- `vix_risk`
- `us_futures_reversal_risk`

Hard risk gates:

- high RiskScore: not eligible for primary signal
- poor liquidity: exclude
- major negative news: exclude
- high-level volume-price divergence plus institutional reversal to sell: exclude
- weak US futures for electronics: downgrade

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

Signal selection variables:

```yaml
signal_selection:
  min_probability_up_1d: 0.56
  min_probability_up_5d: 0.60
  min_probability_up_20d: 0.58
  min_confidence: 0.60
  max_risk_score: 55
  min_bullish_score: 65
  min_risk_adjusted_score: 50
  top_k_per_day: 20
  max_per_industry: 5
  min_expected_return_5d: 0.015
  min_trade_sample_count: 30
  require_positive_chip_score: true
  require_no_major_negative_news: true
```

These thresholds should be tuned with walk-forward backtests. Lower thresholds create more signals but usually reduce win rate; higher thresholds create fewer signals and can improve win rate, but may leave too few samples to be statistically meaningful.

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

### 11. ExplainabilityReport

Inputs:

- signal_id
- generated_at
- data sources and point-in-time availability
- model version
- scoring version
- score calculation details
- factor scores and factor weights
- positive factors
- negative factors
- risk factors
- historical calibration / similar-condition win rate
- selection decision
- market regime
- portfolio risk context
- user-visible text

The report preserves the analysis basis for each research signal. It should be generated before the user sees the signal so the displayed explanation can be audited later.

### 12. ModelMonitoringEngine

Inputs:

- recent 20-day and 60-day win rate
- historical win-rate mean and standard deviation
- recent 20-day average return
- recent 20-day max drawdown
- probability calibration error
- sector win-rate changes
- factor contribution changes
- data latency
- API failure rate
- news parsing error rate

The monitoring engine emits daily health status, alerts, and a signal-strength multiplier. If the recent 20-day win rate is below the historical average by more than two standard deviations, it marks `possible_model_decay` and recommends lowering signal strength while reviewing retraining or recalibration.

### 13. SignalQualityEvaluator

Inputs:

- win rate
- trade count
- average return after costs
- expectancy after costs
- max drawdown
- Profit Factor
- max single loss
- transaction cost and slippage

The evaluator prevents the system from optimizing raw win rate alone. A high-win-rate signal can be rejected if expectancy is negative, drawdown is unacceptable, sample count is too small, or transaction costs remove the edge.

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

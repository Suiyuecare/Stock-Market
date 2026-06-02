# Product Requirements Document

## Product Summary

TW-US Stock Prediction App helps investors review Taiwan stocks after market close and understand how US premarket conditions may affect the next Taiwan trading session.

The product is not a trading bot. It is a decision-support system that explains signals, drivers, and confidence.

## Target Users

- Taiwan stock investors who track US market influence
- Analysts who need a repeatable daily workflow
- Portfolio managers who want signal summaries before the next session

## MVP Goal

Deliver a web dashboard that summarizes:

- Taiwan after-close status
- US premarket linkage status
- Watchlist instruments
- Prediction score and confidence
- Signal drivers such as ADR, US tech sector, FX, futures, and news events

## User Stories

- As an investor, I want to see tomorrow's directional signal for my Taiwan watchlist.
- As an analyst, I want to understand which factors pushed the score up or down.
- As an operator, I want scheduled jobs to run after Taiwan close and before US open.
- As a developer, I want API contracts and database tables ready for real data ingestion.

## MVP Features

### Target Variables

The model should not optimize a single generic up/down label. The MVP supports 1-day, 5-day, and 20-day targets.

Primary model target:

- `y_rel_5d`: future 5-day net return is greater than the benchmark 5-day return plus transaction costs and a minimum excess-return hurdle.

Supporting labels:

- `y_abs_1d`, `y_abs_5d`, `y_abs_20d`
- `y_rel_1d`, `y_rel_5d`, `y_rel_20d`
- `y_tp_sl_1d`, `y_tp_sl_5d`, `y_tp_sl_20d`

This target design avoids rewarding stocks that only rise because the whole market is strong.

### Universe Filters

Before a stock enters training, backtesting, ranking, or signal generation, the system should apply conservative universe filters:

- at least 250 listing days
- close price at least TWD 10
- 20-day average turnover at least TWD 50,000,000
- exclude full-delivery stocks
- exclude disposition stocks
- exclude attention stocks in conservative mode
- exclude low-liquidity stocks
- exclude recent extreme gap moves
- exclude records with missing fundamental data

The goal is to avoid inflated backtests and unstable signals from stocks that are hard to trade, newly listed, special-risk, low-priced, or missing critical data.

### Feature Variables

The MVP should store raw and derived feature variables in the feature store. Early priority groups:

- fundamental variables such as revenue growth, EPS growth, margin deltas, cash-flow quality, and industry growth
- chip/institutional variables such as institutional net ratios, consecutive buy days, TDCC large-holder changes, margin/short changes, and chip alignment

Derived resonance variables such as `fundamental_turnaround`, `quality_growth`, and `chip_alignment_score` help the system find conditions where multiple factors point in the same direction.

Additional feature groups:

- technical variables: MA trend, breakouts, volume ratios, RSI, KD, ATR, volatility, MACD states, and volume-price divergence
- US linkage variables: US index returns, SOX/Nasdaq/ADR/key-stock movement, futures, rates, FX, betas, supply-chain sensitivity, and `us_market_alignment_score`
- news variables: sentiment, impact, confidence, event type, novelty, source reliability, risk flags, supply-chain linkage, and consistency with fundamentals
- risk variables: risk score, volatility, beta, drawdown, liquidity, gap risk, margin overheat, institutional selling, negative news, valuation overheat, VIX, and US futures reversal

Hard risk gates should prevent weak samples from entering the primary research signal list when risk is too high, liquidity is too poor, major negative news is active, high-level volume-price divergence appears with institutional selling, or US futures sharply weaken electronics exposure.

### Signal Selection Thresholds

After probability scoring, the system should decide whether a stock enters the research watchlist using configurable thresholds:

- minimum 1-day, 5-day, and 20-day probability
- minimum confidence
- maximum RiskScore
- minimum BullishScore and RiskAdjustedScore
- top-k limit per day
- maximum count per industry
- minimum expected 5-day return
- minimum historical sample count
- positive chip score requirement
- no-major-negative-news requirement

These thresholds should be selected through walk-forward backtests rather than treated as permanent constants. The system must reject configurations with too few historical trades, because a tiny sample can show 100% win rate without statistical meaning.

### Trade Management Rules

The MVP must define simulated entry and exit rules even before broker integration exists.

- default entry: next-session open
- default exit: fixed horizon or take-profit / stop-loss
- supported horizons: 1, 5, and 20 days
- stop-loss may use ATR or percentage ranges
- take-profit uses configurable percentage ranges
- trailing stop can be enabled
- loss cooldown can temporarily suppress new simulated entries after a losing trade

The app should report fixed-horizon win rate, take-profit/stop-loss win rate, and relative-to-benchmark win rate.

### Cost Model

Backtests and simulated labels must deduct configurable costs before reporting win rate, expectancy, or probability calibration quality.

- buy and sell commission rates are configurable
- transaction tax rate is configurable
- minimum commission fee is configurable
- slippage is modeled by market-cap bucket, with MVP defaults of 3 bps for large cap, 8 bps for mid cap, and 15 bps for small cap
- ETF, stock, day-trading, futures, and broker-specific cost assumptions should be represented as different cost-model configurations

The product should never present gross-return-only performance as the main result, because short-term strategy quality can be materially overstated when trading costs are ignored.

### Validation Design

Model validation must use walk-forward splits with an embargo gap between train, validation, and test periods. The default windows are 756 training days, 126 validation days, 126 test days, monthly retraining, and a 5-day embargo.

Validation must reject or warn on weak results when a fold has fewer than 100 trades or the full validation run has fewer than 500 test trades. Results should be broken down by market regime, industry, and liquidity bucket so the system can detect signals that only work in narrow conditions.

### Strategy Objective Score

The system should compare strategy configurations with a confidence-aware objective score rather than raw win rate. The main win-rate component is the Wilson lower-bound win rate, which penalizes small samples that look too good by chance.

The MVP objective combines lower-bound win rate, average net return, profit factor, calibration quality, stability across validation segments, and a max-drawdown penalty. Raw win rate should remain visible, but it should not be the primary ranking metric.

### Dashboard

- Market status cards
- Watchlist table
- Prediction signal cards
- Signal trend chart
- Job schedule overview

### Backend API

- Health check
- Market summary
- Prediction signal list
- News parser endpoint

### Data Foundation

- Instrument master
- Daily prices
- Market sessions
- News events
- Prediction signals

### Background Jobs

- Taiwan after-close job
- US premarket linkage job
- News/event parsing job placeholder

## Non-Goals

- No mobile app in phase 1
- No full intraday realtime system
- No broker integration
- No direct financial advice language
- No unauthorized market-data scraping

## Success Criteria

- App runs locally through Docker Compose.
- Backend tests pass.
- Dashboard shows signals from API data.
- Data model supports historical prices, news events, and prediction signals.
- Architecture allows legal market-data providers to be plugged in later.

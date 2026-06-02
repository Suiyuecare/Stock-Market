from datetime import date

from app.schemas import BacktestConfig, BacktestObservation, BacktestResult, BacktestTrade


def test_backtest_observation_schema_represents_point_in_time_signal_sample() -> None:
    observation = BacktestObservation(
        trade_date=date(2026, 1, 2),
        stock_id="2330",
        probability=0.68,
        forward_return=0.04,
        holding_days=5,
        sector="semiconductor",
        market_state="bull",
        market_cap_bucket="large",
        liquidity_bucket="high",
        max_favorable_excursion=0.05,
        max_adverse_excursion=-0.01,
    )

    assert observation.stock_id == "2330"
    assert observation.market_state == "bull"
    assert observation.max_favorable_excursion == 0.05


def test_backtest_result_schema_contains_required_research_metrics() -> None:
    trade = BacktestTrade(
        trade_date=date(2026, 1, 2),
        stock_id="2330",
        holding_days=5,
        gross_return=0.04,
        net_return=0.038,
        exit_reason="take_profit",
        sector="semiconductor",
        market_state="bull",
    )
    result = BacktestResult(
        win_rate=1.0,
        trade_count=1,
        average_return=0.038,
        median_return=0.038,
        expectancy=0.038,
        max_drawdown=0.0,
        profit_factor=0.038,
        sharpe_ratio=0.0,
        sortino_ratio=0.0,
        max_single_loss=0.0,
        max_consecutive_losses=0,
        average_holding_days=5.0,
        turnover=1.0,
        win_rate_by_sector={"semiconductor": 1.0},
        win_rate_by_market_state={"bull": 1.0},
        trades=[trade],
    )

    assert result.trade_count == 1
    assert result.trades[0].exit_reason == "take_profit"


def test_backtest_config_supports_costs_thresholds_and_segments() -> None:
    config = BacktestConfig(
        holding_days=20,
        entry_probability_threshold=0.7,
        transaction_cost=0.001425,
        slippage=0.001,
        take_profit=0.08,
        stop_loss=0.04,
        sector="semiconductor",
        market_state="high_volatility",
        market_cap_bucket="large",
        liquidity_bucket="high",
    )

    assert config.holding_days == 20
    assert config.entry_probability_threshold == 0.7
    assert config.market_state == "high_volatility"

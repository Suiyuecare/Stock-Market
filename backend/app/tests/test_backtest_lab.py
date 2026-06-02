from datetime import date, timedelta

from app.schemas import BacktestConfig, BacktestObservation
from app.services.backtest_lab import BacktestLab


def _observations() -> list[BacktestObservation]:
    return [
        BacktestObservation(
            trade_date=date(2026, 1, 2),
            stock_id="2330",
            probability=0.70,
            forward_return=0.05,
            holding_days=5,
            sector="semiconductor",
            market_state="bull",
            market_cap_bucket="large",
            liquidity_bucket="high",
            max_favorable_excursion=0.06,
            max_adverse_excursion=-0.01,
        ),
        BacktestObservation(
            trade_date=date(2026, 1, 3),
            stock_id="2454",
            probability=0.65,
            forward_return=-0.02,
            holding_days=5,
            sector="semiconductor",
            market_state="bear",
            market_cap_bucket="large",
            liquidity_bucket="high",
            max_favorable_excursion=0.01,
            max_adverse_excursion=-0.03,
        ),
        BacktestObservation(
            trade_date=date(2026, 1, 4),
            stock_id="2382",
            probability=0.80,
            forward_return=0.03,
            holding_days=5,
            sector="ai_server",
            market_state="bull",
            market_cap_bucket="large",
            liquidity_bucket="medium",
            max_favorable_excursion=0.04,
            max_adverse_excursion=-0.01,
        ),
        BacktestObservation(
            trade_date=date(2026, 1, 5),
            stock_id="1301",
            probability=0.59,
            forward_return=0.04,
            holding_days=5,
            sector="domestic_demand",
            market_state="bull",
            market_cap_bucket="large",
            liquidity_bucket="medium",
        ),
        BacktestObservation(
            trade_date=date(2026, 1, 6),
            stock_id="2912",
            probability=0.70,
            forward_return=-0.04,
            holding_days=5,
            sector="domestic_demand",
            market_state="bear",
            market_cap_bucket="mid",
            liquidity_bucket="medium",
            max_favorable_excursion=0.01,
            max_adverse_excursion=-0.05,
        ),
    ]


def test_backtest_lab_calculates_core_metrics_after_costs() -> None:
    result = BacktestLab().run(_observations(), BacktestConfig())

    assert result.trade_count == 4
    assert result.win_rate == 0.5
    assert result.average_return == 0.003
    assert result.median_return == 0.003
    assert result.expectancy == 0.003
    assert result.profit_factor == 1.1875
    assert result.max_single_loss == -0.042
    assert result.max_consecutive_losses == 1
    assert result.average_holding_days == 5.0
    assert result.turnover == 1.0
    assert result.win_rate_by_sector["semiconductor"] == 0.5
    assert result.win_rate_by_sector["ai_server"] == 1.0
    assert result.win_rate_by_market_state["bear"] == 0.0


def test_backtest_lab_filters_by_signal_and_segment_configuration() -> None:
    result = BacktestLab().run(
        _observations(),
        BacktestConfig(
            entry_probability_threshold=0.75,
            sector="ai_server",
            market_state="bull",
            liquidity_bucket="medium",
        ),
    )

    assert result.trade_count == 1
    assert result.trades[0].stock_id == "2382"
    assert result.trades[0].net_return == 0.028


def test_backtest_lab_supports_take_profit_and_stop_loss_exits() -> None:
    result = BacktestLab().run(
        _observations(),
        BacktestConfig(take_profit=0.04, stop_loss=0.025),
    )

    exits = {trade.stock_id: trade.exit_reason for trade in result.trades}
    returns = {trade.stock_id: trade.net_return for trade in result.trades}

    assert exits["2330"] == "take_profit"
    assert returns["2330"] == 0.038
    assert exits["2454"] == "stop_loss"
    assert returns["2454"] == -0.027


def test_backtest_lab_uses_chronological_time_series_windows() -> None:
    observations = [
        BacktestObservation(
            trade_date=date(2026, 1, 1) + timedelta(days=index),
            stock_id="2330",
            probability=0.70,
            forward_return=0.01,
            holding_days=5,
        )
        for index in range(8)
    ]

    windows = BacktestLab().time_series_split(observations, n_splits=3)

    assert len(windows) == 3
    assert windows[0].train_start == date(2026, 1, 1)
    assert windows[0].train_end == date(2026, 1, 2)
    assert windows[0].test_start == date(2026, 1, 3)
    assert windows[0].test_end == date(2026, 1, 4)
    assert all(window.train_end < window.test_start for window in windows)

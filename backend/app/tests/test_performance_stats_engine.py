from datetime import date
from decimal import Decimal

from app.schemas import BacktestResult, BacktestTrade, PerformanceStatsInput
from app.services.performance_stats_engine import PerformanceStatsEngine


def _result() -> BacktestResult:
    trades = [
        BacktestTrade(
            trade_date=date(2026, 1, 2),
            stock_id="2330",
            holding_days=5,
            gross_return=0.05,
            net_return=0.045,
            exit_reason="horizon",
            sector="semiconductor",
            market_state="bull",
            liquidity_bucket="high",
        ),
        BacktestTrade(
            trade_date=date(2026, 1, 3),
            stock_id="2454",
            holding_days=5,
            gross_return=-0.02,
            net_return=-0.025,
            exit_reason="horizon",
            sector="semiconductor",
            market_state="bull",
            liquidity_bucket="high",
        ),
        BacktestTrade(
            trade_date=date(2026, 1, 4),
            stock_id="2382",
            holding_days=5,
            gross_return=0.03,
            net_return=0.025,
            exit_reason="horizon",
            sector="ai_server",
            market_state="bull",
            liquidity_bucket="medium",
        ),
    ]
    return BacktestResult(
        win_rate=2 / 3,
        trade_count=3,
        average_return=0.015,
        median_return=0.025,
        expectancy=0.015,
        max_drawdown=-0.025,
        profit_factor=2.8,
        sharpe_ratio=1.0,
        sortino_ratio=1.1,
        max_single_loss=-0.025,
        max_consecutive_losses=1,
        average_holding_days=5,
        turnover=1,
        win_rate_by_sector={"semiconductor": 0.5, "ai_server": 1.0},
        win_rate_by_market_state={"bull": 2 / 3},
        trades=trades,
    )


def test_performance_stats_engine_aggregates_backtest_trades() -> None:
    result = PerformanceStatsEngine().build_stats(
        PerformanceStatsInput(
            model_version="model-v1",
            strategy_version="mvp-default-v1",
            horizon_days=5,
            market_regime="bull",
            industry="semiconductor",
            probability_bucket="0.60-0.70",
            risk_bucket="30-45",
            backtest_result=_result(),
            calibration_error=Decimal("0.04"),
        )
    )

    stats = result.stats
    assert stats.trade_count == 3
    assert stats.win_rate == Decimal("0.66666667")
    assert stats.win_rate_lower_bound < stats.win_rate
    assert stats.avg_net_return == Decimal("0.015")
    assert stats.median_net_return == Decimal("0.025")
    assert stats.profit_factor == Decimal("2.8")
    assert stats.max_drawdown < 0
    assert stats.calibration_error == Decimal("0.04")

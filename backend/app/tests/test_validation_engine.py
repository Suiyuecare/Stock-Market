from datetime import date, timedelta

from app.schemas import BacktestConfig, BacktestObservation, ValidationConfig
from app.services.validation_engine import ValidationEngine


def _observations(days: int = 40) -> list[BacktestObservation]:
    rows: list[BacktestObservation] = []
    for index in range(days):
        rows.append(
            BacktestObservation(
                trade_date=date(2026, 1, 1) + timedelta(days=index),
                stock_id=f"23{index:02d}",
                probability=0.70,
                forward_return=0.02 if index % 2 == 0 else -0.01,
                holding_days=5,
                sector="semiconductor" if index % 3 else "ai_server",
                market_state="bull" if index % 2 == 0 else "bear",
                liquidity_bucket="high" if index % 4 else "medium",
            )
        )
    return rows


def test_validation_engine_builds_walk_forward_folds_with_embargo() -> None:
    config = ValidationConfig(
        train_window_days=10,
        validation_window_days=5,
        test_window_days=5,
        embargo_days=2,
        retrain_frequency="weekly",
        min_trades_per_fold=1,
        min_total_trades=2,
        backtest_config=BacktestConfig(transaction_cost=0, slippage=0),
    )

    result = ValidationEngine().validate(_observations(), config)

    assert result.fold_count == 4
    first = result.folds[0]
    assert first.train_start == date(2026, 1, 1)
    assert first.train_end == date(2026, 1, 10)
    assert first.validation_start == date(2026, 1, 13)
    assert first.test_start == date(2026, 1, 20)
    assert (first.validation_start - first.train_end).days == config.embargo_days + 1
    assert (first.test_start - first.validation_end).days == config.embargo_days + 1


def test_validation_engine_checks_fold_and_total_trade_thresholds() -> None:
    config = ValidationConfig(
        train_window_days=10,
        validation_window_days=5,
        test_window_days=5,
        embargo_days=2,
        retrain_frequency="monthly",
        min_trades_per_fold=10,
        min_total_trades=100,
    )

    result = ValidationEngine().validate(_observations(), config)

    assert result.passed_all_folds is False
    assert result.passed_min_total_trades is False
    assert result.warnings


def test_validation_engine_reports_segment_win_rates_for_test_windows() -> None:
    config = ValidationConfig(
        train_window_days=10,
        validation_window_days=5,
        test_window_days=5,
        embargo_days=1,
        retrain_frequency="weekly",
        min_trades_per_fold=1,
        min_total_trades=1,
        backtest_config=BacktestConfig(transaction_cost=0, slippage=0),
    )

    result = ValidationEngine().validate(_observations(), config)

    assert "bull" in result.win_rate_by_market_regime
    assert "semiconductor" in result.win_rate_by_industry
    assert "high" in result.win_rate_by_liquidity_bucket


def test_validation_engine_can_disable_segment_evaluation() -> None:
    config = ValidationConfig(
        train_window_days=10,
        validation_window_days=5,
        test_window_days=5,
        embargo_days=1,
        evaluate_by_market_regime=False,
        evaluate_by_industry=False,
        evaluate_by_liquidity_bucket=False,
    )

    result = ValidationEngine().validate(_observations(), config)

    assert result.win_rate_by_market_regime == {}
    assert result.win_rate_by_industry == {}
    assert result.win_rate_by_liquidity_bucket == {}

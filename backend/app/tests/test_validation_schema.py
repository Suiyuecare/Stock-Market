from datetime import date

from app.schemas import BacktestResult, ValidationConfig, ValidationFold, ValidationResult


def _empty_backtest_result() -> BacktestResult:
    return BacktestResult(
        win_rate=0,
        trade_count=0,
        average_return=0,
        median_return=0,
        expectancy=0,
        max_drawdown=0,
        profit_factor=0,
        sharpe_ratio=0,
        sortino_ratio=0,
        max_single_loss=0,
        max_consecutive_losses=0,
        average_holding_days=0,
        turnover=0,
        win_rate_by_sector={},
        win_rate_by_market_state={},
        trades=[],
    )


def test_validation_config_defaults_match_mvp_validation_variables() -> None:
    config = ValidationConfig()

    assert config.split_method == "walk_forward"
    assert config.train_window_days == 756
    assert config.validation_window_days == 126
    assert config.test_window_days == 126
    assert config.retrain_frequency == "monthly"
    assert config.embargo_days == 5
    assert config.min_trades_per_fold == 100
    assert config.min_total_trades == 500


def test_validation_result_schema_contains_fold_quality_gates() -> None:
    fold = ValidationFold(
        fold_index=0,
        train_start=date(2026, 1, 1),
        train_end=date(2026, 1, 10),
        validation_start=date(2026, 1, 16),
        validation_end=date(2026, 1, 20),
        test_start=date(2026, 1, 26),
        test_end=date(2026, 1, 30),
        train_sample_count=1000,
        validation_trade_count=120,
        test_trade_count=130,
        passed_min_trades=True,
        validation_result=_empty_backtest_result(),
        test_result=_empty_backtest_result(),
    )
    result = ValidationResult(
        split_method="walk_forward",
        retrain_frequency="monthly",
        embargo_days=5,
        fold_count=1,
        total_test_trades=130,
        passed_min_total_trades=False,
        passed_all_folds=False,
        folds=[fold],
        win_rate_by_market_regime={"bull": 0.6},
        win_rate_by_industry={"semiconductor": 0.55},
        win_rate_by_liquidity_bucket={"high": 0.58},
        warnings=["Total test trades are fewer than min_total_trades."],
    )

    assert result.folds[0].passed_min_trades is True
    assert result.win_rate_by_industry["semiconductor"] == 0.55

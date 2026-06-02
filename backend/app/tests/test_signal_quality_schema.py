from app.schemas import SignalQualityInput, SignalQualityResult, SignalQualityThresholds


def test_signal_quality_input_schema_tracks_non_win_rate_metrics() -> None:
    metrics = SignalQualityInput(
        win_rate=0.62,
        trade_count=80,
        average_return=0.018,
        expectancy=0.014,
        max_drawdown=-0.05,
        profit_factor=1.8,
        max_single_loss=-0.04,
        transaction_cost=0.001,
        slippage=0.001,
    )

    assert metrics.expectancy == 0.014
    assert metrics.transaction_cost == 0.001


def test_signal_quality_result_schema_returns_quality_decision() -> None:
    result = SignalQualityResult(
        passed=True,
        quality_grade="acceptable",
        quality_score=78.5,
        reasons=["Expectancy is positive after costs."],
        warnings=[],
        metrics={"win_rate": 0.62},
    )

    assert result.passed is True
    assert result.quality_grade == "acceptable"


def test_signal_quality_threshold_schema_can_tune_objective() -> None:
    thresholds = SignalQualityThresholds(
        minimum_win_rate=0.6,
        minimum_expectancy=0.005,
        minimum_trade_count=50,
        maximum_drawdown=0.08,
    )

    assert thresholds.minimum_win_rate == 0.6
    assert thresholds.maximum_drawdown == 0.08

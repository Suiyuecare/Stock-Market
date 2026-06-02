from app.schemas import SignalQualityInput, SignalQualityThresholds
from app.services.signal_quality_evaluator import SignalQualityEvaluator


def test_signal_quality_accepts_balanced_positive_expectancy_signal() -> None:
    result = SignalQualityEvaluator().evaluate(
        SignalQualityInput(
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
    )

    assert result.passed is True
    assert result.quality_grade in {"acceptable", "excellent"}
    assert "Expectancy is positive after costs." in result.reasons


def test_signal_quality_rejects_high_win_rate_negative_expectancy() -> None:
    result = SignalQualityEvaluator().evaluate(
        SignalQualityInput(
            win_rate=0.90,
            trade_count=100,
            average_return=-0.006,
            expectancy=-0.006,
            max_drawdown=-0.22,
            profit_factor=0.75,
            max_single_loss=-0.15,
        )
    )

    assert result.passed is False
    assert result.quality_grade == "rejected"
    assert "Expectancy is not positive after costs." in result.warnings
    assert "Max drawdown exceeds the acceptable threshold." in result.warnings


def test_signal_quality_rejects_small_sample_even_when_returns_are_good() -> None:
    result = SignalQualityEvaluator().evaluate(
        SignalQualityInput(
            win_rate=0.7,
            trade_count=8,
            average_return=0.03,
            expectancy=0.025,
            max_drawdown=-0.03,
            profit_factor=2.0,
            max_single_loss=-0.02,
        )
    )

    assert result.passed is False
    assert "Sample count is too small to trust the signal." in result.warnings


def test_signal_quality_thresholds_can_be_tuned() -> None:
    result = SignalQualityEvaluator().evaluate(
        SignalQualityInput(
            win_rate=0.58,
            trade_count=40,
            average_return=0.01,
            expectancy=0.008,
            max_drawdown=-0.08,
            profit_factor=1.2,
            max_single_loss=-0.04,
        ),
        SignalQualityThresholds(minimum_win_rate=0.6),
    )

    assert result.passed is False
    assert "Win rate is below the minimum threshold." in result.warnings

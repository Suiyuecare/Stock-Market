from datetime import date

from app.schemas import SignalAntiPatternInput
from app.services.anti_pattern_guard import SignalAntiPatternGuard


def _signal(**overrides: object) -> SignalAntiPatternInput:
    values = {
        "stock_id": "2330",
        "signal_date": date(2026, 6, 5),
        "probability_up": 0.66,
        "risk_score": 40,
        "trade_sample_count": 180,
        "factor_alignment_count": 5,
        "net_expectancy_after_costs": 0.018,
        "yearly_stability_score": 0.72,
        "market_regime_stability_score": 0.68,
        "has_macd_golden_cross": True,
        "has_foreign_net_buy": True,
        "has_positive_news": True,
        "has_technical_breakout": True,
    }
    values.update(overrides)
    return SignalAntiPatternInput(**values)


def test_anti_pattern_guard_accepts_multi_factor_stable_signal() -> None:
    result = SignalAntiPatternGuard().evaluate(_signal())

    assert result.passed is True
    assert result.anti_patterns == []
    assert "Multiple independent factors are aligned." in result.quality_gates_passed


def test_anti_pattern_guard_rejects_single_macd_signal() -> None:
    result = SignalAntiPatternGuard().evaluate(
        _signal(
            factor_alignment_count=1,
            has_macd_golden_cross=True,
            has_foreign_net_buy=False,
            has_positive_news=False,
            has_technical_breakout=False,
        )
    )

    assert result.passed is False
    assert "single_macd_golden_cross" in result.anti_patterns
    assert "insufficient_multi_factor_alignment" in result.quality_gates_failed


def test_anti_pattern_guard_rejects_single_nvda_or_news_narrative() -> None:
    nvda = SignalAntiPatternGuard().evaluate(
        _signal(
            factor_alignment_count=1,
            has_macd_golden_cross=False,
            has_foreign_net_buy=False,
            has_nvda_spike=True,
            has_positive_news=False,
            has_technical_breakout=False,
        )
    )
    news = SignalAntiPatternGuard().evaluate(
        _signal(
            factor_alignment_count=1,
            has_macd_golden_cross=False,
            has_foreign_net_buy=False,
            has_positive_news=True,
            has_technical_breakout=False,
        )
    )

    assert "single_nvda_spike" in nvda.anti_patterns
    assert "single_positive_news" in news.anti_patterns


def test_anti_pattern_guard_rejects_high_probability_without_quality_gates() -> None:
    result = SignalAntiPatternGuard().evaluate(
        _signal(
            probability_up=0.78,
            risk_score=70,
            trade_sample_count=20,
            factor_alignment_count=1,
            net_expectancy_after_costs=-0.002,
            yearly_stability_score=0.4,
            market_regime_stability_score=0.45,
            has_macd_golden_cross=False,
            has_foreign_net_buy=False,
            has_positive_news=False,
            has_technical_breakout=False,
        )
    )

    assert result.passed is False
    assert "single_high_model_probability" in result.anti_patterns
    assert "risk_score_above_threshold" in result.quality_gates_failed
    assert "expectancy_not_positive_after_costs" in result.quality_gates_failed


def test_anti_pattern_guard_rejects_poor_year_or_market_regime_stability() -> None:
    result = SignalAntiPatternGuard().evaluate(
        _signal(yearly_stability_score=0.5, market_regime_stability_score=0.42)
    )

    assert result.passed is False
    assert "yearly_stability_below_threshold" in result.quality_gates_failed
    assert "market_regime_stability_below_threshold" in result.quality_gates_failed

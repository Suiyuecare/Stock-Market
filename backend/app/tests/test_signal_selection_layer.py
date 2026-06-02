from datetime import date

from app.schemas import SignalSelectionConfig, SignalSelectionInput
from app.services.signal_selection_layer import SignalSelectionLayer


def _signal(**overrides: object) -> SignalSelectionInput:
    values = {
        "stock_id": "2330",
        "signal_date": date(2026, 6, 2),
        "probability_up": 0.72,
        "risk_score": 45.0,
        "confidence": 72.0,
        "calibration_sample_count": 80,
        "liquidity_score": 70.0,
        "chip_score": 62.0,
        "us_market_score": 68.0,
    }
    values.update(overrides)
    return SignalSelectionInput(**values)


def test_signal_selection_accepts_high_quality_signal() -> None:
    result = SignalSelectionLayer().evaluate(_signal())

    assert result.selected is True
    assert result.decision == "primary_watchlist"
    assert result.priority == 3
    assert result.risk_flags == []


def test_signal_selection_excludes_low_probability_signal() -> None:
    result = SignalSelectionLayer().evaluate(_signal(probability_up=0.55))

    assert result.selected is False
    assert result.decision == "excluded"
    assert "Probability is below the signal threshold." in result.reasons


def test_signal_selection_excludes_illiquid_signal() -> None:
    result = SignalSelectionLayer().evaluate(_signal(liquidity_score=30.0))

    assert result.selected is False
    assert result.decision == "excluded"
    assert "insufficient_liquidity" in result.risk_flags


def test_signal_selection_excludes_major_negative_event() -> None:
    result = SignalSelectionLayer().evaluate(_signal(has_major_negative_event=True))

    assert result.selected is False
    assert result.decision == "excluded"
    assert "major_negative_event" in result.risk_flags


def test_signal_selection_routes_high_risk_probability_to_high_risk_watchlist() -> None:
    result = SignalSelectionLayer().evaluate(_signal(risk_score=82.0))

    assert result.selected is True
    assert result.decision == "high_risk_watchlist"
    assert "high_risk_score" in result.risk_flags


def test_signal_selection_marks_low_sample_count_as_low_confidence() -> None:
    result = SignalSelectionLayer().evaluate(_signal(calibration_sample_count=8))

    assert result.selected is True
    assert result.decision == "low_confidence_watchlist"
    assert "insufficient_sample_count" in result.risk_flags


def test_signal_selection_downgrades_us_positive_but_chip_weak_signal() -> None:
    result = SignalSelectionLayer().evaluate(_signal(us_market_score=78.0, chip_score=35.0))

    assert result.selected is True
    assert result.decision == "low_confidence_watchlist"
    assert "us_positive_chip_weak" in result.risk_flags


def test_signal_selection_routes_earnings_window_to_high_risk_watchlist() -> None:
    result = SignalSelectionLayer().evaluate(
        _signal(
            is_high_risk_event_window=True,
            event_window_reason="Earnings call window requires higher caution.",
        )
    )

    assert result.decision == "high_risk_watchlist"
    assert "high_risk_event_window" in result.risk_flags
    assert result.warnings[0] == "Earnings call window requires higher caution."


def test_signal_selection_config_can_raise_selection_bar() -> None:
    result = SignalSelectionLayer().evaluate(
        _signal(probability_up=0.72),
        SignalSelectionConfig(minimum_probability=0.75),
    )

    assert result.selected is False
    assert result.decision == "excluded"

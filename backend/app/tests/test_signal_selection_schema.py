from datetime import date

from app.schemas import SignalSelectionConfig, SignalSelectionInput, SignalSelectionResult


def test_signal_selection_input_schema_tracks_filter_features() -> None:
    signal = SignalSelectionInput(
        stock_id="2330",
        signal_date=date(2026, 6, 2),
        probability_up=0.72,
        risk_score=45,
        confidence=72,
        calibration_sample_count=80,
        liquidity_score=70,
        chip_score=62,
        us_market_score=68,
        is_high_risk_event_window=True,
        event_window_reason="Ex-dividend window.",
    )

    assert signal.stock_id == "2330"
    assert signal.event_window_reason == "Ex-dividend window."


def test_signal_selection_result_schema_represents_decision() -> None:
    result = SignalSelectionResult(
        stock_id="2330",
        signal_date=date(2026, 6, 2),
        selected=True,
        decision="primary_watchlist",
        priority=3,
        reasons=["Probability passed the signal threshold."],
        warnings=[],
        risk_flags=[],
    )

    assert result.selected is True
    assert result.decision == "primary_watchlist"


def test_signal_selection_config_schema_can_tune_thresholds() -> None:
    config = SignalSelectionConfig(
        minimum_probability=0.7,
        high_risk_threshold=70,
        minimum_confidence=65,
        minimum_sample_count=50,
        minimum_liquidity_score=55,
    )

    assert config.minimum_probability == 0.7
    assert config.minimum_sample_count == 50

from datetime import date

from app.schemas import (
    SignalSelectionBatchResult,
    SignalSelectionCandidate,
    SignalSelectionConfig,
    SignalSelectionInput,
    SignalSelectionResult,
    SignalSelectionThresholds,
)


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


def test_signal_selection_threshold_schema_tracks_advanced_variables() -> None:
    thresholds = SignalSelectionThresholds()

    assert thresholds.min_probability_up_1d == 0.56
    assert thresholds.min_probability_up_5d == 0.60
    assert thresholds.max_risk_score == 55
    assert thresholds.top_k_per_day == 20
    assert thresholds.max_per_industry == 5
    assert thresholds.min_trade_sample_count == 30


def test_signal_selection_candidate_schema_tracks_scores_and_samples() -> None:
    candidate = SignalSelectionCandidate(
        stock_id="2330",
        signal_date=date(2026, 6, 2),
        industry="semiconductor",
        probability_up_1d=0.58,
        probability_up_5d=0.64,
        probability_up_20d=0.6,
        confidence=0.72,
        risk_score=42,
        bullish_score=72,
        risk_adjusted_score=58,
        expected_return_5d=0.025,
        chip_score=62,
        trade_sample_count=80,
    )

    assert candidate.industry == "semiconductor"
    assert candidate.trade_sample_count == 80


def test_signal_selection_batch_result_schema_keeps_selected_and_rejected() -> None:
    result = SignalSelectionBatchResult(
        selected=[],
        rejected=[
            SignalSelectionResult(
                stock_id="2330",
                signal_date=date(2026, 6, 2),
                selected=False,
                decision="excluded",
                priority=0,
                reasons=[],
                warnings=["Signal failed selection thresholds."],
                risk_flags=["sample_count_below_threshold"],
            )
        ],
        thresholds=SignalSelectionThresholds(),
    )

    assert result.rejected[0].risk_flags == ["sample_count_below_threshold"]

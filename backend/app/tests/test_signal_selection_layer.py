from datetime import date

from app.schemas import SignalSelectionCandidate, SignalSelectionConfig, SignalSelectionInput, SignalSelectionThresholds
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


def _candidate(stock_id: str, industry: str = "semiconductor", **overrides: object) -> SignalSelectionCandidate:
    values = {
        "stock_id": stock_id,
        "signal_date": date(2026, 6, 2),
        "industry": industry,
        "probability_up_1d": 0.58,
        "probability_up_5d": 0.64,
        "probability_up_20d": 0.60,
        "confidence": 0.72,
        "risk_score": 42.0,
        "bullish_score": 72.0,
        "risk_adjusted_score": 58.0,
        "expected_return_5d": 0.025,
        "chip_score": 62.0,
        "has_major_negative_news": False,
        "trade_sample_count": 80,
    }
    values.update(overrides)
    return SignalSelectionCandidate(**values)


def test_signal_selection_batch_accepts_candidate_passing_all_thresholds() -> None:
    result = SignalSelectionLayer().select_batch([_candidate("2330")])

    assert [candidate.stock_id for candidate in result.selected] == ["2330"]
    assert result.rejected == []


def test_signal_selection_batch_rejects_probability_risk_chip_news_and_sample_failures() -> None:
    result = SignalSelectionLayer().select_batch(
        [
            _candidate("low_prob", probability_up_5d=0.55),
            _candidate("high_risk", risk_score=80),
            _candidate("weak_chip", chip_score=45),
            _candidate("bad_news", has_major_negative_news=True),
            _candidate("tiny_sample", trade_sample_count=5),
        ]
    )
    flags = {flag for rejected in result.rejected for flag in rejected.risk_flags}

    assert result.selected == []
    assert "probability_up_5d_below_threshold" in flags
    assert "risk_score_above_threshold" in flags
    assert "chip_score_not_positive" in flags
    assert "major_negative_news" in flags
    assert "sample_count_below_threshold" in flags


def test_signal_selection_batch_applies_top_k_and_industry_limits() -> None:
    candidates = [
        _candidate("ai1", "ai_server", risk_adjusted_score=90),
        _candidate("ai2", "ai_server", risk_adjusted_score=88),
        _candidate("ai3", "ai_server", risk_adjusted_score=86),
        _candidate("semi1", "semiconductor", risk_adjusted_score=84),
    ]
    result = SignalSelectionLayer().select_batch(
        candidates,
        SignalSelectionThresholds(top_k_per_day=3, max_per_industry=2),
    )

    assert [candidate.stock_id for candidate in result.selected] == ["ai1", "ai2", "semi1"]
    assert any("industry_limit" in rejected.risk_flags for rejected in result.rejected)


def test_signal_selection_batch_higher_thresholds_reduce_signal_count() -> None:
    candidates = [_candidate("2330"), _candidate("2454", probability_up_5d=0.61, risk_adjusted_score=51)]

    loose = SignalSelectionLayer().select_batch(candidates, SignalSelectionThresholds())
    strict = SignalSelectionLayer().select_batch(
        candidates,
        SignalSelectionThresholds(min_probability_up_5d=0.65, min_risk_adjusted_score=60),
    )

    assert len(loose.selected) == 2
    assert len(strict.selected) == 0

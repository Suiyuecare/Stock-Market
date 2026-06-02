from datetime import date

from app.schemas import BullishConfluenceConfig, BullishConfluenceInput
from app.services.confluence_signal import BullishConfluenceEvaluator


def _signal(**overrides: object) -> BullishConfluenceInput:
    values = {
        "stock_id": "2330",
        "signal_date": date(2026, 6, 5),
        "fundamental_score": 68,
        "chip_score": 72,
        "technical_score": 74,
        "us_market_score": 62,
        "news_score": 58,
        "risk_score": 42,
        "liquidity_score": 70,
    }
    values.update(overrides)
    return BullishConfluenceInput(**values)


def test_bullish_confluence_accepts_multi_factor_resonance() -> None:
    result = BullishConfluenceEvaluator().evaluate(_signal())

    assert result.passed is True
    assert result.confluence_score == 100
    assert "FundamentalScore shows improvement." in result.passed_conditions
    assert result.failed_conditions == []
    assert result.rejection_reasons == []


def test_bullish_confluence_rejects_low_core_scores() -> None:
    result = BullishConfluenceEvaluator().evaluate(
        _signal(
            fundamental_score=55,
            chip_score=60,
            technical_score=61,
        )
    )

    assert result.passed is False
    assert "fundamental_score_below_confluence_threshold" in result.failed_conditions
    assert "chip_score_below_confluence_threshold" in result.failed_conditions
    assert "technical_score_below_confluence_threshold" in result.failed_conditions


def test_bullish_confluence_rejects_macd_and_volume_price_risk() -> None:
    result = BullishConfluenceEvaluator().evaluate(
        _signal(
            macd_death_cross=True,
            high_price_volume_divergence=True,
        )
    )

    assert result.passed is False
    assert "MACD death cross is active." in result.rejection_reasons
    assert "High-level price-volume divergence is active." in result.rejection_reasons
    assert "macd_death_cross" in result.risk_flags
    assert "high_price_volume_divergence" in result.risk_flags


def test_bullish_confluence_rejects_institutional_sync_sell_and_bad_news() -> None:
    result = BullishConfluenceEvaluator().evaluate(
        _signal(
            three_institutions_sync_sell=True,
            has_major_negative_news=True,
        )
    )

    assert result.passed is False
    assert "three_institutions_sync_sell" in result.risk_flags
    assert "major_negative_news" in result.risk_flags


def test_bullish_confluence_thresholds_are_configurable() -> None:
    result = BullishConfluenceEvaluator().evaluate(
        _signal(chip_score=62),
        BullishConfluenceConfig(min_chip_score=60),
    )

    assert result.passed is True

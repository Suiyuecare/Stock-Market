from app.services.indicators import (
    analyze_kd,
    analyze_moving_averages,
    analyze_obv,
    analyze_rsi,
    build_technical_indicators,
)
from app.services.indicators.macd import analyze_macd
from app.services.indicators.volume_price_divergence import analyze_volume_price_divergence


def test_moving_average_analysis_returns_explainable_signal() -> None:
    analysis = analyze_moving_averages([float(value) for value in range(1, 81)])

    assert analysis["trend"] == "uptrend"
    assert "close above MA20" in analysis["positive_factors"]
    assert analysis["confidence"] == 1.0


def test_rsi_analysis_returns_state_and_factors() -> None:
    analysis = analyze_rsi([10, 11, 12, 11, 13, 14, 13, 15, 16, 15, 17, 18, 19, 18, 20], 14)

    assert analysis["rsi"] is not None
    assert analysis["state"] in {"constructive", "strong_momentum", "overextended", "soft_momentum", "weak"}
    assert set(analysis.keys()) >= {"positive_factors", "negative_factors", "risk_factors", "confidence"}


def test_kd_analysis_returns_state_and_factors() -> None:
    closes = [float(value) for value in range(1, 20)]
    highs = [value + 1 for value in closes]
    lows = [value - 1 for value in closes]
    analysis = analyze_kd(highs, lows, closes)

    assert analysis["k"] is not None
    assert analysis["d"] is not None
    assert analysis["state"] in {"positive_momentum", "negative_momentum", "neutral", "overbought"}
    assert set(analysis.keys()) >= {"positive_factors", "negative_factors", "risk_factors", "confidence"}


def test_obv_analysis_returns_accumulation_or_distribution_signal() -> None:
    analysis = analyze_obv([10, 11, 12, 13, 14, 15], [100, 120, 140, 160, 180, 220])

    assert analysis["obv"] is not None
    assert analysis["state"] == "accumulation_confirming_price"
    assert analysis["positive_factors"]


def test_macd_and_volume_price_analysis_are_explainable() -> None:
    closes = [float(value) for value in range(1, 80)]
    volumes = [1000 + value * 10 for value in range(1, 80)]
    macd = analyze_macd(closes)
    volume_price = analyze_volume_price_divergence(closes, volumes)

    assert set(macd.keys()) >= {"dif", "dea", "macd_hist", "golden_cross", "death_cross"}
    assert set(volume_price.keys()) >= {"state", "states", "score_signal", "bearish_divergence", "bullish_divergence"}


def test_build_technical_indicators_includes_explainable_signals() -> None:
    closes = [float(value) for value in range(1, 81)]
    highs = [value + 2 for value in closes]
    lows = [value - 1 for value in closes]
    volumes = [1000 + value * 10 for value in range(1, 81)]
    indicators = build_technical_indicators(highs, lows, closes, volumes)

    assert set(indicators["signals"].keys()) == {
        "moving_average",
        "rsi",
        "kd",
        "obv",
        "macd",
        "volume_price_divergence",
    }

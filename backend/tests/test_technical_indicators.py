from app.services.technical_indicators import (
    build_technical_indicators,
    moving_average,
    obv,
    rsi,
    volume_price_divergence,
)


def test_moving_average() -> None:
    assert moving_average([1, 2, 3, 4, 5], 3) == 4
    assert moving_average([1, 2], 3) is None


def test_rsi_bounds() -> None:
    value = rsi([10, 11, 12, 11, 13, 14, 13, 15, 16, 15, 17, 18, 19, 18, 20], 14)
    assert value is not None
    assert 0 <= value <= 100


def test_obv_direction() -> None:
    assert obv([10, 11, 10], [100, 200, 300]) == -100


def test_volume_price_divergence_returns_value() -> None:
    value = volume_price_divergence([10, 11, 12, 13, 14, 15], [100, 120, 140, 160, 180, 240], 5)
    assert value is not None


def test_build_technical_indicators_contract() -> None:
    highs = [value + 2 for value in range(1, 81)]
    lows = [value - 1 for value in range(1, 81)]
    closes = [float(value) for value in range(1, 81)]
    volumes = [1000 + value * 10 for value in range(1, 81)]
    indicators = build_technical_indicators(highs, lows, closes, volumes)

    assert indicators["ma_5"] == 78
    assert indicators["ma_20"] == 70.5
    assert indicators["ma_60"] == 50.5
    assert indicators["rsi_14"] == 100
    assert indicators["macd"] is not None
    assert indicators["obv"] is not None

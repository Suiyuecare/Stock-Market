from app.services.indicators.macd import macd


def test_macd_returns_values_for_long_series() -> None:
    macd_line, signal_line, histogram = macd([float(value) for value in range(1, 80)])

    assert macd_line is not None
    assert signal_line is not None
    assert histogram is not None

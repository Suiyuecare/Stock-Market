from app.services.indicators.macd import analyze_macd, detect_macd_divergence, macd, macd_series


def test_macd_returns_values_for_long_series() -> None:
    macd_line, signal_line, histogram = macd([float(value) for value in range(1, 80)])

    assert macd_line is not None
    assert signal_line is not None
    assert histogram is not None


def test_macd_analysis_contract() -> None:
    prices = [float(value) for value in range(1, 80)]
    analysis = analyze_macd(prices)

    assert analysis["ema12"] is not None
    assert analysis["ema26"] is not None
    assert analysis["dif"] is not None
    assert analysis["dea"] is not None
    assert analysis["macd_hist"] is not None
    assert analysis["macd_bar_tw"] == round(2 * float(analysis["macd_hist"]), 4)
    assert isinstance(analysis["golden_cross"], bool)
    assert isinstance(analysis["death_cross"], bool)
    assert isinstance(analysis["zero_axis_cross_up"], bool)
    assert isinstance(analysis["zero_axis_cross_down"], bool)


def test_macd_series_lengths_match_prices() -> None:
    prices = [float(value) for value in range(1, 80)]
    series = macd_series(prices)

    assert len(series["ema12"]) == len(prices)
    assert len(series["ema26"]) == len(prices)
    assert len(series["dif"]) == len(prices)
    assert len(series["dea"]) == len(prices)
    assert len(series["macd_hist"]) == len(prices)
    assert len(series["macd_bar_tw"]) == len(prices)


def test_macd_bullish_and_bearish_divergence_detection() -> None:
    bullish = detect_macd_divergence(
        closes=[10, 9, 8, 7, 8, 9, 9, 8, 6, 7],
        macd_hist=[-2, -3, -4, -5, -3, -2, -1, -2, -3, -1],
        window=5,
    )
    bearish = detect_macd_divergence(
        closes=[10, 11, 12, 13, 12, 11, 12, 14, 15, 14],
        macd_hist=[1, 2, 3, 4, 3, 2, 2, 2.5, 3, 2],
        window=5,
    )

    assert bullish["bullish_divergence"] is True
    assert bearish["bearish_divergence"] is True

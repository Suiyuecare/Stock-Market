from app.services.indicators.volume_price_divergence import analyze_volume_price_divergence, volume_price_divergence


def test_volume_price_divergence_detects_volume_outperformance() -> None:
    value = volume_price_divergence([10, 10.5, 11, 11.5, 12, 12.2], [100, 110, 120, 130, 140, 220])

    assert value is not None
    assert value > 0


def test_volume_price_states() -> None:
    assert analyze_volume_price_divergence([10, 11], [100, 120])["state"] == "price_up_volume_up"
    assert analyze_volume_price_divergence([10, 11], [120, 100])["state"] == "price_up_volume_down"
    assert analyze_volume_price_divergence([11, 10], [120, 100])["state"] == "price_down_volume_down"
    assert analyze_volume_price_divergence([11, 10], [100, 120])["state"] == "price_down_volume_up"


def test_price_new_high_without_confirmation() -> None:
    analysis = analyze_volume_price_divergence(
        closes=[10, 11, 12, 13, 14, 15],
        volumes=[100, 130, 150, 170, 190, 120],
        macd_hist=[1, 1.2, 1.4, 1.5, 1.6, 1.1],
        window=5,
    )

    assert analysis["bearish_divergence"] is True
    assert "price_new_high_without_volume_obv_macd_confirmation" in analysis["states"]


def test_price_new_low_without_momentum_confirmation() -> None:
    analysis = analyze_volume_price_divergence(
        closes=[15, 14, 13, 12, 11, 10],
        volumes=[100, 150, 200, 250, 300, 120],
        macd_hist=[-1, -1.5, -2, -2.5, -3, -1.2],
        window=5,
    )

    assert analysis["bullish_divergence"] is True
    assert "price_new_low_without_macd_obv_new_low" in analysis["states"]

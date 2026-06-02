from app.services.indicators.volume_price_divergence import volume_price_divergence


def test_volume_price_divergence_detects_volume_outperformance() -> None:
    value = volume_price_divergence([10, 10.5, 11, 11.5, 12, 12.2], [100, 110, 120, 130, 140, 220])

    assert value is not None
    assert value > 0

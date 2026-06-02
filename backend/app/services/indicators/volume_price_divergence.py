from typing import Iterable, Optional


def volume_price_divergence(closes: Iterable[float], volumes: Iterable[float], window: int = 5) -> Optional[float]:
    """Return volume momentum minus price momentum over a fixed lookback window."""
    close_series = list(closes)
    volume_series = list(volumes)
    if len(close_series) <= window or len(volume_series) <= window:
        return None

    price_change = (close_series[-1] - close_series[-window - 1]) / close_series[-window - 1]
    volume_change = (volume_series[-1] - volume_series[-window - 1]) / max(volume_series[-window - 1], 1)
    return round(volume_change - price_change, 4)

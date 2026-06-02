from typing import Iterable, Optional


def stochastic_kd(
    highs: Iterable[float], lows: Iterable[float], closes: Iterable[float], window: int = 9
) -> tuple[Optional[float], Optional[float]]:
    high_series = list(highs)
    low_series = list(lows)
    close_series = list(closes)
    if len(close_series) < window:
        return None, None

    k_values = []
    for index in range(len(close_series) - window + 1, len(close_series) + 1):
        high = max(high_series[index - window : index])
        low = min(low_series[index - window : index])
        close = close_series[index - 1]
        k_values.append(50.0 if high == low else ((close - low) / (high - low)) * 100)

    k = k_values[-1]
    d = sum(k_values[-3:]) / min(3, len(k_values))
    return round(k, 4), round(d, 4)

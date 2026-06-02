from typing import Iterable, List, Optional


def ema(values: Iterable[float], window: int) -> List[float]:
    series = list(values)
    if not series:
        return []

    multiplier = 2 / (window + 1)
    result = [series[0]]
    for value in series[1:]:
        result.append((value - result[-1]) * multiplier + result[-1])
    return result


def macd(values: Iterable[float]) -> tuple[Optional[float], Optional[float], Optional[float]]:
    series = list(values)
    if len(series) < 26:
        return None, None, None

    ema_12 = ema(series, 12)
    ema_26 = ema(series, 26)
    macd_line = [fast - slow for fast, slow in zip(ema_12, ema_26)]
    signal_line = ema(macd_line, 9)
    histogram = macd_line[-1] - signal_line[-1]
    return round(macd_line[-1], 4), round(signal_line[-1], 4), round(histogram, 4)

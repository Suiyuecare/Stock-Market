from typing import Iterable, List, Optional


def _last(values: List[Optional[float]]) -> Optional[float]:
    return values[-1] if values else None


def moving_average(values: Iterable[float], window: int) -> Optional[float]:
    series = list(values)
    if len(series) < window:
        return None
    return round(sum(series[-window:]) / window, 4)


def rsi(values: Iterable[float], window: int = 14) -> Optional[float]:
    series = list(values)
    if len(series) <= window:
        return None

    gains = []
    losses = []
    for previous, current in zip(series[-window - 1 : -1], series[-window:]):
        change = current - previous
        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))

    average_gain = sum(gains) / window
    average_loss = sum(losses) / window
    if average_loss == 0:
        return 100.0

    relative_strength = average_gain / average_loss
    return round(100 - (100 / (1 + relative_strength)), 4)


def stochastic_kd(highs: Iterable[float], lows: Iterable[float], closes: Iterable[float], window: int = 9) -> tuple[Optional[float], Optional[float]]:
    high_series = list(highs)
    low_series = list(lows)
    close_series = list(closes)
    if len(close_series) < window:
        return None, None

    recent_high = max(high_series[-window:])
    recent_low = min(low_series[-window:])
    if recent_high == recent_low:
        return 50.0, 50.0

    k_values = []
    for index in range(len(close_series) - window + 1, len(close_series) + 1):
        high = max(high_series[index - window : index])
        low = min(low_series[index - window : index])
        close = close_series[index - 1]
        k_values.append(50.0 if high == low else ((close - low) / (high - low)) * 100)

    k = k_values[-1]
    d = sum(k_values[-3:]) / min(3, len(k_values))
    return round(k, 4), round(d, 4)


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


def obv(closes: Iterable[float], volumes: Iterable[float]) -> Optional[float]:
    close_series = list(closes)
    volume_series = list(volumes)
    if len(close_series) < 2 or len(close_series) != len(volume_series):
        return None

    total = 0.0
    for previous, current, volume in zip(close_series[:-1], close_series[1:], volume_series[1:]):
        if current > previous:
            total += volume
        elif current < previous:
            total -= volume
    return round(total, 4)


def volume_price_divergence(closes: Iterable[float], volumes: Iterable[float], window: int = 5) -> Optional[float]:
    close_series = list(closes)
    volume_series = list(volumes)
    if len(close_series) <= window or len(volume_series) <= window:
        return None

    price_change = (close_series[-1] - close_series[-window - 1]) / close_series[-window - 1]
    volume_change = (volume_series[-1] - volume_series[-window - 1]) / max(volume_series[-window - 1], 1)
    return round(volume_change - price_change, 4)


def build_technical_indicators(highs: Iterable[float], lows: Iterable[float], closes: Iterable[float], volumes: Iterable[float]) -> dict:
    close_series = list(closes)
    high_series = list(highs)
    low_series = list(lows)
    volume_series = list(volumes)
    k, d = stochastic_kd(high_series, low_series, close_series)
    macd_line, signal_line, histogram = macd(close_series)

    return {
        "ma_5": moving_average(close_series, 5),
        "ma_20": moving_average(close_series, 20),
        "ma_60": moving_average(close_series, 60),
        "rsi_14": rsi(close_series, 14),
        "k_9": k,
        "d_9": d,
        "macd": macd_line,
        "macd_signal": signal_line,
        "macd_histogram": histogram,
        "obv": obv(close_series, volume_series),
        "volume_price_divergence": volume_price_divergence(close_series, volume_series),
    }

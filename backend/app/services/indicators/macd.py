from typing import Dict, Iterable, List, Optional, Tuple


def ema(values: Iterable[float], window: int) -> List[float]:
    series = list(values)
    if not series:
        return []

    multiplier = 2 / (window + 1)
    result = [series[0]]
    for value in series[1:]:
        result.append((value - result[-1]) * multiplier + result[-1])
    return result


def macd(values: Iterable[float]) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    series = list(values)
    if len(series) < 26:
        return None, None, None

    analysis = analyze_macd(series)
    return analysis["dif"], analysis["dea"], analysis["macd_hist"]


def macd_series(values: Iterable[float]) -> Dict[str, List[float]]:
    series = list(values)
    if len(series) < 26:
        return {"ema12": [], "ema26": [], "dif": [], "dea": [], "macd_hist": [], "macd_bar_tw": []}

    ema_12 = ema(series, 12)
    ema_26 = ema(series, 26)
    dif = [fast - slow for fast, slow in zip(ema_12, ema_26)]
    dea = ema(dif, 9)
    macd_hist = [line - signal for line, signal in zip(dif, dea)]
    macd_bar_tw = [2 * value for value in macd_hist]
    return {
        "ema12": [round(value, 4) for value in ema_12],
        "ema26": [round(value, 4) for value in ema_26],
        "dif": [round(value, 4) for value in dif],
        "dea": [round(value, 4) for value in dea],
        "macd_hist": [round(value, 4) for value in macd_hist],
        "macd_bar_tw": [round(value, 4) for value in macd_bar_tw],
    }


def crossed_up(previous_left: float, previous_right: float, current_left: float, current_right: float) -> bool:
    return previous_left <= previous_right and current_left > current_right


def crossed_down(previous_left: float, previous_right: float, current_left: float, current_right: float) -> bool:
    return previous_left >= previous_right and current_left < current_right


def _recent_low(values: List[float], window: int) -> float:
    return min(values[-window:])


def _recent_high(values: List[float], window: int) -> float:
    return max(values[-window:])


def detect_macd_divergence(closes: Iterable[float], macd_hist: Iterable[float], window: int = 20) -> Dict[str, bool]:
    close_series = list(closes)
    hist_series = list(macd_hist)
    if len(close_series) < window * 2 or len(hist_series) < window * 2:
        return {"bullish_divergence": False, "bearish_divergence": False}

    previous_prices = close_series[-window * 2 : -window]
    recent_prices = close_series[-window:]
    previous_hist = hist_series[-window * 2 : -window]
    recent_hist = hist_series[-window:]

    bullish = _recent_low(recent_prices, window) < _recent_low(previous_prices, window) and _recent_low(recent_hist, window) > _recent_low(previous_hist, window)
    bearish = _recent_high(recent_prices, window) > _recent_high(previous_prices, window) and _recent_high(recent_hist, window) < _recent_high(previous_hist, window)
    return {"bullish_divergence": bullish, "bearish_divergence": bearish}


def analyze_macd(values: Iterable[float]) -> Dict[str, object]:
    """Calculate MACD values and latest crossover/divergence signals."""
    closes = list(values)
    series = macd_series(closes)
    if not series["dif"]:
        return {
            "ema12": None,
            "ema26": None,
            "dif": None,
            "dea": None,
            "macd_hist": None,
            "macd_bar_tw": None,
            "golden_cross": False,
            "death_cross": False,
            "zero_axis_cross_up": False,
            "zero_axis_cross_down": False,
            "bullish_divergence": False,
            "bearish_divergence": False,
        }

    dif = series["dif"]
    dea = series["dea"]
    hist = series["macd_hist"]
    previous_index = -2 if len(dif) > 1 else -1
    divergence = detect_macd_divergence(closes, hist)
    return {
        "ema12": series["ema12"][-1],
        "ema26": series["ema26"][-1],
        "dif": dif[-1],
        "dea": dea[-1],
        "macd_hist": hist[-1],
        "macd_bar_tw": series["macd_bar_tw"][-1],
        "golden_cross": crossed_up(dif[previous_index], dea[previous_index], dif[-1], dea[-1]),
        "death_cross": crossed_down(dif[previous_index], dea[previous_index], dif[-1], dea[-1]),
        "zero_axis_cross_up": dif[previous_index] <= 0 < dif[-1],
        "zero_axis_cross_down": dif[previous_index] >= 0 > dif[-1],
        **divergence,
    }

from typing import Dict, Iterable, List, Optional

from app.services.indicators.obv import obv_series


def _pct_change(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return (current - previous) / abs(previous)


def _new_high(series: List[float], window: int) -> bool:
    if len(series) <= window:
        return False
    return series[-1] > max(series[-window - 1 : -1])


def _new_low(series: List[float], window: int) -> bool:
    if len(series) <= window:
        return False
    return series[-1] < min(series[-window - 1 : -1])


def analyze_volume_price_divergence(
    closes: Iterable[float],
    volumes: Iterable[float],
    macd_hist: Optional[Iterable[float]] = None,
    window: int = 5,
) -> Dict[str, object]:
    """Detect common volume-price and momentum confirmation states."""
    close_series = list(closes)
    volume_series = list(volumes)
    hist_series = list(macd_hist or [])
    if len(close_series) < 2 or len(close_series) != len(volume_series):
        return {
            "state": "insufficient_data",
            "states": ["insufficient_data"],
            "score_signal": 0.0,
            "bearish_divergence": False,
            "bullish_divergence": False,
            "confidence": 0.0,
        }

    price_change_1d = close_series[-1] - close_series[-2]
    volume_change_1d = volume_series[-1] - volume_series[-2]
    price_direction = "up" if price_change_1d > 0 else "down" if price_change_1d < 0 else "flat"
    volume_direction = "up" if volume_change_1d > 0 else "down" if volume_change_1d < 0 else "flat"
    states: List[str] = []
    score_signal = 0.0

    if price_direction == "up" and volume_direction == "up":
        states.append("price_up_volume_up")
        score_signal += 0.25
    elif price_direction == "up" and volume_direction == "down":
        states.append("price_up_volume_down")
        score_signal -= 0.1
    elif price_direction == "down" and volume_direction == "down":
        states.append("price_down_volume_down")
        score_signal += 0.05
    elif price_direction == "down" and volume_direction == "up":
        states.append("price_down_volume_up")
        score_signal -= 0.25
    else:
        states.append(f"price_{price_direction}_volume_{volume_direction}")

    lookback = min(window, len(close_series) - 1)
    obv_values = obv_series(close_series, volume_series)
    price_new_high = _new_high(close_series, lookback)
    price_new_low = _new_low(close_series, lookback)
    volume_confirms_high = not price_new_high or volume_series[-1] >= max(volume_series[-lookback - 1 : -1])
    obv_confirms_high = not price_new_high or (obv_values and obv_values[-1] >= max(obv_values[-lookback - 1 : -1]))
    obv_confirms_low = not price_new_low or (obv_values and obv_values[-1] <= min(obv_values[-lookback - 1 : -1]))
    has_hist_lookback = len(hist_series) > lookback
    macd_confirms_high = not price_new_high or not has_hist_lookback or hist_series[-1] >= max(hist_series[-lookback - 1 : -1])
    macd_confirms_low = not price_new_low or not has_hist_lookback or hist_series[-1] <= min(hist_series[-lookback - 1 : -1])

    bearish_divergence = price_new_high and (not volume_confirms_high or not obv_confirms_high or not macd_confirms_high)
    bullish_divergence = price_new_low and (not obv_confirms_low or not macd_confirms_low)

    if bearish_divergence:
        states.append("price_new_high_without_volume_obv_macd_confirmation")
        score_signal -= 0.35
    if bullish_divergence:
        states.append("price_new_low_without_macd_obv_new_low")
        score_signal += 0.25

    if len(close_series) > lookback and len(volume_series) > lookback:
        price_change_window = _pct_change(close_series[-1], close_series[-lookback - 1])
        volume_change_window = _pct_change(volume_series[-1], volume_series[-lookback - 1])
    else:
        price_change_window = 0.0
        volume_change_window = 0.0

    return {
        "state": states[0],
        "states": states,
        "score_signal": round(max(-1.0, min(1.0, score_signal)), 4),
        "price_change": round(price_change_window, 4),
        "volume_change": round(volume_change_window, 4),
        "bearish_divergence": bearish_divergence,
        "bullish_divergence": bullish_divergence,
        "confidence": round(min(1.0, len(close_series) / max(window * 2, 1)), 4),
    }


def volume_price_divergence(closes: Iterable[float], volumes: Iterable[float], window: int = 5) -> Optional[float]:
    """Return a legacy numeric confirmation value for existing callers."""
    analysis = analyze_volume_price_divergence(closes, volumes, window=window)
    if analysis["state"] == "insufficient_data":
        return None
    return round(float(analysis["volume_change"]) - float(analysis["price_change"]), 4)

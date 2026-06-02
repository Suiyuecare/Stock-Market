from typing import Dict, Iterable, List, Optional


def obv(closes: Iterable[float], volumes: Iterable[float]) -> Optional[float]:
    values = obv_series(closes, volumes)
    if not values:
        return None
    return round(values[-1], 4)


def obv_series(closes: Iterable[float], volumes: Iterable[float]) -> List[float]:
    close_series = list(closes)
    volume_series = list(volumes)
    if len(close_series) < 2 or len(close_series) != len(volume_series):
        return []

    total = 0.0
    values = [total]
    for previous, current, volume in zip(close_series[:-1], close_series[1:], volume_series[1:]):
        if current > previous:
            total += volume
        elif current < previous:
            total -= volume
        values.append(round(total, 4))
    return values


def analyze_obv(closes: Iterable[float], volumes: Iterable[float], window: int = 5) -> Dict[str, object]:
    close_series = list(closes)
    volume_series = list(volumes)
    values = obv_series(close_series, volume_series)
    if len(values) < 2:
        return {
            "obv": None,
            "state": "insufficient_data",
            "positive_factors": [],
            "negative_factors": [],
            "risk_factors": ["not enough price/volume data for OBV"],
            "confidence": 0.0,
        }

    lookback = min(window, len(values) - 1)
    obv_change = values[-1] - values[-lookback - 1]
    price_change = close_series[-1] - close_series[-lookback - 1]
    positives = []
    negatives = []
    risks = []

    if obv_change > 0 and price_change >= 0:
        state = "accumulation_confirming_price"
        positives.append("OBV accumulation confirms price direction")
    elif obv_change < 0 and price_change <= 0:
        state = "distribution_confirming_price"
        negatives.append("OBV distribution confirms weak price direction")
    elif price_change > 0 and obv_change <= 0:
        state = "bearish_obv_divergence"
        risks.append("price rises without OBV confirmation")
    elif price_change < 0 and obv_change >= 0:
        state = "bullish_obv_divergence"
        positives.append("price weakens without OBV making a lower trend")
    else:
        state = "flat"

    return {
        "obv": round(values[-1], 4),
        "state": state,
        "obv_change": round(obv_change, 4),
        "positive_factors": positives,
        "negative_factors": negatives,
        "risk_factors": risks,
        "confidence": round(min(1.0, len(values) / max(window * 2, 1)), 4),
    }

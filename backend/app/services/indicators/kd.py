from typing import Dict, Iterable, Optional


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


def analyze_kd(highs: Iterable[float], lows: Iterable[float], closes: Iterable[float], window: int = 9) -> Dict[str, object]:
    high_series = list(highs)
    low_series = list(lows)
    close_series = list(closes)
    k, d = stochastic_kd(high_series, low_series, close_series, window)
    if k is None or d is None:
        return {
            "k": None,
            "d": None,
            "state": "insufficient_data",
            "positive_factors": [],
            "negative_factors": [],
            "risk_factors": ["not enough prices for KD"],
            "confidence": 0.0,
        }

    positives = []
    negatives = []
    risks = []
    if k > d and k < 80:
        state = "positive_momentum"
        positives.append("K above D with room before overbought zone")
    elif k < d:
        state = "negative_momentum"
        negatives.append("K below D")
    else:
        state = "neutral"
    if k >= 85 and d >= 80:
        state = "overbought"
        risks.append("KD overbought")
    elif k <= 20 and d <= 25:
        positives.append("KD near oversold recovery zone")

    return {
        "k": k,
        "d": d,
        "state": state,
        "positive_factors": positives,
        "negative_factors": negatives,
        "risk_factors": risks,
        "confidence": round(min(1.0, len(close_series) / window), 4),
    }

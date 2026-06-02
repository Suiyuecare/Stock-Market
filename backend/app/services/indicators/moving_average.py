from typing import Dict, Iterable, Optional


def moving_average(values: Iterable[float], window: int) -> Optional[float]:
    series = list(values)
    if len(series) < window:
        return None
    return round(sum(series[-window:]) / window, 4)


def analyze_moving_averages(values: Iterable[float]) -> Dict[str, object]:
    series = list(values)
    if not series:
        return {
            "ma5": None,
            "ma20": None,
            "ma60": None,
            "trend": "insufficient_data",
            "positive_factors": [],
            "negative_factors": [],
            "risk_factors": ["missing close prices"],
            "confidence": 0.0,
        }

    latest = series[-1]
    ma5 = moving_average(series, 5)
    ma20 = moving_average(series, 20)
    ma60 = moving_average(series, 60)
    positives = []
    negatives = []
    risks = []

    if ma5 is not None and ma20 is not None:
        if ma5 > ma20:
            positives.append("MA5 above MA20")
        else:
            negatives.append("MA5 below MA20")
    if ma20 is not None and ma60 is not None:
        if ma20 > ma60:
            positives.append("MA20 above MA60")
            trend = "uptrend"
        else:
            negatives.append("MA20 below MA60")
            trend = "downtrend"
    else:
        trend = "forming"
    if ma20 is not None:
        if latest > ma20:
            positives.append("close above MA20")
        else:
            negatives.append("close below MA20")
    if ma60 is not None and latest < ma60:
        risks.append("close below MA60")

    return {
        "ma5": ma5,
        "ma20": ma20,
        "ma60": ma60,
        "trend": trend,
        "positive_factors": positives,
        "negative_factors": negatives,
        "risk_factors": risks,
        "confidence": round(min(1.0, len(series) / 60), 4),
    }

from typing import Dict, Iterable, Optional


def rsi(values: Iterable[float], window: int = 14) -> Optional[float]:
    """Return RSI using a simple average gain/loss calculation for MVP scoring."""
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


def analyze_rsi(values: Iterable[float], window: int = 14) -> Dict[str, object]:
    series = list(values)
    value = rsi(series, window)
    if value is None:
        return {
            "rsi": None,
            "state": "insufficient_data",
            "positive_factors": [],
            "negative_factors": [],
            "risk_factors": ["not enough prices for RSI"],
            "confidence": 0.0,
        }

    positives = []
    negatives = []
    risks = []
    if 45 <= value <= 65:
        state = "constructive"
        positives.append("RSI in constructive range")
    elif 65 < value <= 75:
        state = "strong_momentum"
        positives.append("RSI shows strong momentum")
    elif value > 75:
        state = "overextended"
        risks.append("RSI overextended")
    elif 35 <= value < 45:
        state = "soft_momentum"
        negatives.append("RSI momentum soft")
    else:
        state = "weak"
        negatives.append("RSI weak")

    return {
        "rsi": value,
        "state": state,
        "positive_factors": positives,
        "negative_factors": negatives,
        "risk_factors": risks,
        "confidence": round(min(1.0, len(series) / (window + 1)), 4),
    }

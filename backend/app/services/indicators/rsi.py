from typing import Iterable, Optional


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

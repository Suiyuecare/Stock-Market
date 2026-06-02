from typing import Iterable, Optional


def moving_average(values: Iterable[float], window: int) -> Optional[float]:
    series = list(values)
    if len(series) < window:
        return None
    return round(sum(series[-window:]) / window, 4)

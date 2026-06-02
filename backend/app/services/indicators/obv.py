from typing import Iterable, Optional


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

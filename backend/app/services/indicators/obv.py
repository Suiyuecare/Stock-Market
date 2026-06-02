from typing import Iterable, List, Optional


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

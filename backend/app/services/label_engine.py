from datetime import datetime, timezone
from decimal import Decimal
from typing import Iterable, List, Optional, Union

from app.schemas import LabelResult

LABEL_VERSION = "label-v1"


Number = Union[Decimal, float, int]


def _decimal(value: Number) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def _return(start: Decimal, end: Decimal) -> Decimal:
    if start == 0:
        return Decimal("0")
    return (end - start) / start


def _max_excursions(start: Decimal, future_closes: Iterable[Decimal]) -> tuple[Decimal, Decimal]:
    returns = [_return(start, close) for close in future_closes]
    if not returns:
        return Decimal("0"), Decimal("0")
    return max(returns), min(returns)


def _tp_sl_label(start: Decimal, future_closes: List[Decimal], take_profit: Decimal, stop_loss: Decimal) -> int:
    for close in future_closes:
        future_return = _return(start, close)
        if future_return >= take_profit:
            return 1
        if future_return <= -abs(stop_loss):
            return 0
    return 0


class LabelEngine:
    """Builds point-in-time training labels for signal evaluation."""

    def build_labels(
        self,
        trade_date,
        stock_id: str,
        closes: List[Number],
        horizons: List[int] = [1, 5, 20],
        benchmark_closes: Optional[List[Number]] = None,
        transaction_cost: Number = Decimal("0.001"),
        minimum_excess_return: Number = Decimal("0.002"),
        take_profit: Number = Decimal("0.03"),
        stop_loss: Number = Decimal("0.02"),
        label_version: str = LABEL_VERSION,
        available_for_signal_at: Optional[datetime] = None,
    ) -> List[LabelResult]:
        normalized_closes = [_decimal(value) for value in closes]
        normalized_benchmark = [_decimal(value) for value in benchmark_closes] if benchmark_closes else None
        cost = _decimal(transaction_cost)
        min_excess = _decimal(minimum_excess_return)
        tp = _decimal(take_profit)
        sl = _decimal(stop_loss)
        calculated_at = datetime.now(timezone.utc)
        available_at = available_for_signal_at or calculated_at
        labels: List[LabelResult] = []

        if len(normalized_closes) < 2:
            return labels

        start = normalized_closes[0]
        for horizon in horizons:
            if len(normalized_closes) <= horizon:
                continue

            future_window = normalized_closes[1 : horizon + 1]
            forward_return = _return(start, normalized_closes[horizon])
            max_favorable, max_adverse = _max_excursions(start, future_window)
            benchmark_return = None
            excess_return = None
            if normalized_benchmark and len(normalized_benchmark) > horizon:
                benchmark_return = _return(normalized_benchmark[0], normalized_benchmark[horizon])
                excess_return = forward_return - benchmark_return

            labels.append(
                self._result(
                    trade_date,
                    stock_id,
                    f"up_{horizon}d_absolute",
                    1 if forward_return > 0 else 0,
                    horizon,
                    label_version,
                    forward_return,
                    benchmark_return,
                    excess_return,
                    max_favorable,
                    max_adverse,
                    cost,
                    min_excess,
                    calculated_at,
                    available_at,
                )
            )

            if benchmark_return is not None and excess_return is not None:
                labels.append(
                    self._result(
                        trade_date,
                        stock_id,
                        f"up_{horizon}d_relative",
                        1 if forward_return > benchmark_return + cost + min_excess else 0,
                        horizon,
                        label_version,
                        forward_return,
                        benchmark_return,
                        excess_return,
                        max_favorable,
                        max_adverse,
                        cost,
                        min_excess,
                        calculated_at,
                        available_at,
                    )
                )

            labels.append(
                self._result(
                    trade_date,
                    stock_id,
                    f"up_{horizon}d_tp_sl",
                    _tp_sl_label(start, future_window, tp, sl),
                    horizon,
                    label_version,
                    forward_return,
                    benchmark_return,
                    excess_return,
                    max_favorable,
                    max_adverse,
                    cost,
                    min_excess,
                    calculated_at,
                    available_at,
                )
            )

            downside = abs(max_adverse)
            risk_adjusted_return = forward_return / downside if downside > 0 else forward_return
            labels.append(
                self._result(
                    trade_date,
                    stock_id,
                    f"up_{horizon}d_risk_adjusted",
                    1 if risk_adjusted_return > Decimal("1.0") else 0,
                    horizon,
                    label_version,
                    forward_return,
                    benchmark_return,
                    excess_return,
                    max_favorable,
                    max_adverse,
                    cost,
                    min_excess,
                    calculated_at,
                    available_at,
                )
            )

        return labels

    def _result(
        self,
        trade_date,
        stock_id: str,
        label_name: str,
        label_value: int,
        horizon_days: int,
        label_version: str,
        forward_return: Decimal,
        benchmark_return: Optional[Decimal],
        excess_return: Optional[Decimal],
        max_favorable_excursion: Decimal,
        max_adverse_excursion: Decimal,
        transaction_cost: Decimal,
        minimum_excess_return: Decimal,
        calculated_at: datetime,
        available_for_signal_at: datetime,
    ) -> LabelResult:
        return LabelResult(
            trade_date=trade_date,
            stock_id=stock_id,
            label_name=label_name,
            label_value=label_value,
            horizon_days=horizon_days,
            label_version=label_version,
            forward_return=forward_return,
            benchmark_return=benchmark_return,
            excess_return=excess_return,
            max_favorable_excursion=max_favorable_excursion,
            max_adverse_excursion=max_adverse_excursion,
            transaction_cost=transaction_cost,
            minimum_excess_return=minimum_excess_return,
            calculated_at=calculated_at,
            available_for_signal_at=available_for_signal_at,
        )

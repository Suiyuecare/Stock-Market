from decimal import Decimal
from typing import List, Optional

from app.schemas import TargetVariableRequest, TargetVariableResult


class TargetVariableEngine:
    """Build target variables from next-session entry prices and future exits."""

    def build(self, request: TargetVariableRequest) -> List[TargetVariableResult]:
        results: List[TargetVariableResult] = []
        total_cost = request.config.fee_rate + request.config.transaction_tax_rate + request.config.slippage
        for horizon in request.config.horizons:
            if len(request.exit_prices) < horizon:
                continue
            exit_price = request.exit_prices[horizon - 1]
            net_return = self._net_return(request.entry_price, exit_price, total_cost)
            benchmark_return = self._benchmark_return(request, horizon)
            excess_return = net_return - benchmark_return if benchmark_return is not None else None

            results.append(
                self._result(
                    request,
                    f"y_abs_{horizon}d",
                    horizon,
                    1 if net_return > 0 else 0,
                    net_return,
                    benchmark_return,
                    excess_return,
                    exit_price,
                    total_cost,
                )
            )
            if benchmark_return is not None:
                hurdle = benchmark_return + request.config.cost_buffer + request.config.minimum_excess_return
                results.append(
                    self._result(
                        request,
                        f"y_rel_{horizon}d",
                        horizon,
                        1 if net_return > hurdle else 0,
                        net_return,
                        benchmark_return,
                        excess_return,
                        exit_price,
                        total_cost,
                    )
                )

            results.append(
                self._result(
                    request,
                    f"y_tp_sl_{horizon}d",
                    horizon,
                    self._tp_sl_label(request, horizon),
                    net_return,
                    benchmark_return,
                    excess_return,
                    exit_price,
                    total_cost,
                )
            )
        return results

    def primary_target(self, request: TargetVariableRequest) -> Optional[TargetVariableResult]:
        targets = self.build(request)
        return next((target for target in targets if target.target_name == request.config.primary_target), None)

    def _net_return(self, entry_price: Decimal, exit_price: Decimal, total_cost: Decimal) -> Decimal:
        if entry_price == 0:
            return Decimal("0")
        return exit_price / entry_price - Decimal("1") - total_cost

    def _benchmark_return(self, request: TargetVariableRequest, horizon: int) -> Optional[Decimal]:
        if not request.benchmark_entry_price or not request.benchmark_exit_prices:
            return None
        if len(request.benchmark_exit_prices) < horizon or request.benchmark_entry_price == 0:
            return None
        return request.benchmark_exit_prices[horizon - 1] / request.benchmark_entry_price - Decimal("1")

    def _tp_sl_label(self, request: TargetVariableRequest, horizon: int) -> int:
        highs = request.intraperiod_highs or request.exit_prices
        lows = request.intraperiod_lows or request.exit_prices
        for high, low in zip(highs[:horizon], lows[:horizon]):
            high_return = high / request.entry_price - Decimal("1")
            low_return = low / request.entry_price - Decimal("1")
            if high_return >= request.config.take_profit:
                return 1
            if low_return <= -abs(request.config.stop_loss):
                return 0
        return 0

    def _result(
        self,
        request: TargetVariableRequest,
        target_name: str,
        horizon_days: int,
        target_value: int,
        net_return: Decimal,
        benchmark_return: Optional[Decimal],
        excess_return: Optional[Decimal],
        exit_price: Decimal,
        total_cost: Decimal,
    ) -> TargetVariableResult:
        return TargetVariableResult(
            signal_date=request.signal_date,
            signal_time=request.signal_time,
            stock_id=request.stock_id,
            target_name=target_name,
            horizon_days=horizon_days,
            target_value=target_value,
            net_return=net_return,
            benchmark_return=benchmark_return,
            excess_return=excess_return,
            entry_price=request.entry_price,
            exit_price=exit_price,
            total_cost=total_cost,
            target_version=request.config.target_version,
        )

from datetime import timedelta
from decimal import Decimal
from typing import List, Optional, Tuple

from app.schemas import TradeManagementRequest, TradeManagementResult


class TradeManagementEngine:
    """Simulate entry, exit, and win definitions for research signals."""

    def evaluate(self, request: TradeManagementRequest) -> List[TradeManagementResult]:
        results: List[TradeManagementResult] = []
        total_cost = request.total_cost_rate or (
            request.config.fee_rate + request.config.transaction_tax_rate + request.config.slippage
        )
        stop_loss_pct = self._stop_loss_pct(request)
        take_profit_pct = request.config.take_profit_pct_range[0]
        cooldown_active = self._cooldown_active(request)

        for horizon in request.config.holding_days:
            capped_horizon = min(horizon, request.config.max_holding_days)
            if len(request.future_closes) < capped_horizon:
                continue
            exit_price, exit_reason, tp_sl_win = self._exit_path(request, capped_horizon, stop_loss_pct, take_profit_pct)
            net_return = self._net_return(request.entry_price, exit_price, total_cost)
            fixed_exit_price = request.future_closes[capped_horizon - 1]
            fixed_net_return = self._net_return(request.entry_price, fixed_exit_price, total_cost)
            benchmark_return = self._benchmark_return(request, capped_horizon)
            relative_win = None
            if benchmark_return is not None:
                relative_win = 1 if fixed_net_return > benchmark_return + request.config.cost_buffer else 0

            results.append(
                TradeManagementResult(
                    stock_id=request.stock_id,
                    signal_date=request.signal_date,
                    horizon_days=capped_horizon,
                    entry_method=request.config.entry_method,
                    exit_method=request.config.exit_method,
                    exit_reason=exit_reason,
                    entry_price=request.entry_price,
                    exit_price=exit_price,
                    net_return=net_return,
                    benchmark_return=benchmark_return,
                    fixed_horizon_win=1 if fixed_net_return > 0 else 0,
                    tp_sl_win=tp_sl_win,
                    relative_win=relative_win,
                    cooldown_active=cooldown_active,
                    applied_stop_loss_pct=stop_loss_pct,
                    applied_take_profit_pct=take_profit_pct,
                )
            )
        return results

    def _exit_path(
        self,
        request: TradeManagementRequest,
        horizon: int,
        stop_loss_pct: Decimal,
        take_profit_pct: Decimal,
    ) -> Tuple[Decimal, str, int]:
        trailing_stop_price: Optional[Decimal] = None
        for index, (high, low, close) in enumerate(
            zip(request.future_highs[:horizon], request.future_lows[:horizon], request.future_closes[:horizon])
        ):
            if high / request.entry_price - Decimal("1") >= take_profit_pct:
                return request.entry_price * (Decimal("1") + take_profit_pct), "take_profit", 1
            if low / request.entry_price - Decimal("1") <= -abs(stop_loss_pct):
                return request.entry_price * (Decimal("1") - abs(stop_loss_pct)), "stop_loss", 0
            if request.config.trailing_stop_enabled and request.atr is not None:
                candidate_stop = high - request.atr * request.config.trailing_stop_atr
                trailing_stop_price = max(trailing_stop_price or candidate_stop, candidate_stop)
                if index > 0 and low <= trailing_stop_price:
                    return trailing_stop_price, "trailing_stop", 0
            if close:
                continue
        return request.future_closes[horizon - 1], "fixed_horizon", 0

    def _stop_loss_pct(self, request: TradeManagementRequest) -> Decimal:
        percent_stop = request.config.stop_loss_pct_range[0]
        if request.config.stop_loss_method != "atr_or_percent" or request.atr is None or request.entry_price == 0:
            return percent_stop
        atr_stop = request.atr / request.entry_price * request.config.trailing_stop_atr
        lower, upper = request.config.stop_loss_pct_range
        return max(lower, min(upper, atr_stop))

    def _net_return(self, entry_price: Decimal, exit_price: Decimal, total_cost: Decimal) -> Decimal:
        if entry_price == 0:
            return Decimal("0")
        return exit_price / entry_price - Decimal("1") - total_cost

    def _benchmark_return(self, request: TradeManagementRequest, horizon: int) -> Optional[Decimal]:
        if not request.benchmark_entry_price or not request.benchmark_future_closes:
            return None
        if len(request.benchmark_future_closes) < horizon or request.benchmark_entry_price == 0:
            return None
        return request.benchmark_future_closes[horizon - 1] / request.benchmark_entry_price - Decimal("1")

    def _cooldown_active(self, request: TradeManagementRequest) -> bool:
        if not request.recent_loss_dates:
            return False
        latest_loss = max(request.recent_loss_dates)
        return request.signal_date <= latest_loss + timedelta(days=request.config.cooldown_days_after_loss)

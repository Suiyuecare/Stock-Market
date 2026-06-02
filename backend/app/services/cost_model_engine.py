from decimal import Decimal
from typing import Dict

from app.schemas import CostModelRequest, CostModelResult


class CostModelEngine:
    """Calculate configurable trading costs for labels, backtests, and simulations."""

    def calculate(self, request: CostModelRequest) -> CostModelResult:
        commission_buy = self._commission(request.buy_notional, request.config.commission_rate_buy, request.config.min_fee)
        commission_sell = self._commission(
            request.sell_notional,
            request.config.commission_rate_sell,
            request.config.min_fee,
        )
        transaction_tax = request.sell_notional * request.config.transaction_tax_rate
        slippage_bps = self._slippage_bps(request)
        slippage_buy = self._slippage_cost(request.buy_notional, slippage_bps)
        slippage_sell = self._slippage_cost(request.sell_notional, slippage_bps)
        total_cost = commission_buy + commission_sell + transaction_tax + slippage_buy + slippage_sell
        total_cost_rate = Decimal("0") if request.buy_notional == 0 else total_cost / request.buy_notional

        return CostModelResult(
            commission_buy=commission_buy,
            commission_sell=commission_sell,
            transaction_tax=transaction_tax,
            slippage_buy=slippage_buy,
            slippage_sell=slippage_sell,
            total_cost=total_cost,
            total_cost_rate=total_cost_rate,
            market_cap_bucket=request.market_cap_bucket,
            instrument_type=request.config.instrument_type,
            broker=request.config.broker,
        )

    def _commission(self, notional: Decimal, rate: Decimal, min_fee: Decimal) -> Decimal:
        if notional <= 0:
            return Decimal("0")
        return max(notional * rate, min_fee)

    def _slippage_bps(self, request: CostModelRequest) -> Decimal:
        bucket_map: Dict[str, Decimal] = {
            "large_cap": request.config.slippage_bps_large_cap,
            "mid_cap": request.config.slippage_bps_mid_cap,
            "small_cap": request.config.slippage_bps_small_cap,
        }
        return bucket_map.get(request.market_cap_bucket, request.config.slippage_bps_large_cap)

    def _slippage_cost(self, notional: Decimal, bps: Decimal) -> Decimal:
        if notional <= 0:
            return Decimal("0")
        return notional * bps / Decimal("10000")

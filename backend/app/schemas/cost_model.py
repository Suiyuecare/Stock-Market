from decimal import Decimal

from pydantic import BaseModel, Field


class CostModelConfig(BaseModel):
    commission_rate_buy: Decimal = Decimal("0.001425")
    commission_rate_sell: Decimal = Decimal("0.001425")
    transaction_tax_rate: Decimal = Decimal("0.003")
    slippage_bps_large_cap: Decimal = Decimal("3")
    slippage_bps_mid_cap: Decimal = Decimal("8")
    slippage_bps_small_cap: Decimal = Decimal("15")
    min_fee: Decimal = Decimal("20")
    instrument_type: str = "stock"
    broker: str = "default"


class CostModelRequest(BaseModel):
    buy_notional: Decimal
    sell_notional: Decimal
    market_cap_bucket: str = "large_cap"
    is_day_trade: bool = False
    config: CostModelConfig = Field(default_factory=CostModelConfig)


class CostModelResult(BaseModel):
    commission_buy: Decimal
    commission_sell: Decimal
    transaction_tax: Decimal
    slippage_buy: Decimal
    slippage_sell: Decimal
    total_cost: Decimal
    total_cost_rate: Decimal
    market_cap_bucket: str
    instrument_type: str
    broker: str

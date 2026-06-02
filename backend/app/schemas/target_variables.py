from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class TargetVariableConfig(BaseModel):
    horizons: List[int] = [1, 5, 20]
    entry_price_type: str = "next_open"
    primary_target: str = "y_rel_5d"
    fee_rate: Decimal = Decimal("0.001425")
    transaction_tax_rate: Decimal = Decimal("0.003")
    slippage: Decimal = Decimal("0.001")
    cost_buffer: Decimal = Decimal("0.001")
    minimum_excess_return: Decimal = Decimal("0.002")
    take_profit: Decimal = Decimal("0.03")
    stop_loss: Decimal = Decimal("0.02")
    target_version: str = "target-v1"


class TargetVariableRequest(BaseModel):
    signal_date: date
    signal_time: datetime
    stock_id: str
    entry_price: Decimal
    exit_prices: List[Decimal]
    benchmark_entry_price: Optional[Decimal] = None
    benchmark_exit_prices: Optional[List[Decimal]] = None
    intraperiod_highs: Optional[List[Decimal]] = None
    intraperiod_lows: Optional[List[Decimal]] = None
    config: TargetVariableConfig = TargetVariableConfig()


class TargetVariableResult(BaseModel):
    signal_date: date
    signal_time: datetime
    stock_id: str
    target_name: str
    horizon_days: int
    target_value: int
    net_return: Decimal
    benchmark_return: Optional[Decimal] = None
    excess_return: Optional[Decimal] = None
    entry_price: Decimal
    exit_price: Decimal
    total_cost: Decimal
    target_version: str

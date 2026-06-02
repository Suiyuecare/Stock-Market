from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class LabelResult(BaseModel):
    trade_date: date
    stock_id: str
    label_name: str
    label_value: int
    horizon_days: int
    label_version: str
    forward_return: Optional[Decimal] = None
    benchmark_return: Optional[Decimal] = None
    excess_return: Optional[Decimal] = None
    max_favorable_excursion: Optional[Decimal] = None
    max_adverse_excursion: Optional[Decimal] = None
    transaction_cost: Decimal = Decimal("0")
    minimum_excess_return: Decimal = Decimal("0")
    calculated_at: datetime
    available_for_signal_at: datetime


class LabelEngineRequest(BaseModel):
    trade_date: date
    stock_id: str
    closes: list[Decimal]
    benchmark_closes: Optional[list[Decimal]] = None
    horizon_days: int
    transaction_cost: Decimal = Decimal("0")
    minimum_excess_return: Decimal = Decimal("0")
    take_profit: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    label_version: str = "label-v1"
    available_for_signal_at: datetime

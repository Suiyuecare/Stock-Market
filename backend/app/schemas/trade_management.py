from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class TradeManagementConfig(BaseModel):
    entry_method: str = "next_open"
    exit_method: str = "fixed_horizon_or_tp_sl"
    holding_days: List[int] = Field(default_factory=lambda: [1, 5, 20])
    stop_loss_method: str = "atr_or_percent"
    stop_loss_pct_range: List[Decimal] = Field(default_factory=lambda: [Decimal("0.03"), Decimal("0.08")])
    take_profit_pct_range: List[Decimal] = Field(default_factory=lambda: [Decimal("0.05"), Decimal("0.15")])
    trailing_stop_enabled: bool = True
    trailing_stop_atr: Decimal = Decimal("1.5")
    max_holding_days: int = 20
    cooldown_days_after_loss: int = 3
    fee_rate: Decimal = Decimal("0.001425")
    transaction_tax_rate: Decimal = Decimal("0.003")
    slippage: Decimal = Decimal("0.001")
    cost_buffer: Decimal = Decimal("0.001")


class TradeManagementRequest(BaseModel):
    signal_date: date
    stock_id: str
    entry_price: Decimal
    future_closes: List[Decimal]
    future_highs: List[Decimal]
    future_lows: List[Decimal]
    benchmark_entry_price: Optional[Decimal] = None
    benchmark_future_closes: Optional[List[Decimal]] = None
    atr: Optional[Decimal] = None
    total_cost_rate: Optional[Decimal] = None
    recent_loss_dates: List[date] = Field(default_factory=list)
    config: TradeManagementConfig = TradeManagementConfig()


class TradeManagementResult(BaseModel):
    stock_id: str
    signal_date: date
    horizon_days: int
    entry_method: str
    exit_method: str
    exit_reason: str
    entry_price: Decimal
    exit_price: Decimal
    net_return: Decimal
    benchmark_return: Optional[Decimal] = None
    fixed_horizon_win: int
    tp_sl_win: int
    relative_win: Optional[int] = None
    cooldown_active: bool
    applied_stop_loss_pct: Decimal
    applied_take_profit_pct: Decimal

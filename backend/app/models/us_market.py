from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class USMarketDaily:
    """Domain model for US market inputs that affect Taiwan stocks."""

    trade_date: date
    symbol: str
    symbol_type: str
    close: float
    return_1d: float
    volume: Optional[float] = None
    ma20: Optional[float] = None
    ma60: Optional[float] = None
    rsi14: Optional[float] = None
    dif: Optional[float] = None
    dea: Optional[float] = None
    macd_hist: Optional[float] = None
    volume_price_signal: Optional[float] = None

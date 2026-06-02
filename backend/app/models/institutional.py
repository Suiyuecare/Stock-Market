from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class InstitutionalTradingDay:
    """Domain model for one day of Taiwan institutional trading flow."""

    trade_date: date
    stock_id: str
    foreign_net: float
    investment_trust_net: float
    dealer_net: float
    dealer_self_net: float
    dealer_hedge_net: float
    total_institutional_net: float
    volume: float
    close: float
    ma20: Optional[float] = None

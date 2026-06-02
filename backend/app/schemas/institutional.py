from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class InstitutionalTradingInput(BaseModel):
    trade_date: date
    stock_id: str
    foreign_net: float
    investment_trust_net: float
    dealer_net: float
    dealer_self_net: float = 0
    dealer_hedge_net: float = 0
    total_institutional_net: Optional[float] = None
    volume: float
    close: float
    ma20: Optional[float] = None


class ChipScoreRequest(BaseModel):
    stock_id: str
    observations: List[InstitutionalTradingInput]


class ChipScoreResponse(BaseModel):
    score: float
    positive_factors: List[str]
    negative_factors: List[str]
    risk_factors: List[str]
    confidence: float
    foreign_net_ratio: float
    investment_trust_net_ratio: float
    dealer_net_ratio: float
    institutional_net_ratio: float
    consecutive_foreign_net_buy_days: int
    consecutive_investment_trust_net_buy_days: int

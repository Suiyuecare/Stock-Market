from datetime import date
from typing import List

from pydantic import BaseModel


class PortfolioCandidate(BaseModel):
    stock_id: str
    signal_date: date
    selection_decision: str
    score: float
    sector: str
    proposed_weight: float
    volatility_20d: float
    is_electronics: bool = False


class PortfolioRiskConfig(BaseModel):
    max_single_stock_weight: float = 0.12
    max_sector_weight: float = 0.35
    max_holdings: int = 12
    max_new_signals_per_day: int = 5
    max_drawdown_limit: float = 0.15
    max_volatility_limit: float = 0.28
    consecutive_loss_limit: int = 3
    high_vix_threshold: float = 25.0
    weak_us_futures_threshold: float = -0.01
    high_vix_exposure_multiplier: float = 0.75
    drawdown_exposure_multiplier: float = 0.65
    volatility_exposure_multiplier: float = 0.7
    consecutive_loss_exposure_multiplier: float = 0.75
    weak_us_futures_electronics_multiplier: float = 0.65


class PortfolioRiskState(BaseModel):
    current_drawdown: float = 0.0
    portfolio_volatility: float = 0.0
    consecutive_losses: int = 0
    vix_level: float = 0.0
    us_futures_return: float = 0.0


class PortfolioAllocation(BaseModel):
    stock_id: str
    sector: str
    weight: float
    original_weight: float
    risk_adjusted_weight: float
    reasons: List[str]


class PortfolioRiskResult(BaseModel):
    signal_date: date
    total_target_exposure: float
    allocations: List[PortfolioAllocation]
    excluded: List[PortfolioAllocation]
    risk_flags: List[str]
    notes: List[str]

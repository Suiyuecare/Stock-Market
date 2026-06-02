from typing import Dict, List

from pydantic import BaseModel


class SignalQualityThresholds(BaseModel):
    minimum_win_rate: float = 0.55
    minimum_expectancy: float = 0.0
    minimum_trade_count: int = 30
    maximum_drawdown: float = 0.12
    minimum_average_return: float = 0.0
    minimum_profit_factor: float = 1.1


class SignalQualityInput(BaseModel):
    win_rate: float
    trade_count: int
    average_return: float
    expectancy: float
    max_drawdown: float
    profit_factor: float
    max_single_loss: float
    transaction_cost: float = 0.0
    slippage: float = 0.0


class SignalQualityResult(BaseModel):
    passed: bool
    quality_grade: str
    quality_score: float
    reasons: List[str]
    warnings: List[str]
    metrics: Dict[str, float]

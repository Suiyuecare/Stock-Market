from typing import List

from pydantic import BaseModel

from app.schemas.backtest import BacktestResult


class ObjectiveScoreConfig(BaseModel):
    z_score: float = 1.96
    average_return_scale: float = 0.03
    profit_factor_scale: float = 2.0
    max_drawdown_scale: float = 0.2
    win_rate_lower_bound_weight: float = 0.40
    average_net_return_weight: float = 0.20
    profit_factor_weight: float = 0.15
    calibration_weight: float = 0.10
    stability_weight: float = 0.10
    max_drawdown_penalty_weight: float = 0.05


class ObjectiveScoreRequest(BaseModel):
    backtest_result: BacktestResult
    calibration_score: float = 0.0
    stability_score: float = 0.0
    config: ObjectiveScoreConfig = ObjectiveScoreConfig()


class ObjectiveScoreResult(BaseModel):
    objective_score: float
    win_rate_lower_bound: float
    raw_win_rate: float
    average_net_return_score: float
    profit_factor_score: float
    calibration_score: float
    stability_score: float
    max_drawdown_penalty: float
    adjusted_win_score: float
    trade_count: int
    positive_factors: List[str]
    negative_factors: List[str]
    risk_factors: List[str]

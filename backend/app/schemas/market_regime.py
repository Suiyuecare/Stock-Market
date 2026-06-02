from typing import Dict, List

from pydantic import BaseModel


class MarketRegimeInput(BaseModel):
    tw_index_return_20d: float = 0.0
    tw_index_return_60d: float = 0.0
    tw_index_above_ma60: bool = False
    range_position_20d: float = 0.5
    volatility_20d: float = 0.0
    volatility_percentile: float = 0.5
    foreign_net_flow_20d: float = 0.0
    nasdaq_return_20d: float = 0.0
    sox_return_20d: float = 0.0
    vix_change_20d: float = 0.0
    tsm_adr_return_20d: float = 0.0


class MarketRegimeResult(BaseModel):
    primary_regime: str
    active_regimes: List[str]
    factor_weight_adjustments: Dict[str, float]
    risk_weight_multiplier: float
    confidence: float
    explanations: List[str]

from typing import Dict, List

from pydantic import BaseModel


class FactorWeightProfile(BaseModel):
    name: str
    description: str
    factor_weights: Dict[str, float]
    risk_score_weight: float
    signal_policy_notes: List[str]


class FactorWeightPresetCatalog(BaseModel):
    general_tw_stock: FactorWeightProfile
    electronics_semiconductor_ai: FactorWeightProfile
    domestic_traditional_construction: FactorWeightProfile
    bear_or_high_volatility: FactorWeightProfile

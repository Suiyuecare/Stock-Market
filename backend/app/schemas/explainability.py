from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class ExplainabilityDataSource(BaseModel):
    source: str
    dataset_name: str
    version: str
    available_for_signal_at: datetime
    fields_used: List[str]


class ExplainabilityFactorContribution(BaseModel):
    factor_name: str
    score: float
    weight: float
    contribution: float
    direction: str
    explanation: str
    data_sources: List[str]


class ExplainabilityReportInput(BaseModel):
    signal_id: str
    stock_id: str
    stock_name: str
    generated_at: datetime
    model_version: str
    scoring_version: str
    final_prediction: Dict[str, object]
    factor_scores: Dict[str, Dict[str, object]]
    data_sources: List[ExplainabilityDataSource]
    calibration_summary: Optional[Dict[str, object]] = None
    selection_decision: Optional[Dict[str, object]] = None
    market_regime: Optional[Dict[str, object]] = None
    portfolio_context: Optional[Dict[str, object]] = None


class ExplainabilityReport(BaseModel):
    signal_id: str
    stock_id: str
    stock_name: str
    generated_at: datetime
    model_version: str
    scoring_version: str
    data_sources: List[ExplainabilityDataSource]
    score_calculation: Dict[str, object]
    positive_factors: List[ExplainabilityFactorContribution]
    negative_factors: List[ExplainabilityFactorContribution]
    risk_factors: List[str]
    historical_win_rate_summary: Optional[Dict[str, object]]
    selection_summary: Optional[Dict[str, object]]
    market_regime_summary: Optional[Dict[str, object]]
    portfolio_risk_summary: Optional[Dict[str, object]]
    user_visible_text: str
    disclaimer: str

from typing import Dict, List, Optional

from pydantic import BaseModel


class TaiwanStockProfile(BaseModel):
    stock_id: str
    stock_name: Optional[str] = None
    industry: Optional[str] = None
    supply_chain_tags: List[str] = []
    us_market_sensitivity: float = 1.0


class USTWSensitivityInput(BaseModel):
    us_ticker: str
    tw_stock_id: str
    relation_type: str
    supply_chain_tag: str
    sensitivity_weight: float
    confidence: float = 0.5


class USMarketScoreRequest(BaseModel):
    linkage: Dict[str, float]
    stock_profile: TaiwanStockProfile
    sensitivity_mapping: List[USTWSensitivityInput] = []


class USMarketScoreResponse(BaseModel):
    score: float
    positive_factors: List[str]
    negative_factors: List[str]
    risk_factors: List[str]
    confidence: float
    us_index_score: float
    us_semiconductor_ai_score: float
    us_supply_chain_stock_score: float
    adr_score: float
    us_macro_liquidity_score: float
    us_news_sentiment_score: float
    sensitivity_multiplier: float

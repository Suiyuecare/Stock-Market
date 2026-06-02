from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str


class Instrument(BaseModel):
    symbol: str
    market: str
    name: str
    sector: Optional[str] = None
    currency: str


class TechnicalIndicators(BaseModel):
    ma_5: Optional[float] = None
    ma_20: Optional[float] = None
    ma_60: Optional[float] = None
    rsi_14: Optional[float] = None
    k_9: Optional[float] = None
    d_9: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    obv: Optional[float] = None
    volume_price_divergence: Optional[float] = None


class FactorScore(BaseModel):
    name: str
    category: str
    score: float
    weight: float
    direction: str
    explanation: str


class RiskScore(BaseModel):
    total: float
    volatility: float
    liquidity: float
    concentration: float
    event: float
    explanation: str


class NewsEvent(BaseModel):
    title: str
    source: str
    published_at: datetime
    sentiment: str
    impact_score: float
    related_symbols: List[str]


class MarketSummary(BaseModel):
    session_date: date
    tw_status: str
    us_premarket_status: str
    disclaimer: str
    instruments: List[Instrument]
    us_linkage: Dict[str, float]


class PredictionSignal(BaseModel):
    symbol: str
    name: str
    signal_date: date
    horizon: str
    probability_up: float
    confidence: float
    composite_score: float
    risk_score: RiskScore
    technicals: TechnicalIndicators
    factor_scores: List[FactorScore]
    positive_drivers: List[FactorScore]
    negative_drivers: List[FactorScore]
    news: List[NewsEvent]


class NewsParseRequest(BaseModel):
    title: str
    body: str
    source: str = "manual"
    published_at: Optional[datetime] = None


class NewsParseResponse(BaseModel):
    summary: str
    tickers: List[str]
    sentiment: str
    impact_score: float
    reasons: List[str]


class RankingResponse(BaseModel):
    disclaimer: str
    signals: List[PredictionSignal]


class StockDetailResponse(BaseModel):
    disclaimer: str
    instrument: Instrument
    signal: PredictionSignal
    factor_history: List[Dict[str, Any]]

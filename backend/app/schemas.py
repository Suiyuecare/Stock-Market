from datetime import date, datetime
from typing import Any, Optional

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


class MarketSummary(BaseModel):
    session_date: date
    tw_status: str
    us_premarket_status: str
    instruments: list[Instrument]


class PredictionSignal(BaseModel):
    symbol: str
    signal_date: date
    horizon: str
    score: float
    confidence: float
    drivers: list[dict[str, Any]]


class NewsParseRequest(BaseModel):
    title: str
    body: str
    source: str = "manual"
    published_at: Optional[datetime] = None


class NewsParseResponse(BaseModel):
    summary: str
    tickers: list[str]
    sentiment: str
    impact_score: float
    reasons: list[str]

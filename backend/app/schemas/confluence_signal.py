from datetime import date
from typing import List

from pydantic import BaseModel


class BullishConfluenceInput(BaseModel):
    stock_id: str
    signal_date: date
    fundamental_score: float
    chip_score: float
    technical_score: float
    us_market_score: float
    news_score: float
    risk_score: float
    liquidity_score: float
    macd_death_cross: bool = False
    macd_bearish_divergence: bool = False
    high_price_volume_divergence: bool = False
    three_institutions_sync_sell: bool = False
    has_major_negative_news: bool = False


class BullishConfluenceConfig(BaseModel):
    min_fundamental_score: float = 60.0
    min_chip_score: float = 65.0
    min_technical_score: float = 65.0
    min_us_market_score: float = 55.0
    min_news_score: float = 50.0
    max_risk_score: float = 55.0
    min_liquidity_score: float = 50.0
    min_passed_conditions: int = 8
    reject_macd_death_cross: bool = True
    reject_macd_bearish_divergence: bool = True
    reject_high_price_volume_divergence: bool = True
    reject_three_institutions_sync_sell: bool = True
    reject_major_negative_news: bool = True


class BullishConfluenceResult(BaseModel):
    stock_id: str
    signal_date: date
    passed: bool
    confluence_score: float
    passed_conditions: List[str]
    failed_conditions: List[str]
    rejection_reasons: List[str]
    risk_flags: List[str]

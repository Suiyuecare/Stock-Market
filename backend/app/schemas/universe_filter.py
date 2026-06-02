from typing import List

from pydantic import BaseModel


class UniverseFilterConfig(BaseModel):
    min_listing_days: int = 250
    min_close_price: float = 10.0
    min_avg_turnover_20d_twd: float = 50_000_000.0
    exclude_full_delivery_stocks: bool = True
    exclude_disposition_stocks: bool = True
    exclude_attention_stocks_for_conservative_mode: bool = True
    exclude_low_liquidity: bool = True
    exclude_recent_extreme_gap: bool = True
    exclude_missing_fundamental_data: bool = True
    extreme_gap_threshold: float = 0.08


class UniverseFilterCandidate(BaseModel):
    stock_id: str
    listing_days: int
    close_price: float
    avg_turnover_20d_twd: float
    is_full_delivery_stock: bool = False
    is_disposition_stock: bool = False
    is_attention_stock: bool = False
    has_low_liquidity: bool = False
    recent_gap_pct: float = 0.0
    has_missing_fundamental_data: bool = False


class UniverseFilterResult(BaseModel):
    stock_id: str
    included: bool
    exclusion_reasons: List[str]
    risk_flags: List[str]

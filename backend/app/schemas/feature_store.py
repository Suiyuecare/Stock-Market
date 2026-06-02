from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class FeatureStoreDailyInput(BaseModel):
    trade_date: date
    stock_id: str
    feature_group: str
    feature_name: str
    feature_value: Decimal
    feature_version: str
    calculated_at: datetime
    available_for_signal_at: datetime


class FeatureStoreDailyRecord(FeatureStoreDailyInput):
    pass


class FeatureStoreQuery(BaseModel):
    stock_id: str
    trade_date: date
    signal_generated_at: datetime
    feature_group: Optional[str] = None

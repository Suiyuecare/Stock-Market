from typing import List, Optional

from pydantic import BaseModel


class CalibrationSample(BaseModel):
    predicted_probability: float
    actual_outcome: int
    horizon_days: int
    stock_id: Optional[str] = None
    sector: Optional[str] = None
    market_state: Optional[str] = None


class CalibrationBucket(BaseModel):
    lower_bound: float
    upper_bound: float
    sample_count: int
    average_predicted_probability: float
    actual_win_rate: float
    calibration_error: float
    brier_score: float
    reliability_status: str


class CalibrationResult(BaseModel):
    horizon_days: int
    sample_count: int
    brier_score: float
    expected_calibration_error: float
    max_calibration_error: float
    buckets: List[CalibrationBucket]

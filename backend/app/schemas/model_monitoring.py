from datetime import date
from typing import Dict, List

from pydantic import BaseModel


class ModelMonitoringInput(BaseModel):
    monitoring_date: date
    win_rate_20d: float
    win_rate_60d: float
    historical_win_rate_mean: float
    historical_win_rate_std: float
    average_return_20d: float
    max_drawdown_20d: float
    calibration_error: float
    sector_win_rate_20d: Dict[str, float]
    historical_sector_win_rate: Dict[str, float]
    factor_contribution_20d: Dict[str, float]
    historical_factor_contribution: Dict[str, float]
    data_latency_minutes: float
    api_failure_rate: float
    news_parse_error_rate: float


class ModelMonitoringThresholds(BaseModel):
    win_rate_std_alert_multiplier: float = 2.0
    calibration_error_threshold: float = 0.08
    max_drawdown_threshold: float = 0.12
    data_latency_minutes_threshold: float = 30.0
    api_failure_rate_threshold: float = 0.05
    news_parse_error_rate_threshold: float = 0.08
    sector_win_rate_drop_threshold: float = 0.12
    factor_contribution_drift_threshold: float = 0.15


class ModelMonitoringAlert(BaseModel):
    code: str
    severity: str
    message: str
    recommended_action: str


class ModelMonitoringResult(BaseModel):
    monitoring_date: date
    health_status: str
    signal_strength_multiplier: float
    metrics: Dict[str, object]
    alerts: List[ModelMonitoringAlert]

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.backtest import BacktestResult
from app.schemas.feature_store import FeatureStoreDailyRecord
from app.schemas.objective_score import ObjectiveScoreResult
from app.schemas.signal_pipeline import SignalPerformanceStatsRecord


class FeatureSnapshotRequest(BaseModel):
    trade_date: date
    stock_id: str
    features: Dict[str, Decimal]
    feature_group: str = "snapshot"
    feature_version: str = "feature-v1"
    calculated_at: datetime
    available_for_signal_at: datetime


class FeatureSnapshotResult(BaseModel):
    records: List[FeatureStoreDailyRecord]


class PerformanceStatsInput(BaseModel):
    model_version: str
    strategy_version: str
    horizon_days: int
    market_regime: str = "all"
    industry: str = "all"
    probability_bucket: str = "all"
    risk_bucket: str = "all"
    backtest_result: BacktestResult
    calibration_error: Decimal = Decimal("0")


class PerformanceStatsResult(BaseModel):
    stats: SignalPerformanceStatsRecord


class StrategyParameterSet(BaseModel):
    strategy_version: str
    probability_threshold: float = 0.60
    risk_score_threshold: float = 55.0
    bullish_score_threshold: float = 65.0
    holding_period: int = 5
    stop_loss: float = 0.06
    take_profit: float = 0.10
    top_k_per_day: int = 20
    max_per_industry: int = 5
    factor_weight_profile: str = "general"
    market_regime_filter: Optional[str] = None
    us_market_score_threshold: Optional[float] = None
    reject_macd_bearish_divergence: bool = True
    reject_volume_price_divergence: bool = True
    require_institutional_net_buy: bool = False
    confidence_threshold: float = 0.60


class StrategyOptimizationConfig(BaseModel):
    min_total_trades: int = 500
    min_trades_per_fold: int = 100
    min_average_net_return: float = 0.0
    min_profit_factor: float = 1.2
    max_drawdown_limit: float = 0.20
    min_confidence: float = 0.60
    default_calibration_score: float = 0.80
    default_stability_score: float = 0.80


class StrategyOptimizationCandidate(BaseModel):
    parameters: StrategyParameterSet
    backtest_result: BacktestResult
    calibration_error: float = 0.0
    stability_score: float = 0.80
    confidence: float = 0.60
    best_market_regime: Optional[str] = None
    worst_market_regime: Optional[str] = None
    top_positive_factor_combinations: List[str] = Field(default_factory=list)
    top_failure_patterns: List[str] = Field(default_factory=list)


class StrategyOptimizationSummary(BaseModel):
    strategy_version: str
    passed_constraints: bool
    rejection_reasons: List[str]
    objective: Optional[ObjectiveScoreResult] = None


class StrategyOptimizationResult(BaseModel):
    best_strategy_version: Optional[str]
    best_objective_score: Optional[float]
    best_parameters: Optional[StrategyParameterSet]
    ranked_results: List[StrategyOptimizationSummary]
    rejected_results: List[StrategyOptimizationSummary]


class BacktestRunRecord(BaseModel):
    run_id: str
    strategy_version: str
    model_version: str
    feature_version: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "completed"
    split_method: str = "walk_forward"
    train_window_days: int
    validation_window_days: int
    test_window_days: int
    embargo_days: int = 5
    objective_score: Optional[Decimal] = None
    notes: Optional[str] = None


class BacktestResultRecordSchema(BaseModel):
    result_id: str
    run_id: str
    strategy_version: str
    horizon_days: int
    market_regime: str = "all"
    industry: str = "all"
    liquidity_bucket: str = "all"
    probability_bucket: str = "all"
    risk_bucket: str = "all"
    win_rate: Decimal
    win_rate_lower_bound: Decimal
    trade_count: int
    average_net_return: Decimal
    median_net_return: Decimal
    profit_factor: Decimal
    max_drawdown: Decimal
    sharpe_ratio: Decimal
    calibration_error: Decimal
    best_parameter_set: Dict[str, object] = Field(default_factory=dict)
    worst_market_regime: Optional[str] = None
    best_market_regime: Optional[str] = None
    top_positive_factor_combinations: List[str] = Field(default_factory=list)
    top_failure_patterns: List[str] = Field(default_factory=list)


class StrategyParameterRecord(BaseModel):
    strategy_version: str
    parameter_group: str
    parameter_name: str
    parameter_value: str
    parameter_json: Optional[Dict[str, object]] = None
    created_at: datetime

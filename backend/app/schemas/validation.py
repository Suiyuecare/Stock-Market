from datetime import date
from typing import Dict, List

from pydantic import BaseModel

from app.schemas.backtest import BacktestConfig, BacktestResult


class ValidationConfig(BaseModel):
    split_method: str = "walk_forward"
    train_window_days: int = 756
    validation_window_days: int = 126
    test_window_days: int = 126
    retrain_frequency: str = "monthly"
    embargo_days: int = 5
    min_trades_per_fold: int = 100
    min_total_trades: int = 500
    evaluate_by_market_regime: bool = True
    evaluate_by_industry: bool = True
    evaluate_by_liquidity_bucket: bool = True
    backtest_config: BacktestConfig = BacktestConfig()


class ValidationFold(BaseModel):
    fold_index: int
    train_start: date
    train_end: date
    validation_start: date
    validation_end: date
    test_start: date
    test_end: date
    train_sample_count: int
    validation_trade_count: int
    test_trade_count: int
    passed_min_trades: bool
    validation_result: BacktestResult
    test_result: BacktestResult


class ValidationResult(BaseModel):
    split_method: str
    retrain_frequency: str
    embargo_days: int
    fold_count: int
    total_test_trades: int
    passed_min_total_trades: bool
    passed_all_folds: bool
    folds: List[ValidationFold]
    win_rate_by_market_regime: Dict[str, float]
    win_rate_by_industry: Dict[str, float]
    win_rate_by_liquidity_bucket: Dict[str, float]
    warnings: List[str]

from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel


class BacktestObservation(BaseModel):
    trade_date: date
    stock_id: str
    probability: float
    forward_return: float
    holding_days: int
    sector: Optional[str] = None
    market_state: Optional[str] = None
    market_cap_bucket: Optional[str] = None
    liquidity_bucket: Optional[str] = None
    max_favorable_excursion: Optional[float] = None
    max_adverse_excursion: Optional[float] = None


class BacktestConfig(BaseModel):
    holding_days: int = 5
    entry_probability_threshold: float = 0.6
    transaction_cost: float = 0.001
    slippage: float = 0.001
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    market_state: Optional[str] = None
    sector: Optional[str] = None
    market_cap_bucket: Optional[str] = None
    liquidity_bucket: Optional[str] = None


class BacktestTrade(BaseModel):
    trade_date: date
    stock_id: str
    holding_days: int
    gross_return: float
    net_return: float
    exit_reason: str
    sector: Optional[str] = None
    market_state: Optional[str] = None
    market_cap_bucket: Optional[str] = None
    liquidity_bucket: Optional[str] = None


class BacktestResult(BaseModel):
    win_rate: float
    trade_count: int
    average_return: float
    median_return: float
    expectancy: float
    max_drawdown: float
    profit_factor: float
    sharpe_ratio: float
    sortino_ratio: float
    max_single_loss: float
    max_consecutive_losses: int
    average_holding_days: float
    turnover: float
    win_rate_by_sector: Dict[str, float]
    win_rate_by_market_state: Dict[str, float]
    trades: List[BacktestTrade]


class TimeSeriesSplitWindow(BaseModel):
    train_start: date
    train_end: date
    test_start: date
    test_end: date

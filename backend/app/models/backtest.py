from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class BacktestRun(Base):
    """Point-in-time record for a walk-forward or strategy optimization run."""

    __tablename__ = "backtest_runs"
    __table_args__ = (
        Index("ix_backtest_runs_strategy_model", "strategy_version", "model_version"),
        Index("ix_backtest_runs_started_at", "started_at"),
    )

    run_id: Mapped[str] = mapped_column(String, primary_key=True)
    strategy_version: Mapped[str] = mapped_column(String, nullable=False)
    model_version: Mapped[str] = mapped_column(String, nullable=False)
    feature_version: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String, nullable=False, default="completed")
    split_method: Mapped[str] = mapped_column(String, nullable=False, default="walk_forward")
    train_window_days: Mapped[int] = mapped_column(Integer, nullable=False)
    validation_window_days: Mapped[int] = mapped_column(Integer, nullable=False)
    test_window_days: Mapped[int] = mapped_column(Integer, nullable=False)
    embargo_days: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    objective_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    notes: Mapped[Optional[str]] = mapped_column(String)


class BacktestResultRecord(Base):
    """Aggregated strategy result stored for ranking and auditability."""

    __tablename__ = "backtest_results"
    __table_args__ = (
        Index("ix_backtest_results_run", "run_id"),
        Index("ix_backtest_results_strategy_horizon", "strategy_version", "horizon_days"),
    )

    result_id: Mapped[str] = mapped_column(String, primary_key=True)
    run_id: Mapped[str] = mapped_column(String, ForeignKey("backtest_runs.run_id", ondelete="CASCADE"), nullable=False)
    strategy_version: Mapped[str] = mapped_column(String, nullable=False)
    horizon_days: Mapped[int] = mapped_column(Integer, nullable=False)
    market_regime: Mapped[str] = mapped_column(String, nullable=False, default="all")
    industry: Mapped[str] = mapped_column(String, nullable=False, default="all")
    liquidity_bucket: Mapped[str] = mapped_column(String, nullable=False, default="all")
    probability_bucket: Mapped[str] = mapped_column(String, nullable=False, default="all")
    risk_bucket: Mapped[str] = mapped_column(String, nullable=False, default="all")
    win_rate: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    win_rate_lower_bound: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    trade_count: Mapped[int] = mapped_column(Integer, nullable=False)
    average_net_return: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    median_net_return: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    profit_factor: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    max_drawdown: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    sharpe_ratio: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    calibration_error: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    best_parameter_set: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    worst_market_regime: Mapped[Optional[str]] = mapped_column(String)
    best_market_regime: Mapped[Optional[str]] = mapped_column(String)
    top_positive_factor_combinations: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    top_failure_patterns: Mapped[list] = mapped_column(JSON, nullable=False, default=list)


class StrategyParameter(Base):
    """Versioned strategy setting used by a backtest or signal generation run."""

    __tablename__ = "strategy_parameters"
    __table_args__ = (Index("ix_strategy_parameters_version", "strategy_version"),)

    strategy_version: Mapped[str] = mapped_column(String, primary_key=True)
    parameter_group: Mapped[str] = mapped_column(String, primary_key=True)
    parameter_name: Mapped[str] = mapped_column(String, primary_key=True)
    parameter_value: Mapped[str] = mapped_column(String, nullable=False)
    parameter_json: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

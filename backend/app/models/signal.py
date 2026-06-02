from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Signal(Base):
    """Generated point-in-time model signal for a stock and horizon."""

    __tablename__ = "signals"
    __table_args__ = (
        Index("ix_signals_trade_date_rank", "trade_date", "horizon_days", "signal_rank"),
        Index("ix_signals_stock_date", "stock_id", "trade_date", "horizon_days"),
        Index("ix_signals_versions", "model_version", "feature_version"),
    )

    signal_id: Mapped[str] = mapped_column(String, primary_key=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    stock_id: Mapped[str] = mapped_column(String, ForeignKey("stock_master.stock_id", ondelete="CASCADE"), nullable=False)
    horizon_days: Mapped[int] = mapped_column(Integer, nullable=False)
    probability_up: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    bullish_score: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    risk_score: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    risk_adjusted_score: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    signal_rank: Mapped[Optional[int]] = mapped_column(Integer)
    selected_for_watchlist: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rejection_reason: Mapped[Optional[str]] = mapped_column(String)
    model_version: Mapped[str] = mapped_column(String, nullable=False)
    feature_version: Mapped[str] = mapped_column(String, nullable=False)


class SignalOutcome(Base):
    """Realized outcome for a generated signal after its holding window closes."""

    __tablename__ = "signal_outcomes"
    __table_args__ = (Index("ix_signal_outcomes_exit_date", "exit_date"),)

    signal_id: Mapped[str] = mapped_column(String, ForeignKey("signals.signal_id", ondelete="CASCADE"), primary_key=True)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    entry_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    exit_date: Mapped[date] = mapped_column(Date, nullable=False)
    exit_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    gross_return: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    net_return: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    benchmark_return: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 8))
    excess_return: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 8))
    win_absolute: Mapped[bool] = mapped_column(Boolean, nullable=False)
    win_relative: Mapped[Optional[bool]] = mapped_column(Boolean)
    hit_take_profit: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    hit_stop_loss: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    max_favorable_excursion: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 8))
    max_adverse_excursion: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 8))
    holding_days: Mapped[int] = mapped_column(Integer, nullable=False)


class SignalPerformanceStats(Base):
    """Aggregated win-rate and risk statistics by strategy segment."""

    __tablename__ = "signal_performance_stats"
    __table_args__ = (
        Index("ix_signal_performance_stats_lookup", "model_version", "strategy_version", "horizon_days"),
    )

    model_version: Mapped[str] = mapped_column(String, primary_key=True)
    strategy_version: Mapped[str] = mapped_column(String, primary_key=True)
    horizon_days: Mapped[int] = mapped_column(Integer, primary_key=True)
    market_regime: Mapped[str] = mapped_column(String, primary_key=True)
    industry: Mapped[str] = mapped_column(String, primary_key=True)
    probability_bucket: Mapped[str] = mapped_column(String, primary_key=True)
    risk_bucket: Mapped[str] = mapped_column(String, primary_key=True)
    trade_count: Mapped[int] = mapped_column(Integer, nullable=False)
    win_rate: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    win_rate_lower_bound: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    avg_net_return: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    median_net_return: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    profit_factor: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    max_drawdown: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    sharpe: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    calibration_error: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LabelsDaily(Base):
    """Point-in-time training/evaluation labels for stock signals."""

    __tablename__ = "labels_daily"
    __table_args__ = (
        Index("ix_labels_daily_lookup", "stock_id", "trade_date", "label_name", "label_version"),
        Index("ix_labels_daily_signal_time", "stock_id", "trade_date", "available_for_signal_at"),
    )

    trade_date: Mapped[date] = mapped_column(Date, primary_key=True)
    stock_id: Mapped[str] = mapped_column(String, ForeignKey("stock_master.stock_id", ondelete="CASCADE"), primary_key=True)
    label_name: Mapped[str] = mapped_column(String, primary_key=True)
    label_value: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    horizon_days: Mapped[int] = mapped_column(primary_key=True)
    label_version: Mapped[str] = mapped_column(String, primary_key=True)
    forward_return: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 8))
    benchmark_return: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 8))
    excess_return: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 8))
    max_favorable_excursion: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 8))
    max_adverse_excursion: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 8))
    transaction_cost: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False, default=0)
    minimum_excess_return: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False, default=0)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    available_for_signal_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class FeatureStoreDaily(Base):
    """Point-in-time daily factor features used by scoring and backtests."""

    __tablename__ = "feature_store_daily"
    __table_args__ = (
        Index("ix_feature_store_signal_time", "stock_id", "trade_date", "available_for_signal_at"),
        Index("ix_feature_store_feature_lookup", "feature_group", "feature_name", "feature_version"),
    )

    trade_date: Mapped[date] = mapped_column(Date, primary_key=True)
    stock_id: Mapped[str] = mapped_column(String, ForeignKey("stock_master.stock_id", ondelete="CASCADE"), primary_key=True)
    feature_group: Mapped[str] = mapped_column(String, primary_key=True)
    feature_name: Mapped[str] = mapped_column(String, primary_key=True)
    feature_value: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    feature_version: Mapped[str] = mapped_column(String, primary_key=True)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    available_for_signal_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

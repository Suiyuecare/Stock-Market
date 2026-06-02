from datetime import date, datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Date, DateTime, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DataAvailabilityLedger(Base):
    """Tracks when each dataset is safe to use for signal generation."""

    __tablename__ = "data_availability_ledger"
    __table_args__ = (
        UniqueConstraint("source", "dataset_name", "symbol", "data_date", "revision_number", name="uq_data_availability_revision"),
        Index("ix_data_availability_signal_time", "dataset_name", "symbol", "available_for_signal_at"),
        Index("ix_data_availability_source_date", "source", "dataset_name", "data_date"),
    )

    id: Mapped[str] = mapped_column(String, default=lambda: str(uuid4()), primary_key=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
    dataset_name: Mapped[str] = mapped_column(String, nullable=False)
    symbol: Mapped[Optional[str]] = mapped_column(String)
    data_date: Mapped[date] = mapped_column(Date, nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    available_for_signal_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    checksum: Mapped[Optional[str]] = mapped_column(String)
    raw_payload_path: Mapped[Optional[str]] = mapped_column(String)

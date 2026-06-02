from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class NewsEvent(Base):
    __tablename__ = "news_events"

    id: Mapped[str] = mapped_column(String, default=lambda: str(uuid4()), primary_key=True)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    market: Mapped[str] = mapped_column(String, nullable=False)
    stock_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("stock_master.stock_id", ondelete="SET NULL"))
    related_symbol: Mapped[Optional[str]] = mapped_column(String)
    related_industry: Mapped[Optional[str]] = mapped_column(String)
    source: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(String)
    sentiment_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    event_type: Mapped[Optional[str]] = mapped_column(String)
    impact_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))

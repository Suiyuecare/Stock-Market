from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.models.base import Base


class FactorScoresDaily(Base):
    __tablename__ = "factor_scores_daily"

    trade_date: Mapped[date] = mapped_column(Date, primary_key=True)
    stock_id: Mapped[str] = mapped_column(String, ForeignKey("stock_master.stock_id", ondelete="CASCADE"), primary_key=True)
    fundamental_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    chip_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    macro_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    technical_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    news_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    us_market_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    target_price_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    risk_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    bullish_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    risk_adjusted_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    probability_up_1d: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    probability_up_5d: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    probability_up_20d: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    top_positive_factors: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    top_negative_factors: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    top_risk_factors: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))

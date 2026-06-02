from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TechnicalIndicatorsDaily(Base):
    __tablename__ = "technical_indicators_daily"

    trade_date: Mapped[date] = mapped_column(Date, primary_key=True)
    stock_id: Mapped[str] = mapped_column(String, ForeignKey("stock_master.stock_id", ondelete="CASCADE"), primary_key=True)
    ma5: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
    ma20: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
    ma60: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
    rsi14: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    k_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    d_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    ema12: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
    ema26: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
    dif: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
    dea: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
    macd_hist: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
    macd_bar_tw: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
    obv: Mapped[Optional[Decimal]] = mapped_column(Numeric(24, 4))
    volume_ma5: Mapped[Optional[Decimal]] = mapped_column(Numeric(24, 4))
    volume_ma20: Mapped[Optional[Decimal]] = mapped_column(Numeric(24, 4))
    bearish_volume_divergence: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    bullish_volume_divergence: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    volume_price_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    macd_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    technical_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))

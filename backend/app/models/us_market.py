from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


@dataclass(frozen=True)
class USMarketDaily:
    """Domain model for US market inputs that affect Taiwan stocks."""

    trade_date: date
    symbol: str
    symbol_type: str
    close: float
    return_1d: float
    volume: Optional[float] = None
    ma20: Optional[float] = None
    ma60: Optional[float] = None
    rsi14: Optional[float] = None
    dif: Optional[float] = None
    dea: Optional[float] = None
    macd_hist: Optional[float] = None
    volume_price_signal: Optional[float] = None


class USMarketDailyORM(Base):
    __tablename__ = "us_market_daily"

    trade_date: Mapped[date] = mapped_column(Date, primary_key=True)
    symbol: Mapped[str] = mapped_column(String, primary_key=True)
    symbol_type: Mapped[str] = mapped_column(String, nullable=False)
    open: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
    high: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
    low: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
    close: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    volume: Mapped[Optional[int]] = mapped_column(BigInteger)
    return_1d: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    ma20: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
    ma60: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
    rsi14: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    dif: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
    dea: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
    macd_hist: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
    volume_price_signal: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))

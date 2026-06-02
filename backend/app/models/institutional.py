from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


@dataclass(frozen=True)
class InstitutionalTradingDay:
    """Domain model for one day of Taiwan institutional trading flow."""

    trade_date: date
    stock_id: str
    foreign_net: float
    investment_trust_net: float
    dealer_net: float
    dealer_self_net: float
    dealer_hedge_net: float
    total_institutional_net: float
    volume: float
    close: float
    ma20: Optional[float] = None


class InstitutionalTradingDaily(Base):
    __tablename__ = "institutional_trading_daily"

    trade_date: Mapped[date] = mapped_column(Date, primary_key=True)
    stock_id: Mapped[str] = mapped_column(String, ForeignKey("stock_master.stock_id", ondelete="CASCADE"), primary_key=True)
    foreign_net: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    investment_trust_net: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    dealer_net: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    dealer_self_net: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    dealer_hedge_net: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    total_institutional_net: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    foreign_net_ratio: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    investment_trust_net_ratio: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    dealer_net_ratio: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))

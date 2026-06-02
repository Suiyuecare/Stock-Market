from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class FundamentalMonthly(Base):
    __tablename__ = "fundamental_monthly"

    data_month: Mapped[date] = mapped_column(Date, primary_key=True)
    stock_id: Mapped[str] = mapped_column(String, ForeignKey("stock_master.stock_id", ondelete="CASCADE"), primary_key=True)
    revenue: Mapped[Optional[Decimal]] = mapped_column(Numeric(24, 4))
    revenue_mom: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    revenue_yoy: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    revenue_acc_yoy: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))


class FundamentalQuarterly(Base):
    __tablename__ = "fundamental_quarterly"

    fiscal_year: Mapped[int] = mapped_column(Integer, primary_key=True)
    quarter: Mapped[int] = mapped_column(Integer, primary_key=True)
    stock_id: Mapped[str] = mapped_column(String, ForeignKey("stock_master.stock_id", ondelete="CASCADE"), primary_key=True)
    eps: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4))
    gross_margin: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    operating_margin: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    net_margin: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    debt_ratio: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    operating_cash_flow: Mapped[Optional[Decimal]] = mapped_column(Numeric(24, 4))
    inventory: Mapped[Optional[Decimal]] = mapped_column(Numeric(24, 4))
    accounts_receivable: Mapped[Optional[Decimal]] = mapped_column(Numeric(24, 4))

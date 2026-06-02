from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


@dataclass(frozen=True)
class USTWSupplyChainMapping:
    """Sensitivity mapping between US companies/themes and Taiwan stocks."""

    us_ticker: str
    us_company_name: str
    tw_stock_id: str
    tw_stock_name: str
    relation_type: str
    supply_chain_tag: str
    sensitivity_weight: float
    impact_lag_days: int = 0
    confidence: float = 0.5


class USTWSupplyChainMap(Base):
    __tablename__ = "us_tw_supply_chain_map"

    us_ticker: Mapped[str] = mapped_column(String, primary_key=True)
    us_company_name: Mapped[str] = mapped_column(String, nullable=False)
    tw_stock_id: Mapped[str] = mapped_column(String, ForeignKey("stock_master.stock_id", ondelete="CASCADE"), primary_key=True)
    tw_stock_name: Mapped[str] = mapped_column(String, nullable=False)
    relation_type: Mapped[str] = mapped_column(String, primary_key=True)
    supply_chain_tag: Mapped[str] = mapped_column(String, primary_key=True)
    sensitivity_weight: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False, default=0)
    impact_lag_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    confidence: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False, default=0)

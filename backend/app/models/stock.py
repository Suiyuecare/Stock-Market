from typing import Optional

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.models.base import Base


class StockMaster(Base):
    __tablename__ = "stock_master"

    stock_id: Mapped[str] = mapped_column(String, primary_key=True)
    stock_name: Mapped[str] = mapped_column(String, nullable=False)
    market_type: Mapped[str] = mapped_column(String, nullable=False)
    industry: Mapped[Optional[str]] = mapped_column(String)
    sub_industry: Mapped[Optional[str]] = mapped_column(String)
    supply_chain_tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    is_listed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_otc: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

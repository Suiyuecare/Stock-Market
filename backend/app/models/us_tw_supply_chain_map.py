from dataclasses import dataclass


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

from app.services.factor_weight_profiles import FactorWeightProfileService


def test_factor_weight_profiles_match_manual_mvp_formulas() -> None:
    catalog = FactorWeightProfileService().catalog()

    assert catalog.general_tw_stock.factor_weights["fundamental"] == 0.20
    assert catalog.general_tw_stock.factor_weights["us_market"] == 0.15
    assert catalog.general_tw_stock.risk_score_weight == 0.35
    assert catalog.electronics_semiconductor_ai.factor_weights["us_market"] == 0.25
    assert catalog.domestic_traditional_construction.factor_weights["us_market"] == 0.05
    assert catalog.bear_or_high_volatility.risk_score_weight == 0.55


def test_factor_weight_profile_selection_uses_stock_profile_and_market_regime() -> None:
    service = FactorWeightProfileService()

    electronics = service.select_profile({"industry": "semiconductor", "supply_chain_tags": ["ai_server"]})
    domestic = service.select_profile({"industry": "construction", "supply_chain_tags": ["domestic_demand"]})
    bear = service.select_profile(
        {"industry": "semiconductor"},
        {"primary_regime": "bear_market", "active_regimes": ["high_volatility"]},
    )

    assert electronics.name == "electronics_semiconductor_ai"
    assert domestic.name == "domestic_traditional_construction"
    assert bear.name == "bear_or_high_volatility"

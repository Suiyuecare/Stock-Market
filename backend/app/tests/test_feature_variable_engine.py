from app.schemas import ChipFeatureInput, FundamentalFeatureInput
from app.services.feature_variable_engine import FeatureVariableEngine


def test_fundamental_features_include_raw_and_derived_variables() -> None:
    result = FeatureVariableEngine().fundamental_features(
        FundamentalFeatureInput(
            revenue_yoy=0.12,
            revenue_mom=0.03,
            previous_revenue_yoy=-0.04,
            revenue_yoy_history_3m=[0.08, 0.1, 0.12],
            eps_yoy=0.15,
            eps_qoq=0.04,
            gross_margin_delta_qoq=0.02,
            gross_margin_delta_yoy=0.03,
            operating_margin_delta=0.01,
            debt_ratio=0.28,
            operating_cash_flow_quality=0.8,
            inventory_growth_vs_revenue_growth=-0.02,
            accounts_receivable_growth_vs_revenue_growth=0.01,
            industry_growth_score=72,
        )
    )

    assert result.feature_group == "fundamental"
    assert result.features["revenue_yoy"] == 0.12
    assert result.features["revenue_yoy_acceleration"] == 0.16
    assert result.features["revenue_3m_yoy_avg"] == 0.1
    assert result.features["fundamental_turnaround"] == 100.0
    assert result.features["quality_growth"] > 0


def test_quality_growth_requires_revenue_margin_and_cash_flow_alignment() -> None:
    weak = FeatureVariableEngine().fundamental_features(
        FundamentalFeatureInput(
            revenue_yoy=-0.05,
            gross_margin_delta_qoq=-0.01,
            gross_margin_delta_yoy=-0.02,
            operating_cash_flow_quality=-0.2,
        )
    )
    strong = FeatureVariableEngine().fundamental_features(
        FundamentalFeatureInput(
            revenue_yoy=0.2,
            gross_margin_delta_qoq=0.03,
            operating_cash_flow_quality=0.9,
        )
    )

    assert weak.features["quality_growth"] == 0
    assert strong.features["quality_growth"] > weak.features["quality_growth"]


def test_chip_features_include_institutional_and_tdcc_variables() -> None:
    result = FeatureVariableEngine().chip_features(
        ChipFeatureInput(
            foreign_net_ratio=0.03,
            investment_trust_net_ratio=0.02,
            dealer_net_ratio=0.0,
            institutional_net_ratio=0.055,
            foreign_consecutive_buy_days=5,
            trust_consecutive_buy_days=4,
            dealer_consecutive_buy_days=1,
            institutional_sync_buy=True,
            foreign_reversal_to_buy=True,
            trust_accumulation_score=78,
            dealer_hedge_pressure=0.05,
            tdcc_large_holder_ratio=0.62,
            tdcc_large_holder_ratio_delta=0.02,
            margin_balance_delta=0.01,
            short_interest_delta=-0.01,
            borrow_sell_balance_delta=-0.02,
        )
    )

    assert result.feature_group == "chip"
    assert result.features["foreign_net_ratio"] == 0.03
    assert result.features["institutional_sync_buy"] == 1.0
    assert result.features["foreign_reversal_to_buy"] == 1.0
    assert result.features["chip_alignment_score"] > 90


def test_chip_alignment_penalizes_sync_sell_and_hedge_pressure() -> None:
    aligned = FeatureVariableEngine().chip_features(
        ChipFeatureInput(
            foreign_net_ratio=0.03,
            investment_trust_net_ratio=0.02,
            dealer_net_ratio=0.01,
            institutional_net_ratio=0.05,
            tdcc_large_holder_ratio_delta=0.01,
        )
    )
    weak = FeatureVariableEngine().chip_features(
        ChipFeatureInput(
            foreign_net_ratio=-0.03,
            investment_trust_net_ratio=-0.02,
            dealer_net_ratio=-0.01,
            institutional_net_ratio=-0.05,
            institutional_sync_sell=True,
            dealer_hedge_pressure=0.2,
            tdcc_large_holder_ratio_delta=-0.01,
        )
    )

    assert aligned.features["chip_alignment_score"] == 100.0
    assert weak.features["chip_alignment_score"] == 0.0

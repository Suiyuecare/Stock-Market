from app.schemas import ChipFeatureInput, FeatureVectorResult, FundamentalFeatureInput


def test_fundamental_feature_input_schema_tracks_required_variables() -> None:
    inputs = FundamentalFeatureInput(
        revenue_yoy=0.12,
        revenue_mom=0.03,
        previous_revenue_yoy=-0.04,
        revenue_yoy_history_3m=[0.08, 0.1, 0.12],
        eps_yoy=0.15,
        eps_qoq=0.04,
    )

    assert inputs.revenue_yoy == 0.12
    assert inputs.revenue_yoy_history_3m == [0.08, 0.1, 0.12]


def test_chip_feature_input_schema_tracks_required_variables() -> None:
    inputs = ChipFeatureInput(
        foreign_net_ratio=0.03,
        investment_trust_net_ratio=0.02,
        dealer_net_ratio=0.01,
        institutional_net_ratio=0.06,
        tdcc_large_holder_ratio=0.62,
        margin_balance_delta=0.01,
    )

    assert inputs.institutional_net_ratio == 0.06
    assert inputs.tdcc_large_holder_ratio == 0.62


def test_feature_vector_result_schema_can_feed_feature_store() -> None:
    result = FeatureVectorResult(
        feature_group="fundamental",
        feature_version="feature-v1",
        features={"revenue_yoy": 0.12, "quality_growth": 80.0},
    )

    assert result.feature_group == "fundamental"
    assert result.features["quality_growth"] == 80.0

from app.schemas import MarketRegimeInput, MarketRegimeResult


def test_market_regime_input_schema_tracks_required_market_features() -> None:
    inputs = MarketRegimeInput(
        tw_index_return_20d=0.06,
        tw_index_return_60d=0.12,
        tw_index_above_ma60=True,
        volatility_percentile=0.2,
        foreign_net_flow_20d=0.05,
        nasdaq_return_20d=0.06,
        sox_return_20d=0.08,
        vix_change_20d=-0.04,
        tsm_adr_return_20d=0.05,
    )

    assert inputs.tw_index_above_ma60 is True
    assert inputs.sox_return_20d == 0.08


def test_market_regime_result_schema_returns_weight_guidance() -> None:
    result = MarketRegimeResult(
        primary_regime="bull_market",
        active_regimes=["bull_market", "foreign_inflow"],
        factor_weight_adjustments={"chip": 1.2, "technical": 1.1},
        risk_weight_multiplier=0.9,
        confidence=0.8,
        explanations=["Foreign flow and trend are supportive."],
    )

    assert result.primary_regime == "bull_market"
    assert result.factor_weight_adjustments["chip"] == 1.2

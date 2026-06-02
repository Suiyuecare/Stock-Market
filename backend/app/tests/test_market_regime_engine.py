from app.schemas import MarketRegimeInput
from app.services.market_regime_engine import MarketRegimeEngine, adjusted_factor_weights
from app.services.scoring.final_prediction_score import calculate_final_prediction_score


def test_market_regime_engine_detects_bull_foreign_inflow_and_us_tech_strength() -> None:
    result = MarketRegimeEngine().evaluate(
        MarketRegimeInput(
            tw_index_return_20d=0.06,
            tw_index_return_60d=0.12,
            tw_index_above_ma60=True,
            volatility_percentile=0.2,
            foreign_net_flow_20d=0.05,
            nasdaq_return_20d=0.06,
            sox_return_20d=0.08,
            tsm_adr_return_20d=0.05,
        )
    )

    assert result.primary_regime == "bull_market"
    assert "foreign_inflow" in result.active_regimes
    assert "us_tech_strong" in result.active_regimes
    assert result.factor_weight_adjustments["chip"] > 1
    assert result.factor_weight_adjustments["us_market"] > 1
    assert result.risk_weight_multiplier < 1


def test_market_regime_engine_detects_bear_high_volatility_foreign_outflow() -> None:
    result = MarketRegimeEngine().evaluate(
        MarketRegimeInput(
            tw_index_return_20d=-0.08,
            tw_index_return_60d=-0.14,
            tw_index_above_ma60=False,
            volatility_percentile=0.9,
            foreign_net_flow_20d=-0.06,
            nasdaq_return_20d=-0.04,
            sox_return_20d=-0.07,
            tsm_adr_return_20d=-0.05,
            vix_change_20d=0.22,
        )
    )

    assert result.primary_regime == "bear_market"
    assert "high_volatility" in result.active_regimes
    assert "foreign_outflow" in result.active_regimes
    assert "us_tech_weak" in result.active_regimes
    assert result.risk_weight_multiplier > 1.7
    assert result.factor_weight_adjustments["us_market"] < 1


def test_market_regime_engine_detects_range_market() -> None:
    result = MarketRegimeEngine().evaluate(
        MarketRegimeInput(
            tw_index_return_20d=0.005,
            tw_index_return_60d=-0.002,
            tw_index_above_ma60=True,
            volatility_percentile=0.5,
        )
    )

    assert result.primary_regime == "range_market"
    assert result.factor_weight_adjustments["technical"] > 1
    assert result.risk_weight_multiplier > 1


def test_adjusted_factor_weights_keep_total_weight_at_one() -> None:
    weights = adjusted_factor_weights(
        {"technical": 0.5, "risk": 0.5},
        {"technical": 1.5, "risk": 0.5},
    )

    assert round(sum(weights.values()), 6) == 1.0
    assert weights["technical"] > weights["risk"]


def test_final_prediction_score_can_use_market_regime_adjustments() -> None:
    regime = MarketRegimeEngine().evaluate(
        MarketRegimeInput(
            tw_index_return_20d=-0.08,
            tw_index_return_60d=-0.14,
            tw_index_above_ma60=False,
            volatility_percentile=0.9,
            foreign_net_flow_20d=-0.06,
        )
    )
    payload = calculate_final_prediction_score(
        {
            "fundamental": {"score": 70, "confidence": 80},
            "chip": {"score": 65, "confidence": 70},
            "technical": {"score": 68, "confidence": 70},
            "us_market": {"score": 60, "confidence": 70},
            "news": {"score": 55, "confidence": 60},
            "macro": {"score": 50, "confidence": 60},
            "target_price": {"score": 50, "confidence": 50},
            "liquidity": {"score": 60, "confidence": 60},
        },
        risk_score=70,
        market_regime=regime,
    )

    assert payload["explanation"]["market_regime"] == "bear_market"
    assert payload["explanation"]["risk_score_weight"] == 0.55
    assert payload["RiskAdjustedScore"] < payload["BullishScore"]

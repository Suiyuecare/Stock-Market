from app.services.data_providers.mock_provider import TW_INSTRUMENTS, get_mock_us_linkage
from app.services.scoring.final_prediction_score import build_all_signals, build_signal, calculate_final_prediction_score, probability_from_score
from app.services.scoring.us_market_score import us_linkage_score


def test_probability_from_score_is_bounded() -> None:
    assert probability_from_score(10) == 1
    assert probability_from_score(-10) == 0
    assert probability_from_score(0) == 0.5


def test_us_linkage_score_has_expected_direction() -> None:
    score = us_linkage_score(get_mock_us_linkage())
    assert score > 0
    assert score <= 1


def test_final_prediction_score_formula_and_probabilities() -> None:
    payload = calculate_final_prediction_score(
        {
            "fundamental": {"score": 80, "confidence": 80},
            "chip": {"score": 70, "confidence": 70},
            "technical": {"score": 60, "confidence": 60},
            "us_market": {"score": 75, "confidence": 75},
            "news": {"score": 55, "confidence": 55},
            "macro": {"score": 50, "confidence": 50},
            "target_price": {"score": 50, "confidence": 40},
            "liquidity": {"score": 65, "confidence": 65},
        },
        risk_score=30,
    )

    assert payload["BullishScore"] == 66.4
    assert payload["RiskAdjustedScore"] == 55.9
    assert 0 <= payload["probability_up_1d"] <= 1
    assert payload["probability_up_5d"] >= payload["probability_up_1d"]
    assert payload["probability_up_20d"] >= payload["probability_up_5d"]
    assert payload["confidence"] == 61.875
    assert payload["explanation"]["component_scores"]["fundamental"] == 80
    assert payload["explanation"]["factor_weight_profile"] == "general_tw_stock"
    assert payload["explanation"]["risk_score_weight"] == 0.35


def test_final_prediction_score_normalizes_legacy_payloads() -> None:
    payload = calculate_final_prediction_score(
        {
            "fundamental": {"score": 0.72, "confidence": 0.58},
            "chip": {"score": 0.64, "confidence": 0.7},
            "technical": {"score": 62, "confidence": 72},
            "us_market": {"score": 58, "confidence": 70},
            "news": {"score": -0.2, "confidence": 0.5},
            "macro": {"score": 0.05, "confidence": 0.35},
            "target_price": {"score": 0, "confidence": 0.2},
            "liquidity": {"score": 0.7, "confidence": 0.6},
        },
        risk_score=0.4,
    )

    assert payload["explanation"]["component_scores"]["fundamental"] == 72
    assert payload["explanation"]["component_scores"]["news"] == 40
    assert payload["RiskScore"] == 40
    assert payload["RiskAdjustedScore"] < payload["BullishScore"]


def test_build_signal_contract() -> None:
    signal = build_signal(TW_INSTRUMENTS[0])
    assert signal.symbol == "2330"
    assert 0 <= signal.probability_up <= 1
    assert signal.probability_up == signal.probability_up_1d
    assert 0 <= signal.probability_up_5d <= 1
    assert 0 <= signal.probability_up_20d <= 1
    assert 0 <= signal.confidence <= 1
    assert signal.bullish_score is not None
    assert signal.risk_adjusted_score is not None
    assert signal.explanation is not None
    assert 0 <= signal.risk_score.total <= 1
    assert len(signal.factor_scores) >= 5
    assert len(signal.positive_drivers) >= 1
    assert len(signal.news) >= 1


def test_build_all_signals_sorted_source_count() -> None:
    signals = build_all_signals()
    assert len(signals) == len(TW_INSTRUMENTS)


def test_final_prediction_score_uses_electronics_weight_profile() -> None:
    payload = calculate_final_prediction_score(
        {
            "fundamental": 50,
            "chip": 50,
            "technical": 50,
            "us_market": 100,
            "news": 50,
            "macro": 50,
            "target_price": 50,
            "liquidity": 50,
        },
        risk_score=0,
        stock_profile={"industry": "semiconductor", "supply_chain_tags": ["ai_server"]},
    )

    assert payload["explanation"]["factor_weight_profile"] == "electronics_semiconductor_ai"
    assert payload["explanation"]["factor_weights"]["us_market"] == 0.25
    assert payload["BullishScore"] == 62.5


def test_final_prediction_score_uses_bear_market_risk_weight() -> None:
    payload = calculate_final_prediction_score(
        {
            "fundamental": 70,
            "chip": 70,
            "technical": 70,
            "us_market": 70,
            "news": 70,
            "macro": 70,
            "target_price": 70,
            "liquidity": 70,
        },
        risk_score=60,
        market_regime={"primary_regime": "bear_market", "active_regimes": ["high_volatility"]},
    )

    assert payload["explanation"]["factor_weight_profile"] == "bear_or_high_volatility"
    assert payload["explanation"]["risk_score_weight"] == 0.55
    assert payload["RiskAdjustedScore"] == 23

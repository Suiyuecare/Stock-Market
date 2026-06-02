from app.services.data_providers.mock_provider import TW_INSTRUMENTS, get_mock_us_linkage
from app.services.scoring.final_prediction_score import build_all_signals, build_signal, probability_from_score
from app.services.scoring.us_market_score import us_linkage_score


def test_probability_from_score_is_bounded() -> None:
    assert probability_from_score(10) == 1
    assert probability_from_score(-10) == 0
    assert probability_from_score(0) == 0.5


def test_us_linkage_score_has_expected_direction() -> None:
    score = us_linkage_score(get_mock_us_linkage())
    assert score > 0
    assert score <= 1


def test_build_signal_contract() -> None:
    signal = build_signal(TW_INSTRUMENTS[0])
    assert signal.symbol == "2330"
    assert 0 <= signal.probability_up <= 1
    assert 0 <= signal.confidence <= 1
    assert 0 <= signal.risk_score.total <= 1
    assert len(signal.factor_scores) >= 5
    assert len(signal.positive_drivers) >= 1
    assert len(signal.news) >= 1


def test_build_all_signals_sorted_source_count() -> None:
    signals = build_all_signals()
    assert len(signals) == len(TW_INSTRUMENTS)

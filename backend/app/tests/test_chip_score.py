from datetime import date, timedelta

from app.services.scoring.chip_score import calculate_chip_score, calculate_chip_score_from_observations


def _row(day: int, foreign: float, trust: float, dealer: float, close: float = 105, ma20: float = 100) -> dict:
    total = foreign + trust + dealer
    return {
        "trade_date": date(2026, 1, 1) + timedelta(days=day),
        "stock_id": "2330",
        "foreign_net": foreign,
        "investment_trust_net": trust,
        "dealer_net": dealer,
        "dealer_self_net": dealer * 0.5,
        "dealer_hedge_net": dealer * 0.5,
        "total_institutional_net": total,
        "volume": 10000,
        "close": close,
        "ma20": ma20,
    }


def test_chip_score_contract_for_mock_symbol() -> None:
    payload = calculate_chip_score("2330")

    for key in ["score", "positive_factors", "negative_factors", "risk_factors", "confidence"]:
        assert key in payload
    assert 0 <= payload["score"] <= 100
    assert payload["score"] > 50
    assert payload["foreign_net_ratio"] > 0


def test_foreign_three_and_five_day_buying_rules() -> None:
    three_day_payload = calculate_chip_score_from_observations(
        [_row(0, -100, 0, 0), _row(1, 100, 0, 0), _row(2, 120, 0, 0), _row(3, 140, 0, 0)]
    )
    five_day_payload = calculate_chip_score_from_observations([_row(index, 100 + index, 0, 0) for index in range(5)])

    assert three_day_payload["consecutive_foreign_net_buy_days"] == 3
    assert "foreign net buying for 3 consecutive days" in three_day_payload["positive_factors"]
    assert five_day_payload["consecutive_foreign_net_buy_days"] == 5
    assert "foreign net buying for 5 consecutive days" in five_day_payload["positive_factors"]
    assert five_day_payload["score"] > three_day_payload["score"]


def test_investment_trust_five_day_accumulation_is_strong_positive() -> None:
    payload = calculate_chip_score_from_observations([_row(index, 0, 220 + index, 0) for index in range(5)])

    assert payload["consecutive_investment_trust_net_buy_days"] == 5
    assert "investment trust net buying for 5 consecutive days" in payload["positive_factors"]
    assert payload["score"] > 60


def test_simultaneous_foreign_and_trust_buying() -> None:
    payload = calculate_chip_score_from_observations([_row(0, 500, 300, -10)])

    assert "foreign and investment trust simultaneous net buying" in payload["positive_factors"]
    assert payload["institutional_net_ratio"] > 0


def test_all_three_institutions_selling_is_negative() -> None:
    payload = calculate_chip_score_from_observations([_row(0, -500, -300, -200)])

    assert "all three institutions net selling" in payload["negative_factors"]
    assert "synchronized institutional selling" in payload["risk_factors"]
    assert payload["synchronized_institutional_selling"] is True
    assert payload["score"] < 50


def test_trust_selling_below_ma20_is_strong_negative() -> None:
    payload = calculate_chip_score_from_observations([_row(index, 0, -250, 0, close=90, ma20=100) for index in range(4)])

    assert "investment trust continuous selling" in payload["negative_factors"]
    assert "investment trust continuous selling while price is below MA20" in payload["risk_factors"]
    assert payload["score"] < 40


def test_foreign_buying_but_trust_selling_conflict() -> None:
    payload = calculate_chip_score_from_observations([_row(0, 700, -500, 50)])

    assert "foreign buying but investment trust selling" in payload["negative_factors"]


def test_institutional_reversal_from_buying_to_selling() -> None:
    payload = calculate_chip_score_from_observations(
        [_row(0, 200, 100, 50), _row(1, 220, 100, 50), _row(2, 240, 100, 50), _row(3, -900, -200, -100)]
    )

    assert "institutional reversal from buying to selling" in payload["risk_factors"]
    assert payload["score"] < 50


def test_ratios_are_normalized_by_volume() -> None:
    payload = calculate_chip_score_from_observations([_row(0, 1000, 500, 250)])

    assert payload["foreign_net_ratio"] == 0.1
    assert payload["investment_trust_net_ratio"] == 0.05
    assert payload["dealer_net_ratio"] == 0.025
    assert payload["institutional_net_ratio"] == 0.175

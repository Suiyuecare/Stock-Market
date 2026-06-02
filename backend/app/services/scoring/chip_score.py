from datetime import date, timedelta
from typing import Iterable, List, Mapping, Sequence, Union

from app.models.institutional import InstitutionalTradingDay
from app.services.scoring.common import ScorePayload, scoring_payload

InstitutionalInput = Union[InstitutionalTradingDay, Mapping[str, object]]


def _value(record: InstitutionalInput, field: str, default: float = 0.0) -> float:
    if isinstance(record, Mapping):
        value = record.get(field, default)
    else:
        value = getattr(record, field, default)
    if value is None:
        return default
    return float(value)


def _date_value(record: InstitutionalInput) -> date:
    if isinstance(record, Mapping):
        value = record.get("trade_date")
    else:
        value = record.trade_date
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _with_total(record: InstitutionalInput) -> dict:
    foreign_net = _value(record, "foreign_net")
    investment_trust_net = _value(record, "investment_trust_net")
    dealer_net = _value(record, "dealer_net")
    total = _value(record, "total_institutional_net", foreign_net + investment_trust_net + dealer_net)
    return {
        "trade_date": _date_value(record),
        "stock_id": str(record.get("stock_id", "")) if isinstance(record, Mapping) else record.stock_id,
        "foreign_net": foreign_net,
        "investment_trust_net": investment_trust_net,
        "dealer_net": dealer_net,
        "dealer_self_net": _value(record, "dealer_self_net"),
        "dealer_hedge_net": _value(record, "dealer_hedge_net"),
        "total_institutional_net": total,
        "volume": max(_value(record, "volume"), 0.0),
        "close": _value(record, "close"),
        "ma20": _value(record, "ma20", 0.0),
    }


def _ratio(numerator: float, volume: float) -> float:
    if volume <= 0:
        return 0.0
    return numerator / volume


def _consecutive_days(records: Sequence[dict], field: str, positive: bool = True) -> int:
    count = 0
    for record in reversed(records):
        value = float(record[field])
        if positive and value > 0:
            count += 1
        elif not positive and value < 0:
            count += 1
        else:
            break
    return count


def _mock_institutional_series(symbol: str) -> List[InstitutionalTradingDay]:
    today = date.today()
    templates = {
        "2330": [900, 1200, 1600, 1800, 2100, 2400],
        "2454": [300, -200, 500, 700, 800, 900],
        "2317": [500, 200, -300, -800, -1200, -1500],
        "2308": [-200, 100, 300, 450, 600, 720],
    }
    foreign_values = templates.get(symbol, [0, 100, 120, 80, 60, 90])
    observations: List[InstitutionalTradingDay] = []
    for index, foreign_net in enumerate(foreign_values):
        investment_trust_net = 600 if symbol == "2330" else 160 if foreign_net > 0 else -220
        dealer_net = 120 if foreign_net > 0 else -120
        total = foreign_net + investment_trust_net + dealer_net
        close = 100 + index * 2
        observations.append(
            InstitutionalTradingDay(
                trade_date=today - timedelta(days=len(foreign_values) - index),
                stock_id=symbol,
                foreign_net=foreign_net,
                investment_trust_net=investment_trust_net,
                dealer_net=dealer_net,
                dealer_self_net=dealer_net * 0.45,
                dealer_hedge_net=dealer_net * 0.55,
                total_institutional_net=total,
                volume=12000,
                close=close,
                ma20=close - 3,
            )
        )
    return observations


def calculate_chip_score_from_observations(observations: Iterable[InstitutionalInput]) -> ScorePayload:
    records = sorted((_with_total(record) for record in observations), key=lambda item: item["trade_date"])
    if not records:
        return scoring_payload(score=0, risk_factors=["missing institutional trading observations"], confidence=0)

    latest = records[-1]
    volume = latest["volume"]
    foreign_net_ratio = _ratio(latest["foreign_net"], volume)
    investment_trust_net_ratio = _ratio(latest["investment_trust_net"], volume)
    dealer_net_ratio = _ratio(latest["dealer_net"], volume)
    institutional_net_ratio = _ratio(latest["total_institutional_net"], volume)
    consecutive_foreign_buy = _consecutive_days(records, "foreign_net", positive=True)
    consecutive_trust_buy = _consecutive_days(records, "investment_trust_net", positive=True)
    consecutive_trust_sell = _consecutive_days(records, "investment_trust_net", positive=False)

    positives: List[str] = []
    negatives: List[str] = []
    risks: List[str] = []
    score = 50.0

    ratio_boost = max(-20.0, min(20.0, institutional_net_ratio * 250))
    score += ratio_boost
    if institutional_net_ratio > 0:
        positives.append("institutional net buying normalized by volume")
    elif institutional_net_ratio < 0:
        negatives.append("institutional net selling normalized by volume")

    if consecutive_foreign_buy >= 5:
        score += 14
        positives.append("foreign net buying for 5 consecutive days")
    elif consecutive_foreign_buy >= 3:
        score += 8
        positives.append("foreign net buying for 3 consecutive days")

    if consecutive_trust_buy >= 5:
        score += 14
        positives.append("investment trust net buying for 5 consecutive days")
    elif consecutive_trust_buy >= 3:
        score += 7
        positives.append("investment trust accumulation")

    synchronized_buying = latest["foreign_net"] > 0 and latest["investment_trust_net"] > 0 and latest["dealer_net"] > 0
    synchronized_selling = latest["foreign_net"] < 0 and latest["investment_trust_net"] < 0 and latest["dealer_net"] < 0
    if synchronized_buying:
        score += 12
        positives.append("foreign, investment trust, and dealer simultaneous net buying")
    elif latest["foreign_net"] > 0 and latest["investment_trust_net"] > 0:
        score += 9
        positives.append("foreign and investment trust simultaneous net buying")

    if synchronized_selling:
        score -= 16
        negatives.append("all three institutions net selling")
        risks.append("synchronized institutional selling")

    if latest["foreign_net"] > 0 and latest["investment_trust_net"] < 0:
        score -= 5
        negatives.append("foreign buying but investment trust selling")

    below_ma20 = latest["ma20"] > 0 and latest["close"] < latest["ma20"]
    if consecutive_trust_sell >= 3:
        negatives.append("investment trust continuous selling")
        score -= 7
    if consecutive_trust_sell >= 3 and below_ma20:
        score -= 11
        risks.append("investment trust continuous selling while price is below MA20")

    if len(records) >= 4:
        previous_total = sum(record["total_institutional_net"] for record in records[-4:-1])
        if previous_total > 0 and latest["total_institutional_net"] < 0:
            score -= 10
            risks.append("institutional reversal from buying to selling")

    confidence = min(100.0, 45.0 + len(records) * 8.0)
    payload = scoring_payload(
        score=max(0.0, min(100.0, score)),
        positive_factors=positives,
        negative_factors=negatives,
        risk_factors=risks,
        confidence=confidence,
    )
    payload.update(
        {
            "foreign_net_ratio": round(foreign_net_ratio, 6),
            "investment_trust_net_ratio": round(investment_trust_net_ratio, 6),
            "dealer_net_ratio": round(dealer_net_ratio, 6),
            "institutional_net_ratio": round(institutional_net_ratio, 6),
            "consecutive_foreign_net_buy_days": consecutive_foreign_buy,
            "consecutive_investment_trust_net_buy_days": consecutive_trust_buy,
            "synchronized_institutional_buying": synchronized_buying,
            "synchronized_institutional_selling": synchronized_selling,
        }
    )
    return payload


def calculate_chip_score(symbol_or_observations: Union[str, Iterable[InstitutionalInput]]) -> ScorePayload:
    if isinstance(symbol_or_observations, str):
        return calculate_chip_score_from_observations(_mock_institutional_series(symbol_or_observations))
    return calculate_chip_score_from_observations(symbol_or_observations)

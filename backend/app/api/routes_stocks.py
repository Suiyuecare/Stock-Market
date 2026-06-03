from functools import lru_cache
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from app.schemas import MarketSummary, RankingResponse, StockDetailResponse, TechnicalIndicators
from app.services.market_data import get_market_summary, get_prediction_signals
from app.services.scoring import DISCLAIMER
from app.services.data_providers.mock_provider import TW_INSTRUMENTS, get_mock_news, get_mock_price_series
from app.services.data_providers.public_provider import PublicMarketDataProvider, unique_instruments
from app.services.indicators import build_technical_indicators
from app.services.scoring.chip_score import calculate_chip_score
from app.services.scoring.final_prediction_score import build_signal
from app.services.scoring.technical_score import calculate_technical_score

router = APIRouter()

RECOMMENDATION_COVERAGE_SYMBOLS = [
    "2330", "2454", "3035", "3661", "2382", "3231", "6669", "2317", "2308", "2345",
    "3017", "3324", "2383", "3037", "8046", "3711", "1590", "2049", "2359", "1504",
    "1513", "1519", "1605", "2603", "2609", "2615", "2618", "2610", "2634", "2881",
    "2882", "2884", "2885", "2886", "2891", "5880", "5876", "1216", "2912", "2207",
    "6505", "1301", "1303", "2002", "6446", "5871", "4904", "3008", "2408", "2357",
]

THEME_FIT_BY_SYMBOL = {
    "2330": 88, "2454": 82, "3035": 80, "3661": 84, "2382": 86, "3231": 84, "6669": 86,
    "2317": 78, "2308": 82, "2345": 80, "3017": 82, "3324": 80, "2383": 82, "3037": 78,
    "8046": 76, "3711": 78, "1590": 82, "2049": 82, "2359": 78, "1504": 76, "1513": 78,
    "1519": 80, "1605": 72, "2603": 74, "2609": 72, "2615": 70, "2618": 72, "2610": 70,
    "2634": 68, "2881": 78, "2882": 78, "2884": 76, "2885": 74, "2886": 78, "2891": 78,
    "5880": 76, "5876": 74, "1216": 70, "2912": 72, "2207": 70, "6505": 68, "1301": 66,
    "1303": 66, "2002": 64, "6446": 72,
}

THEME_KEYWORDS = {
    "半導體": 66,
    "IC": 64,
    "晶片": 66,
    "電腦及週邊": 62,
    "電子零組件": 62,
    "通信網路": 60,
    "電機機械": 66,
    "航運": 62,
    "金融": 66,
    "食品": 60,
    "塑膠": 58,
    "鋼鐵": 56,
}


@lru_cache(maxsize=1)
def _public_instruments() -> tuple[dict, ...]:
    provider = PublicMarketDataProvider()
    instruments = unique_instruments([*TW_INSTRUMENTS, *provider.get_instruments()])
    return tuple(instruments)


def _instrument_map() -> Dict[str, dict]:
    return {str(instrument["symbol"]): instrument for instrument in _public_instruments()}


def _get_instrument(stock_id: str) -> dict:
    normalized = stock_id.upper()
    instrument = _instrument_map().get(normalized)
    if instrument is None:
        raise HTTPException(status_code=404, detail="stock not found")
    return instrument


def _signal_map() -> Dict[str, Any]:
    return {signal.symbol: signal for signal in get_prediction_signals()}


def _stock_signal(stock_id: str):
    instrument = _get_instrument(stock_id)
    signals = _signal_map()
    normalized = stock_id.upper()
    return signals.get(normalized) or build_signal(instrument)


def _technical_payload(stock_id: str) -> Dict[str, Any]:
    instrument = _get_instrument(stock_id)
    series = get_mock_price_series(instrument["symbol"])
    indicators = build_technical_indicators(series["highs"], series["lows"], series["closes"], series["volumes"])
    score = calculate_technical_score(TechnicalIndicators(**indicators), series["closes"], series["volumes"])
    return {
        "stock_id": instrument["symbol"],
        "stock_name": instrument["name"],
        "disclaimer": DISCLAIMER,
        "latest_indicators": {key: value for key, value in indicators.items() if key != "signals"},
        "signals": indicators["signals"],
        "technical_score": score,
    }


def _institutional_payload(stock_id: str) -> Dict[str, Any]:
    instrument = _get_instrument(stock_id)
    score = calculate_chip_score(instrument["symbol"])
    return {
        "stock_id": instrument["symbol"],
        "stock_name": instrument["name"],
        "disclaimer": DISCLAIMER,
        "chip_score": score,
        "summary": {
            "foreign_net_ratio": score.get("foreign_net_ratio"),
            "investment_trust_net_ratio": score.get("investment_trust_net_ratio"),
            "dealer_net_ratio": score.get("dealer_net_ratio"),
            "institutional_net_ratio": score.get("institutional_net_ratio"),
            "consecutive_foreign_net_buy_days": score.get("consecutive_foreign_net_buy_days"),
            "consecutive_investment_trust_net_buy_days": score.get("consecutive_investment_trust_net_buy_days"),
            "synchronized_institutional_buying": score.get("synchronized_institutional_buying"),
            "synchronized_institutional_selling": score.get("synchronized_institutional_selling"),
        },
    }


def _ranking_payload(signals: List[Any]) -> Dict[str, Any]:
    return {"disclaimer": DISCLAIMER, "signals": signals}


def _ranking_signals(limit: int = 160) -> List[Any]:
    all_instruments = list(_public_instruments())
    instrument_map = {str(instrument["symbol"]): instrument for instrument in all_instruments}
    covered_instruments = [instrument_map[symbol] for symbol in RECOMMENDATION_COVERAGE_SYMBOLS if symbol in instrument_map]
    other_instruments = [instrument for instrument in all_instruments if str(instrument["symbol"]) not in RECOMMENDATION_COVERAGE_SYMBOLS]
    instruments = unique_instruments([*covered_instruments, *other_instruments])[:limit]
    return [build_signal(instrument) for instrument in instruments]


def _recommendation_score(signal: Any) -> float:
    probability = _percent(signal.probability_up_5d or signal.probability_up_1d or signal.probability_up)
    risk_adjusted = float(signal.risk_adjusted_score or 50)
    risk = _percent(signal.risk_score.total)
    confidence = _percent(signal.confidence)
    return (
        probability * 0.18
        + risk_adjusted * 0.17
        + (100 - risk) * 0.14
        + _theme_fit(signal) * 0.12
        + _factor_score(signal, "chip") * 0.11
        + _factor_score(signal, "technical") * 0.10
        + _factor_score(signal, "fundamental") * 0.08
        + _factor_score(signal, "news") * 0.05
        + _factor_score(signal, "us-linkage") * 0.03
        + confidence * 0.02
        - max(0, risk - 62) * 0.32
    )


def _theme_fit(signal: Any) -> int:
    if signal.symbol in THEME_FIT_BY_SYMBOL:
        return THEME_FIT_BY_SYMBOL[signal.symbol]
    text = f"{signal.name} {getattr(signal, 'sector', '')}"
    return max([score for keyword, score in THEME_KEYWORDS.items() if keyword in text] or [52])


def _percent(value: Any) -> float:
    numeric = float(value or 0)
    if numeric <= 1:
        return numeric * 100
    return min(100, max(0, numeric))


def _factor_score(signal: Any, category: str) -> float:
    for factor in signal.factor_scores:
        if factor.category == category:
            return _percent(factor.score if factor.score >= 0 else (factor.score + 1) / 2)
    return 50


@router.get("/market/summary", response_model=MarketSummary)
def market_summary() -> MarketSummary:
    return get_market_summary()


@router.get("/stocks")
def stocks() -> Dict[str, Any]:
    return {"disclaimer": DISCLAIMER, "stocks": list(_public_instruments())}


@router.get("/stocks/ranking", response_model=RankingResponse)
def stock_ranking() -> RankingResponse:
    signals = sorted(get_prediction_signals(), key=lambda signal: signal.probability_up, reverse=True)
    return RankingResponse(disclaimer=DISCLAIMER, signals=signals)


@router.get("/rankings/top-probability")
def top_probability_ranking() -> Dict[str, Any]:
    signals = sorted(
        _ranking_signals(),
        key=_recommendation_score,
        reverse=True,
    )
    return _ranking_payload(signals)


@router.get("/rankings/institutional-buying")
def institutional_buying_ranking() -> Dict[str, Any]:
    rows = []
    for instrument in list(_public_instruments())[:160]:
        chip_score = calculate_chip_score(instrument["symbol"])
        rows.append(
            {
                "stock_id": instrument["symbol"],
                "stock_name": instrument["name"],
                "score": chip_score["score"],
                "institutional_net_ratio": chip_score.get("institutional_net_ratio", 0),
                "positive_factors": chip_score["positive_factors"],
                "risk_factors": chip_score["risk_factors"],
            }
        )
    rows.sort(key=lambda row: (row["institutional_net_ratio"], row["score"]), reverse=True)
    return {"disclaimer": DISCLAIMER, "ranking": rows}


@router.get("/rankings/macd-golden-cross")
def macd_golden_cross_ranking() -> Dict[str, Any]:
    rows = []
    for instrument in list(_public_instruments())[:160]:
        technical = _technical_payload(instrument["symbol"])
        macd = technical["signals"]["macd"]
        rows.append(
            {
                "stock_id": instrument["symbol"],
                "stock_name": instrument["name"],
                "macd_golden_cross": macd["golden_cross"],
                "macd_hist": macd["macd_hist"],
                "dif": macd["dif"],
                "dea": macd["dea"],
                "technical_score": technical["technical_score"]["score"],
            }
        )
    rows.sort(key=lambda row: (row["macd_golden_cross"], row["technical_score"]), reverse=True)
    return {"disclaimer": DISCLAIMER, "ranking": rows}


@router.get("/rankings/volume-price-divergence")
def volume_price_divergence_ranking() -> Dict[str, Any]:
    rows = []
    for instrument in list(_public_instruments())[:160]:
        technical = _technical_payload(instrument["symbol"])
        divergence = technical["signals"]["volume_price_divergence"]
        rows.append(
            {
                "stock_id": instrument["symbol"],
                "stock_name": instrument["name"],
                "state": divergence["state"],
                "states": divergence["states"],
                "bearish_divergence": divergence["bearish_divergence"],
                "bullish_divergence": divergence["bullish_divergence"],
                "score_signal": divergence["score_signal"],
            }
        )
    rows.sort(key=lambda row: (row["bullish_divergence"], row["score_signal"]), reverse=True)
    return {"disclaimer": DISCLAIMER, "ranking": rows}


@router.get("/risk/high-risk")
def high_risk_stocks() -> Dict[str, Any]:
    signals = sorted(get_prediction_signals(), key=lambda signal: signal.risk_score.total, reverse=True)
    rows = [
        {
            "stock_id": signal.symbol,
            "stock_name": signal.name,
            "risk_score": signal.risk_score,
            "probability_up_1d": signal.probability_up_1d,
            "top_risk_factors": (signal.explanation or {}).get("top_risk_factors", []),
        }
        for signal in signals
        if signal.risk_score.total >= 0.2
    ]
    return {"disclaimer": DISCLAIMER, "signals": rows}


@router.get("/stocks/{stock_id}", response_model=StockDetailResponse)
def stock_detail(stock_id: str) -> StockDetailResponse:
    normalized = stock_id.upper()
    instrument = _get_instrument(normalized)
    signal = _signal_map().get(normalized) or build_signal(instrument)

    return StockDetailResponse(
        disclaimer=DISCLAIMER,
        instrument=instrument,
        signal=signal,
        factor_history=[
            {"date": "2026-05-27", "composite_score": 0.18, "risk_score": 0.34},
            {"date": "2026-05-28", "composite_score": 0.22, "risk_score": 0.33},
            {"date": "2026-05-29", "composite_score": 0.26, "risk_score": 0.31},
            {"date": "2026-06-01", "composite_score": signal.composite_score, "risk_score": signal.risk_score.total},
        ],
    )


@router.get("/stocks/{stock_id}/scores")
def stock_scores(stock_id: str) -> Dict[str, Any]:
    signal = _stock_signal(stock_id)
    return {
        "disclaimer": DISCLAIMER,
        "stock_id": signal.symbol,
        "stock_name": signal.name,
        "BullishScore": signal.bullish_score,
        "RiskScore": signal.risk_score.total,
        "RiskAdjustedScore": signal.risk_adjusted_score,
        "probability_up_1d": signal.probability_up_1d,
        "probability_up_5d": signal.probability_up_5d,
        "probability_up_20d": signal.probability_up_20d,
        "factor_scores": signal.factor_scores,
        "explanation": signal.explanation,
        "confidence": signal.confidence,
    }


@router.get("/stocks/{stock_id}/technical")
def stock_technical(stock_id: str) -> Dict[str, Any]:
    return _technical_payload(stock_id)


@router.get("/stocks/{stock_id}/institutional")
def stock_institutional(stock_id: str) -> Dict[str, Any]:
    return _institutional_payload(stock_id)


@router.get("/stocks/{stock_id}/news")
def stock_news(stock_id: str) -> Dict[str, Any]:
    instrument = _get_instrument(stock_id)
    provider = PublicMarketDataProvider()
    news = provider.get_news(instrument["symbol"])
    return {
        "stock_id": instrument["symbol"],
        "stock_name": instrument["name"],
        "disclaimer": DISCLAIMER,
        "news": news or get_mock_news(instrument["symbol"]),
    }

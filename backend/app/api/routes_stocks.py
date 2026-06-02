from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from app.schemas import MarketSummary, RankingResponse, StockDetailResponse, TechnicalIndicators
from app.services.market_data import get_market_summary, get_prediction_signals
from app.services.scoring import DISCLAIMER
from app.services.data_providers.mock_provider import TW_INSTRUMENTS, get_mock_news, get_mock_price_series
from app.services.indicators import build_technical_indicators
from app.services.scoring.chip_score import calculate_chip_score
from app.services.scoring.technical_score import calculate_technical_score

router = APIRouter()


def _instrument_map() -> Dict[str, dict]:
    return {instrument["symbol"]: instrument for instrument in TW_INSTRUMENTS}


def _get_instrument(stock_id: str) -> dict:
    normalized = stock_id.upper()
    instrument = _instrument_map().get(normalized)
    if instrument is None:
        raise HTTPException(status_code=404, detail="stock not found")
    return instrument


def _signal_map() -> Dict[str, Any]:
    return {signal.symbol: signal for signal in get_prediction_signals()}


def _stock_signal(stock_id: str):
    _get_instrument(stock_id)
    signals = _signal_map()
    return signals[stock_id.upper()]


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


@router.get("/market/summary", response_model=MarketSummary)
def market_summary() -> MarketSummary:
    return get_market_summary()


@router.get("/stocks")
def stocks() -> Dict[str, Any]:
    return {"disclaimer": DISCLAIMER, "stocks": TW_INSTRUMENTS}


@router.get("/stocks/ranking", response_model=RankingResponse)
def stock_ranking() -> RankingResponse:
    signals = sorted(get_prediction_signals(), key=lambda signal: signal.probability_up, reverse=True)
    return RankingResponse(disclaimer=DISCLAIMER, signals=signals)


@router.get("/rankings/top-probability")
def top_probability_ranking() -> Dict[str, Any]:
    signals = sorted(get_prediction_signals(), key=lambda signal: signal.probability_up_1d or signal.probability_up, reverse=True)
    return _ranking_payload(signals)


@router.get("/rankings/institutional-buying")
def institutional_buying_ranking() -> Dict[str, Any]:
    rows = []
    for instrument in TW_INSTRUMENTS:
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
    for instrument in TW_INSTRUMENTS:
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
    for instrument in TW_INSTRUMENTS:
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
    signals = _signal_map()

    return StockDetailResponse(
        disclaimer=DISCLAIMER,
        instrument=instrument,
        signal=signals[normalized],
        factor_history=[
            {"date": "2026-05-27", "composite_score": 0.18, "risk_score": 0.34},
            {"date": "2026-05-28", "composite_score": 0.22, "risk_score": 0.33},
            {"date": "2026-05-29", "composite_score": 0.26, "risk_score": 0.31},
            {"date": "2026-06-01", "composite_score": signals[normalized].composite_score, "risk_score": signals[normalized].risk_score.total},
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
    return {
        "stock_id": instrument["symbol"],
        "stock_name": instrument["name"],
        "disclaimer": DISCLAIMER,
        "news": get_mock_news(instrument["symbol"]),
    }

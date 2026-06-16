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
from app.services.taiwan_prediction_tool import build_prediction_tool_snapshot, rank_signals_with_taiwan_tool

router = APIRouter()

RECOMMENDATION_COVERAGE_SYMBOLS = [
    "2330", "2454", "3035", "3661", "2382", "3231", "6669", "2317", "2308", "2345",
    "3017", "3324", "2383", "3037", "8046", "3711", "1590", "2049", "2359", "1504",
    "1513", "1519", "1605", "2603", "2609", "2615", "2618", "2610", "2634", "2881",
    "2882", "2884", "2885", "2886", "2891", "5880", "5876", "1216", "2912", "2207",
    "6505", "1301", "1303", "2002", "6446", "5871", "4904", "3008", "2408", "2357",
]

RECOMMENDATION_SEED_INSTRUMENTS = [
    {"symbol": "2330", "market": "TW", "name": "台積電", "sector": "半導體", "currency": "TWD"},
    {"symbol": "2454", "market": "TW", "name": "聯發科", "sector": "半導體", "currency": "TWD"},
    {"symbol": "3035", "market": "TW", "name": "智原", "sector": "半導體", "currency": "TWD"},
    {"symbol": "3661", "market": "TW", "name": "世芯-KY", "sector": "半導體", "currency": "TWD"},
    {"symbol": "2382", "market": "TW", "name": "廣達", "sector": "電腦及週邊", "currency": "TWD"},
    {"symbol": "3231", "market": "TW", "name": "緯創", "sector": "電腦及週邊", "currency": "TWD"},
    {"symbol": "6669", "market": "TW", "name": "緯穎", "sector": "電腦及週邊", "currency": "TWD"},
    {"symbol": "2317", "market": "TW", "name": "鴻海", "sector": "電子代工", "currency": "TWD"},
    {"symbol": "2308", "market": "TW", "name": "台達電", "sector": "電源管理", "currency": "TWD"},
    {"symbol": "2345", "market": "TW", "name": "智邦", "sector": "通信網路", "currency": "TWD"},
    {"symbol": "3017", "market": "TW", "name": "奇鋐", "sector": "散熱", "currency": "TWD"},
    {"symbol": "3324", "market": "TPEX", "name": "雙鴻", "sector": "散熱", "currency": "TWD"},
    {"symbol": "2383", "market": "TW", "name": "台光電", "sector": "CCL", "currency": "TWD"},
    {"symbol": "3037", "market": "TW", "name": "欣興", "sector": "PCB/載板", "currency": "TWD"},
    {"symbol": "8046", "market": "TW", "name": "南電", "sector": "PCB/載板", "currency": "TWD"},
    {"symbol": "3711", "market": "TW", "name": "日月光投控", "sector": "封裝測試", "currency": "TWD"},
    {"symbol": "1590", "market": "TW", "name": "亞德客-KY", "sector": "電機機械", "currency": "TWD"},
    {"symbol": "2049", "market": "TW", "name": "上銀", "sector": "機器人/自動化", "currency": "TWD"},
    {"symbol": "2359", "market": "TW", "name": "所羅門", "sector": "機器人/AI 視覺", "currency": "TWD"},
    {"symbol": "1504", "market": "TW", "name": "東元", "sector": "電機機械", "currency": "TWD"},
    {"symbol": "1513", "market": "TW", "name": "中興電", "sector": "重電", "currency": "TWD"},
    {"symbol": "1519", "market": "TW", "name": "華城", "sector": "重電", "currency": "TWD"},
    {"symbol": "1605", "market": "TW", "name": "華新", "sector": "電線電纜", "currency": "TWD"},
    {"symbol": "2603", "market": "TW", "name": "長榮", "sector": "航運業", "currency": "TWD"},
    {"symbol": "2609", "market": "TW", "name": "陽明", "sector": "航運業", "currency": "TWD"},
    {"symbol": "2615", "market": "TW", "name": "萬海", "sector": "航運業", "currency": "TWD"},
    {"symbol": "2618", "market": "TW", "name": "長榮航", "sector": "航空", "currency": "TWD"},
    {"symbol": "2610", "market": "TW", "name": "華航", "sector": "航空", "currency": "TWD"},
    {"symbol": "2634", "market": "TW", "name": "漢翔", "sector": "航太/國防", "currency": "TWD"},
    {"symbol": "2881", "market": "TW", "name": "富邦金", "sector": "金融保險", "currency": "TWD"},
    {"symbol": "2882", "market": "TW", "name": "國泰金", "sector": "金融保險", "currency": "TWD"},
    {"symbol": "2884", "market": "TW", "name": "玉山金", "sector": "金融保險", "currency": "TWD"},
    {"symbol": "2885", "market": "TW", "name": "元大金", "sector": "金融保險", "currency": "TWD"},
    {"symbol": "2886", "market": "TW", "name": "兆豐金", "sector": "金融保險", "currency": "TWD"},
    {"symbol": "2891", "market": "TW", "name": "中信金", "sector": "金融保險", "currency": "TWD"},
    {"symbol": "5880", "market": "TW", "name": "合庫金", "sector": "金融保險", "currency": "TWD"},
    {"symbol": "5876", "market": "TW", "name": "上海商銀", "sector": "金融保險", "currency": "TWD"},
    {"symbol": "1216", "market": "TW", "name": "統一", "sector": "食品工業", "currency": "TWD"},
    {"symbol": "2912", "market": "TW", "name": "統一超", "sector": "貿易百貨", "currency": "TWD"},
    {"symbol": "2207", "market": "TW", "name": "和泰車", "sector": "汽車工業", "currency": "TWD"},
    {"symbol": "6505", "market": "TW", "name": "台塑化", "sector": "油電燃氣", "currency": "TWD"},
    {"symbol": "1301", "market": "TW", "name": "台塑", "sector": "塑膠工業", "currency": "TWD"},
    {"symbol": "1303", "market": "TW", "name": "南亞", "sector": "塑膠工業", "currency": "TWD"},
    {"symbol": "2002", "market": "TW", "name": "中鋼", "sector": "鋼鐵工業", "currency": "TWD"},
    {"symbol": "6446", "market": "TPEX", "name": "藥華藥", "sector": "生技醫療", "currency": "TWD"},
    {"symbol": "5871", "market": "TW", "name": "中租-KY", "sector": "金融保險", "currency": "TWD"},
    {"symbol": "4904", "market": "TW", "name": "遠傳", "sector": "通信網路", "currency": "TWD"},
    {"symbol": "3008", "market": "TW", "name": "大立光", "sector": "光電業", "currency": "TWD"},
    {"symbol": "2408", "market": "TW", "name": "南亞科", "sector": "半導體", "currency": "TWD"},
    {"symbol": "2357", "market": "TW", "name": "華碩", "sector": "電腦及週邊", "currency": "TWD"},
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

HORIZON_WEIGHTS = {
    "1d": {
        "technical": 25,
        "chip": 22,
        "us_market": 18,
        "market": 12,
        "news": 10,
        "revenue_industry": 5,
        "fundamental": 5,
        "valuation": 3,
    },
    "5d": {
        "technical": 22,
        "chip": 22,
        "us_market": 13,
        "market": 8,
        "news": 5,
        "revenue_industry": 15,
        "fundamental": 12,
        "valuation": 3,
    },
    "20d": {
        "technical": 15,
        "chip": 18,
        "us_market": 8,
        "market": 8,
        "news": 2,
        "revenue_industry": 22,
        "fundamental": 22,
        "valuation": 5,
    },
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
    data_date = max((getattr(signal, "signal_date", None) for signal in signals), default=None)
    return {
        "disclaimer": DISCLAIMER,
        "signals": signals,
        "data_date": data_date,
        "candidate_count": len(signals),
        "method": "dynamic-public-instrument-pool",
        "freshness": {
            "mode": "official_aggregate",
            "label": f"候選池資料日 {data_date.isoformat()}" if data_date else "候選池資料日待確認",
            "summary": "後端 ranking 目前使用當日產生的候選池日期。若前端 fallback 偵測到 TWSE 個股 STOCK_DAY 比 STOCK_DAY_ALL 新，會在 UI 顯示個股官方覆蓋說明。",
            "market_study_baseline_date": "2026-06-03",
        },
    }


def _stable_symbol_score(symbol: str) -> float:
    return sum(ord(char) * (index + 3) for index, char in enumerate(symbol)) % 17


def _instrument_priority(instrument: dict) -> float:
    text = f"{instrument.get('symbol', '')} {instrument.get('name', '')} {instrument.get('sector', '')}"
    rules = [
        ("CCL|PCB|載板|ABF|散熱|液冷|封裝|先進封裝", 82),
        ("機器人|自動化|電機|電器電纜|重電|電網|變壓器", 72),
        ("半導體|IC|晶片|電子零組件|電腦及週邊|通信網路|其他電子|資訊服務|數位雲端", 68),
        ("金融|金控|銀行|保險|證券", 64),
        ("航運|航空|貨櫃|航太|國防", 62),
        ("油電|塑膠|化學|鋼鐵|水泥|原物料", 58),
        ("食品|貿易百貨|觀光|居家|運動休閒|內需", 56),
        ("生技|醫療|汽車|建材營造", 46),
    ]
    import re

    base = next((score for pattern, score in rules if re.search(pattern, text)), 54)
    symbol = str(instrument.get("symbol", ""))
    seeded_boost = _stable_symbol_score(symbol) * 0.45
    known_watch_boost = 4 if symbol in RECOMMENDATION_COVERAGE_SYMBOLS else 0
    return base + seeded_boost + known_watch_boost


def _ranking_signals(limit: int = 160) -> List[Any]:
    all_instruments = list(_public_instruments())
    instruments = sorted(
        unique_instruments([*all_instruments, *RECOMMENDATION_SEED_INSTRUMENTS]),
        key=_instrument_priority,
        reverse=True,
    )[:limit]
    return [build_signal(instrument) for instrument in instruments]


def _recommendation_score(signal: Any, market_score: float, horizon: str = "5d") -> float:
    stock_score = _horizon_stock_score(signal, market_score, horizon)
    market_multiplier = _market_multiplier(signal, market_score)
    return _clamp_score(
        stock_score * market_multiplier
        - _overheat_penalty(signal)
        - _event_risk_penalty(signal)
    )


def _horizon_stock_score(signal: Any, market_score: float, horizon: str) -> float:
    weights = HORIZON_WEIGHTS[horizon]
    fundamental = _factor_score(signal, "fundamental")
    technical = _factor_score(signal, "technical")
    chip = _factor_score(signal, "chip")
    news = _factor_score(signal, "news")
    us_market = _factor_score(signal, "us-linkage")
    revenue_industry = _revenue_industry_score(signal, fundamental, technical, news, us_market)
    valuation = _valuation_score(signal, fundamental)
    confidence = _percent(signal.confidence)
    return _clamp_score(
        technical * weights["technical"] / 100
        + chip * weights["chip"] / 100
        + us_market * weights["us_market"] / 100
        + market_score * weights["market"] / 100
        + news * weights["news"] / 100
        + revenue_industry * weights["revenue_industry"] / 100
        + fundamental * weights["fundamental"] / 100
        + valuation * weights["valuation"] / 100
        + max(0, confidence - 60) * 0.04
    )


def _market_state_score(signals: List[Any]) -> float:
    technical_scores = [_factor_score(signal, "technical") for signal in signals]
    chip_scores = [_factor_score(signal, "chip") for signal in signals]
    us_scores = [_factor_score(signal, "us-linkage") for signal in signals]
    risk_scores = [_percent(signal.risk_score.total) for signal in signals]
    taiex_trend = _average(technical_scores)
    market_breadth = len([score for score in technical_scores if score >= 55]) / max(1, len(technical_scores)) * 100
    foreign_funds = _average(chip_scores)
    us_tech_risk = _average(us_scores)
    fx_trend = 55
    volatility_risk = _average([100 - score for score in risk_scores])
    return _clamp_score(
        taiex_trend * 0.30
        + market_breadth * 0.20
        + foreign_funds * 0.20
        + us_tech_risk * 0.15
        + fx_trend * 0.10
        + volatility_risk * 0.05
    )


def _market_multiplier(signal: Any, market_score: float) -> float:
    if market_score > 65:
        return 1.06
    if market_score >= 50:
        return 1.0
    multiplier = 0.92 if market_score >= 40 else 0.84
    if _is_defensive_theme(signal):
        return min(1.0, multiplier + 0.06)
    return multiplier


def _revenue_industry_score(signal: Any, fundamental: float, technical: float, news: float, us_market: float) -> float:
    return _clamp_score(
        _theme_fit(signal) * 0.42
        + fundamental * 0.30
        + technical * 0.13
        + news * 0.08
        + us_market * 0.07
    )


def _valuation_score(signal: Any, fundamental: float) -> float:
    risk = _percent(signal.risk_score.total)
    risk_adjusted = _clamp_score(float(signal.risk_adjusted_score or 50))
    return _clamp_score(50 * 0.40 + fundamental * 0.28 + risk_adjusted * 0.22 + (100 - risk) * 0.10)


def _overheat_penalty(signal: Any) -> float:
    technical = _factor_score(signal, "technical")
    chip = _factor_score(signal, "chip")
    risk = _percent(signal.risk_score.total)
    rsi = float(signal.technicals.rsi_14 or 0)
    penalty = 0.0
    if rsi > 75:
        penalty += 4
    if technical >= 78 and risk >= 55:
        penalty += 3
    if chip < 48 and technical > 70:
        penalty += 4
    if risk >= 68:
        penalty += 3
    return min(15, round(penalty))


def _event_risk_penalty(signal: Any) -> float:
    event_risk = _percent(signal.risk_score.event)
    negative_news = len([event for event in signal.news if event.sentiment == "negative" or event.impact_score < -0.35])
    return min(12, round(max(0, event_risk - 55) * 0.12 + negative_news * 1.5))


def _is_defensive_theme(signal: Any) -> bool:
    text = f"{signal.name} {getattr(signal, 'sector', '')}"
    return any(keyword in text for keyword in ("金融", "銀行", "金控", "保險", "食品", "零售", "百貨"))


def _average(values: List[float]) -> float:
    return _clamp_score(sum(values) / max(1, len(values)))


def _clamp_score(value: float) -> float:
    return min(100, max(0, round(value, 2)))


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
    return RankingResponse(**_ranking_payload(signals))


@router.get("/rankings/top-probability")
def top_probability_ranking() -> Dict[str, Any]:
    ranking_candidates = _ranking_signals()
    signals = rank_signals_with_taiwan_tool(ranking_candidates, "5d")
    return _ranking_payload(signals)


@router.get("/market/taiwan-prediction-tool")
def taiwan_prediction_tool() -> Dict[str, Any]:
    return {
        "disclaimer": DISCLAIMER,
        **build_prediction_tool_snapshot(_ranking_signals()),
    }


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

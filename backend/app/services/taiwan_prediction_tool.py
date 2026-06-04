from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Sequence


HORIZON_WEIGHTS: Dict[str, Dict[str, float]] = {
    "1d": {
        "technical": 0.25,
        "chip": 0.22,
        "us_market": 0.18,
        "market": 0.12,
        "news": 0.10,
        "revenue_industry": 0.05,
        "fundamental": 0.05,
        "valuation": 0.03,
    },
    "5d": {
        "technical": 0.22,
        "chip": 0.22,
        "us_market": 0.13,
        "market": 0.08,
        "news": 0.05,
        "revenue_industry": 0.15,
        "fundamental": 0.12,
        "valuation": 0.03,
    },
    "20d": {
        "technical": 0.15,
        "chip": 0.18,
        "us_market": 0.08,
        "market": 0.08,
        "news": 0.02,
        "revenue_industry": 0.22,
        "fundamental": 0.22,
        "valuation": 0.05,
    },
}

TAIWAN_MARKET_RESEARCH_2026_03_01_TO_06_03: Dict[str, Any] = {
    "research_window": {
        "start": "2026-03-01",
        "first_trading_day": "2026-03-02",
        "end": "2026-06-03",
        "trading_days": 65,
    },
    "market_summary": {
        "taiex_start_close": 35095.09,
        "taiex_end_close": 46459.16,
        "taiex_period_return": 0.3238,
        "taiex_20d_return": 0.1293,
        "taiex_60d_return": 0.3827,
        "taiex_high_date": "2026-06-03",
        "taiex_high": 46552.16,
        "taiex_low_date": "2026-03-09",
        "taiex_low": 31529.36,
        "max_drawdown": -0.0961,
        "max_drawdown_date": "2026-03-31",
        "above_ma20": True,
        "above_ma60": True,
        "daily_volatility": 0.0197,
        "latest_breadth_advancers": 763,
        "latest_breadth_decliners": 289,
        "latest_breadth_total": 1090,
        "latest_breadth_ratio": 0.70,
        "average_breadth_ratio_10d": 0.70,
    },
    "market_state": {
        "score": 73,
        "label": "強多但集中",
        "action": "可積極挑股，但只收流動性足夠、低過熱、多因子共振的股票。",
        "tone": "positive",
        "multiplier": 1.03,
        "components": [
            {
                "name": "加權指數趨勢",
                "score": 92,
                "detail": "3/2 至 6/3 TAIEX +32.38%，6/3 創區間高點，且站上 MA20 / MA60。",
            },
            {
                "name": "市場寬度",
                "score": 70,
                "detail": "6/3 上漲家數 763 / 1090，最近 10 個交易日上漲比例約 70%。",
            },
            {
                "name": "大盤資金",
                "score": 64,
                "detail": "目前用籌碼與成交值代理，後續接入完整外資大盤買賣超再校準。",
            },
            {
                "name": "美股與 AI 外溢",
                "score": 76,
                "detail": "AI / ICT 出口與半導體供應鏈仍是主要基本面背景，但不是唯一可得分題材。",
            },
            {
                "name": "匯率",
                "score": 55,
                "detail": "暫用中性分數，接央行匯率與美元指數後再進入模型。",
            },
            {
                "name": "波動風險",
                "score": 57,
                "detail": "期間最大回撤約 -9.61%，日波動約 1.97%，追高需扣過熱分。",
            },
            {
                "name": "集中風險扣分",
                "score": -8,
                "detail": "TAIEX 市值加權高度集中，不能把大盤強度直接等同於所有股票都強。",
            },
        ],
    },
    "sector_rotation": [
        {"name": "電子零組件", "score": 92, "return": 0.7598, "role": "leader"},
        {"name": "AI 供應鏈", "score": 90, "return": 0.7276, "role": "leader"},
        {"name": "IC 設計", "score": 89, "return": 0.7181, "role": "leader"},
        {"name": "晶圓製造", "score": 88, "return": 0.6984, "role": "leader"},
        {"name": "智慧移動與電動車", "score": 86, "return": 0.7291, "role": "leader"},
        {"name": "半導體全市場", "score": 84, "return": 0.6059, "role": "leader"},
        {"name": "重電與電網", "score": 76, "return": None, "role": "selective"},
        {"name": "機器人與自動化", "score": 74, "return": None, "role": "selective"},
        {"name": "金融避險", "score": 66, "return": None, "role": "defensive"},
        {"name": "航運航空", "score": 63, "return": None, "role": "cyclical"},
        {"name": "內需防禦", "score": 56, "return": None, "role": "defensive"},
        {"name": "食品", "score": 48, "return": -0.0277, "role": "laggard"},
        {"name": "汽車", "score": 43, "return": -0.0705, "role": "laggard"},
        {"name": "建材營造", "score": 42, "return": -0.0623, "role": "laggard"},
        {"name": "生技醫療", "score": 40, "return": -0.1062, "role": "laggard"},
    ],
    "hard_filters": {
        "min_trade_value_twd": 30_000_000,
        "exclude_attention_or_disposition": True,
        "exclude_low_liquidity": True,
        "exclude_extreme_event_risk": True,
    },
    "model_notes": [
        "分數不是機率；probability_up 必須用歷史分桶、Brier Score 與 walk-forward 校準。",
        "流動性不加分，直接作硬性過濾。",
        "AI 不是唯一加權題材；所有產業都用同業百分位、籌碼、技術、營收與風險重新競爭。",
        "1D 看技術、籌碼、美股夜盤；5D 看籌碼延續與相對強度；20D 看月營收、產業景氣與基本面。",
    ],
    "data_sources": [
        {
            "name": "TWSE TAIEX historical index",
            "url": "https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST",
            "usage": "3/1-6/3 TAIEX trend, MA, return, drawdown, volatility.",
        },
        {
            "name": "TWSE daily market quotes",
            "url": "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY_ALL",
            "usage": "Daily breadth and liquidity hard filters.",
        },
        {
            "name": "TWSE daily index tables",
            "url": "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX",
            "usage": "Sector and thematic index rotation from 3/2 to 6/3.",
        },
        {
            "name": "MOPS monthly revenue",
            "url": "https://mopsfin.twse.com.tw/opendata/t187ap05_L.csv",
            "usage": "Monthly revenue and industry cycle score for 5D / 20D.",
        },
        {
            "name": "DGBAS 2026Q1 GDP advance estimate",
            "url": "https://eng.dgbas.gov.tw/News_Content.aspx?n=4438&s=236205",
            "usage": "Macro context for AI / ICT export strength.",
        },
    ],
}

SYMBOL_THEME_SCORES: Dict[str, int] = {
    "2330": 88,
    "2454": 89,
    "3035": 89,
    "3661": 89,
    "2382": 90,
    "3231": 90,
    "6669": 90,
    "2317": 82,
    "2308": 84,
    "2345": 86,
    "3017": 92,
    "3324": 92,
    "2383": 92,
    "3037": 92,
    "8046": 90,
    "3711": 84,
    "1590": 74,
    "2049": 74,
    "2359": 74,
    "1504": 76,
    "1513": 76,
    "1519": 76,
    "1605": 70,
    "2603": 63,
    "2609": 63,
    "2615": 63,
    "2618": 63,
    "2610": 63,
    "2634": 64,
    "2881": 66,
    "2882": 66,
    "2884": 66,
    "2885": 66,
    "2886": 66,
    "2891": 66,
    "5880": 66,
    "5876": 66,
    "1216": 56,
    "2912": 56,
    "2207": 43,
    "6505": 52,
    "1301": 50,
    "1303": 50,
    "2002": 48,
    "6446": 40,
    "4904": 58,
    "3008": 52,
    "2408": 84,
    "2357": 78,
}

SECTOR_THEME_KEYWORDS: Sequence[tuple[str, int]] = (
    ("電子零組件", 92),
    ("CCL", 92),
    ("PCB", 92),
    ("載板", 90),
    ("AI", 90),
    ("伺服器", 90),
    ("半導體", 84),
    ("IC", 89),
    ("晶片", 89),
    ("封裝", 84),
    ("散熱", 92),
    ("電腦", 82),
    ("通信", 76),
    ("電機", 76),
    ("重電", 76),
    ("電線", 70),
    ("機器人", 74),
    ("自動化", 74),
    ("航運", 63),
    ("航空", 63),
    ("航太", 64),
    ("金融", 66),
    ("銀行", 66),
    ("金控", 66),
    ("食品", 48),
    ("汽車", 43),
    ("建材", 42),
    ("營造", 42),
    ("生技", 40),
    ("醫療", 40),
    ("塑膠", 50),
    ("鋼鐵", 48),
)


def build_prediction_tool_snapshot(signals: Iterable[Any] = ()) -> Dict[str, Any]:
    signals_list = list(signals)
    return {
        "research": TAIWAN_MARKET_RESEARCH_2026_03_01_TO_06_03,
        "horizon_weights": HORIZON_WEIGHTS,
        "market_state": TAIWAN_MARKET_RESEARCH_2026_03_01_TO_06_03["market_state"],
        "ranked_signals": [
            _signal_row(signal)
            for signal in rank_signals_with_taiwan_tool(signals_list)[:20]
        ],
    }


def rank_signals_with_taiwan_tool(signals: Iterable[Any], horizon: str = "5d") -> List[Any]:
    return sorted(signals, key=lambda signal: score_prediction_signal(signal, horizon)["score"], reverse=True)


def score_prediction_signal(signal: Any, horizon: str = "5d") -> Dict[str, Any]:
    market_state = TAIWAN_MARKET_RESEARCH_2026_03_01_TO_06_03["market_state"]
    factors = _factor_inputs(signal)
    stock_score = _weighted_score(factors, HORIZON_WEIGHTS[horizon], market_state["score"])
    overheat_penalty = _overheat_penalty(signal, factors)
    event_risk_penalty = _event_risk_penalty(signal)
    liquidity_passed = _liquidity_passed(signal)
    multiplier = _market_multiplier(signal, float(market_state["score"]))
    final_score = _clamp_score(stock_score * multiplier - overheat_penalty - event_risk_penalty)
    if not liquidity_passed:
        final_score = min(final_score, 45)
    return {
        "score": round(final_score),
        "stock_score": round(stock_score),
        "horizon": horizon,
        "factor_inputs": factors,
        "overheat_penalty": overheat_penalty,
        "event_risk_penalty": event_risk_penalty,
        "liquidity_passed": liquidity_passed,
        "market_multiplier": multiplier,
        "market_state_score": market_state["score"],
        "reason": _reason(signal, factors, overheat_penalty, event_risk_penalty, liquidity_passed),
    }


def score_all_horizons(signal: Any) -> Dict[str, Dict[str, Any]]:
    return {horizon: score_prediction_signal(signal, horizon) for horizon in HORIZON_WEIGHTS}


def _signal_row(signal: Any) -> Dict[str, Any]:
    scores = score_all_horizons(signal)
    return {
        "symbol": getattr(signal, "symbol", ""),
        "name": getattr(signal, "name", ""),
        "score_1d": scores["1d"]["score"],
        "score_5d": scores["5d"]["score"],
        "score_20d": scores["20d"]["score"],
        "reason": scores["5d"]["reason"],
        "overheat_penalty": scores["5d"]["overheat_penalty"],
        "event_risk_penalty": scores["5d"]["event_risk_penalty"],
        "liquidity_passed": scores["5d"]["liquidity_passed"],
    }


def _factor_inputs(signal: Any) -> Dict[str, float]:
    fundamental = _factor_score(signal, "fundamental")
    chip = _factor_score(signal, "chip")
    technical = _factor_score(signal, "technical")
    us_market = _factor_score(signal, "us-linkage", "us_market")
    news = _factor_score(signal, "news")
    risk = _risk_score(signal)
    theme = _theme_score(signal)
    risk_adjusted = _numeric(getattr(signal, "risk_adjusted_score", 50), 50)
    target_price = _factor_score(signal, "target_price", default=50)
    revenue_industry = _clamp_score(
        theme * 0.30
        + fundamental * 0.32
        + chip * 0.12
        + technical * 0.12
        + us_market * 0.08
        + news * 0.06
    )
    valuation = _clamp_score(
        target_price * 0.32
        + fundamental * 0.28
        + risk_adjusted * 0.22
        + (100 - risk) * 0.18
    )
    return {
        "technical": technical,
        "chip": chip,
        "us_market": us_market,
        "news": news,
        "revenue_industry": revenue_industry,
        "fundamental": fundamental,
        "valuation": valuation,
        "theme": theme,
        "risk": risk,
        "confidence": _percent(getattr(signal, "confidence", 0.5)),
    }


def _weighted_score(factors: Mapping[str, float], weights: Mapping[str, float], market_score: float) -> float:
    return _clamp_score(
        factors["technical"] * weights["technical"]
        + factors["chip"] * weights["chip"]
        + factors["us_market"] * weights["us_market"]
        + market_score * weights["market"]
        + factors["news"] * weights["news"]
        + factors["revenue_industry"] * weights["revenue_industry"]
        + factors["fundamental"] * weights["fundamental"]
        + factors["valuation"] * weights["valuation"]
        + max(0.0, factors["confidence"] - 60) * 0.04
    )


def _market_multiplier(signal: Any, market_score: float) -> float:
    defensive = _is_defensive(signal)
    if market_score >= 75:
        return 1.05
    if market_score >= 65:
        return 1.02 if not defensive else 1.0
    if market_score >= 50:
        return 1.0
    return 0.96 if defensive else 0.9


def _theme_score(signal: Any) -> float:
    symbol = str(getattr(signal, "symbol", ""))
    if symbol in SYMBOL_THEME_SCORES:
        return float(SYMBOL_THEME_SCORES[symbol])
    text = f"{getattr(signal, 'name', '')} {getattr(signal, 'sector', '')}"
    matches = [score for keyword, score in SECTOR_THEME_KEYWORDS if keyword in text]
    return float(max(matches) if matches else 52)


def _overheat_penalty(signal: Any, factors: Mapping[str, float]) -> int:
    technicals = getattr(signal, "technicals", None)
    rsi = _numeric(getattr(technicals, "rsi_14", None), 0)
    ma60 = _numeric(getattr(technicals, "ma_60", None), 0)
    quote = getattr(signal, "quote", None)
    close = _numeric(getattr(quote, "close", None) if quote is not None else None, 0)
    valuation = getattr(signal, "valuation", None)
    pe_ratio = _numeric(getattr(valuation, "pe_ratio", None) if valuation is not None else None, 0)
    penalty = 0
    if rsi > 75:
        penalty += 4
    if ma60 and close and close > ma60 * 1.20:
        penalty += 5
    if factors["technical"] >= 78 and factors["risk"] >= 55:
        penalty += 3
    if factors["chip"] < 48 and factors["technical"] > 70:
        penalty += 4
    if pe_ratio >= 40 and factors["fundamental"] < 58:
        penalty += 3
    return min(15, int(round(penalty)))


def _event_risk_penalty(signal: Any) -> int:
    risk_score = getattr(signal, "risk_score", None)
    event_risk = _percent(getattr(risk_score, "event", 0))
    news = getattr(signal, "news", []) or []
    negative_news = len([
        item
        for item in news
        if getattr(item, "sentiment", "") == "negative" or _numeric(getattr(item, "impact_score", 0), 0) < -0.35
    ])
    risk_flags = len([
        flag
        for flag in (getattr(signal, "risk_flags", []) or [])
        if _numeric(getattr(flag, "severity", 0), 0) >= 3
    ])
    return min(12, int(round(max(0.0, event_risk - 55) * 0.12 + negative_news * 1.5 + risk_flags * 2)))


def _liquidity_passed(signal: Any) -> bool:
    quote = getattr(signal, "quote", None)
    trade_value = _numeric(getattr(quote, "trade_value", None) if quote is not None else None, 0)
    if trade_value <= 0:
        return True
    return trade_value >= TAIWAN_MARKET_RESEARCH_2026_03_01_TO_06_03["hard_filters"]["min_trade_value_twd"]


def _reason(
    signal: Any,
    factors: Mapping[str, float],
    overheat_penalty: int,
    event_risk_penalty: int,
    liquidity_passed: bool,
) -> str:
    drivers: List[str] = []
    theme = _theme_score(signal)
    if theme >= 80:
        drivers.append("研究期強勢族群")
    elif _is_defensive(signal):
        drivers.append("防禦型題材")
    elif theme >= 62:
        drivers.append("選擇性題材")
    if factors["chip"] >= 65:
        drivers.append("籌碼延續")
    if factors["technical"] >= 65:
        drivers.append("相對強度")
    if factors["fundamental"] >= 62:
        drivers.append("基本面支持")
    if overheat_penalty:
        drivers.append(f"過熱扣 {overheat_penalty}")
    if event_risk_penalty:
        drivers.append(f"事件扣 {event_risk_penalty}")
    if not liquidity_passed:
        drivers.append("流動性未過濾")
    return " · ".join(drivers[:4]) or "多因子條件中性，需等待更明確訊號"


def _is_defensive(signal: Any) -> bool:
    text = f"{getattr(signal, 'symbol', '')} {getattr(signal, 'name', '')} {getattr(signal, 'sector', '')}"
    return any(keyword in text for keyword in ("金融", "銀行", "金控", "保險", "食品", "零售", "百貨", "電信"))


def _factor_score(signal: Any, *categories: str, default: float = 50) -> float:
    factors = getattr(signal, "factor_scores", []) or []
    wanted = set(categories)
    for factor in factors:
        category = getattr(factor, "category", None)
        if category in wanted:
            value = _numeric(getattr(factor, "score", default), default)
            if -1 <= value <= 1:
                return _clamp_score((value + 1) * 50 if value < 0 else value * 100)
            return _clamp_score(value)
    return float(default)


def _risk_score(signal: Any) -> float:
    risk_score = getattr(signal, "risk_score", None)
    return _percent(getattr(risk_score, "total", 0))


def _percent(value: Any) -> float:
    numeric = _numeric(value, 0)
    if numeric <= 1:
        return _clamp_score(numeric * 100)
    return _clamp_score(numeric)


def _numeric(value: Any, default: float) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp_score(value: float) -> float:
    return max(0.0, min(100.0, value))

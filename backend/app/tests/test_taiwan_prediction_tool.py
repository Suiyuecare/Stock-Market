from types import SimpleNamespace

from app.services.taiwan_prediction_tool import (
    HORIZON_WEIGHTS,
    TAIWAN_MARKET_RESEARCH_2026_03_01_TO_06_03,
    build_prediction_tool_snapshot,
    score_prediction_signal,
)


def _factor(category: str, score: float) -> SimpleNamespace:
    return SimpleNamespace(category=category, score=score)


def _signal(
    symbol: str,
    name: str,
    sector: str,
    *,
    fundamental: float = 60,
    chip: float = 60,
    technical: float = 60,
    us_market: float = 60,
    news: float = 55,
    risk: float = 0.35,
    event_risk: float = 0.20,
    rsi: float = 58,
    trade_value: float = 120_000_000,
) -> SimpleNamespace:
    return SimpleNamespace(
        symbol=symbol,
        name=name,
        sector=sector,
        confidence=0.72,
        risk_adjusted_score=62,
        factor_scores=[
            _factor("fundamental", fundamental),
            _factor("chip", chip),
            _factor("technical", technical),
            _factor("us-linkage", us_market),
            _factor("news", news),
        ],
        risk_score=SimpleNamespace(total=risk, event=event_risk),
        technicals=SimpleNamespace(rsi_14=rsi, ma_60=100),
        quote=SimpleNamespace(close=106, trade_value=trade_value),
        valuation=SimpleNamespace(pe_ratio=22),
        news=[],
        risk_flags=[],
    )


def test_research_snapshot_tracks_2026_q2_market_state() -> None:
    research = TAIWAN_MARKET_RESEARCH_2026_03_01_TO_06_03

    assert research["research_window"]["first_trading_day"] == "2026-03-02"
    assert research["research_window"]["end"] == "2026-06-03"
    assert research["market_summary"]["taiex_period_return"] > 0.32
    assert research["market_summary"]["latest_breadth_ratio"] == 0.70
    assert research["market_state"]["label"] == "強多但集中"


def test_horizon_weights_shift_from_short_term_to_swing_factors() -> None:
    assert HORIZON_WEIGHTS["1d"]["technical"] > HORIZON_WEIGHTS["20d"]["technical"]
    assert HORIZON_WEIGHTS["1d"]["news"] > HORIZON_WEIGHTS["20d"]["news"]
    assert HORIZON_WEIGHTS["20d"]["revenue_industry"] > HORIZON_WEIGHTS["1d"]["revenue_industry"]
    assert HORIZON_WEIGHTS["20d"]["fundamental"] > HORIZON_WEIGHTS["1d"]["fundamental"]


def test_prediction_tool_does_not_prefer_weak_ai_stock_over_strong_financial_stock() -> None:
    weak_ai = _signal(
        "2382",
        "廣達",
        "AI 伺服器",
        fundamental=42,
        chip=38,
        technical=45,
        us_market=72,
        news=55,
        risk=0.62,
    )
    strong_financial = _signal(
        "2881",
        "富邦金",
        "金融保險",
        fundamental=74,
        chip=76,
        technical=72,
        us_market=50,
        news=55,
        risk=0.28,
    )

    assert score_prediction_signal(strong_financial, "5d")["score"] > score_prediction_signal(weak_ai, "5d")["score"]


def test_overheat_and_liquidity_are_penalties_not_bonus_points() -> None:
    normal = _signal("3035", "智原", "半導體", technical=78, chip=70, rsi=65, trade_value=100_000_000)
    overheated = _signal("3035", "智原", "半導體", technical=78, chip=70, rsi=82, trade_value=100_000_000)
    illiquid = _signal("3035", "智原", "半導體", technical=78, chip=70, rsi=65, trade_value=5_000_000)

    normal_score = score_prediction_signal(normal, "5d")
    overheated_score = score_prediction_signal(overheated, "5d")
    illiquid_score = score_prediction_signal(illiquid, "5d")

    assert overheated_score["overheat_penalty"] > normal_score["overheat_penalty"]
    assert overheated_score["score"] < normal_score["score"]
    assert not illiquid_score["liquidity_passed"]
    assert illiquid_score["score"] <= 45


def test_snapshot_returns_ranked_rows_for_frontend() -> None:
    snapshot = build_prediction_tool_snapshot([
        _signal("2881", "富邦金", "金融保險", fundamental=74, chip=76, technical=72),
        _signal("2383", "台光電", "電子零組件", fundamental=66, chip=70, technical=75),
    ])

    assert snapshot["horizon_weights"]["5d"]["chip"] == 0.22
    assert snapshot["market_state"]["score"] == 73
    assert len(snapshot["ranked_signals"]) == 2
    assert {"score_1d", "score_5d", "score_20d"} <= set(snapshot["ranked_signals"][0])

from typing import List, Optional

from app.schemas import TechnicalIndicators
from app.services.indicators.macd import analyze_macd, macd_series
from app.services.indicators.volume_price_divergence import analyze_volume_price_divergence
from app.services.scoring.common import ScorePayload, scoring_payload


def clamp_score(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 4)


def _score_ma_trend(indicators: TechnicalIndicators, closes: List[float]) -> tuple[float, List[str], List[str]]:
    latest = closes[-1]
    score = 50.0
    positives: List[str] = []
    negatives: List[str] = []

    if indicators.ma_5 and indicators.ma_20:
        if indicators.ma_5 > indicators.ma_20:
            score += 12
            positives.append("MA5 above MA20")
        else:
            score -= 10
            negatives.append("MA5 below MA20")
    if indicators.ma_20 and indicators.ma_60:
        if indicators.ma_20 > indicators.ma_60:
            score += 14
            positives.append("MA20 above MA60")
        else:
            score -= 12
            negatives.append("MA20 below MA60")
    if indicators.ma_20:
        if latest > indicators.ma_20:
            score += 10
            positives.append("close above MA20")
        else:
            score -= 10
            negatives.append("close below MA20")
    if indicators.ma_60:
        if latest > indicators.ma_60:
            score += 8
            positives.append("close above MA60")
        else:
            score -= 8
            negatives.append("close below MA60")

    return clamp_score(score), positives, negatives


def _score_macd(closes: List[float]) -> tuple[float, List[str], List[str], List[str]]:
    analysis = analyze_macd(closes)
    score = 50.0
    positives: List[str] = []
    negatives: List[str] = []
    risks: List[str] = []
    hist = analysis["macd_hist"]
    dif = analysis["dif"]

    if hist is not None:
        if float(hist) > 0:
            score += 12
            positives.append("MACD histogram positive")
        else:
            score -= 10
            negatives.append("MACD histogram negative")
    if dif is not None:
        if float(dif) > 0:
            score += 8
            positives.append("MACD DIF above zero")
        else:
            score -= 6
            negatives.append("MACD DIF below zero")
    if analysis["golden_cross"]:
        score += 16
        positives.append("MACD golden cross")
    if analysis["death_cross"]:
        score -= 16
        negatives.append("MACD death cross")
    if analysis["zero_axis_cross_up"]:
        score += 10
        positives.append("MACD zero-axis cross up")
    if analysis["zero_axis_cross_down"]:
        score -= 10
        negatives.append("MACD zero-axis cross down")
    if analysis["bullish_divergence"]:
        score += 12
        positives.append("bullish MACD divergence")
    if analysis["bearish_divergence"]:
        score -= 14
        risks.append("bearish MACD divergence")

    return clamp_score(score), positives, negatives, risks


def _score_rsi(indicators: TechnicalIndicators) -> tuple[float, List[str], List[str], List[str]]:
    score = 50.0
    positives: List[str] = []
    negatives: List[str] = []
    risks: List[str] = []
    value = indicators.rsi_14
    if value is None:
        return score, positives, negatives, risks

    if 45 <= value <= 65:
        score = 70
        positives.append("RSI in constructive range")
    elif 65 < value <= 75:
        score = 62
        positives.append("RSI shows strong momentum")
    elif value > 75:
        score = 42
        risks.append("RSI overextended")
    elif 35 <= value < 45:
        score = 45
        negatives.append("RSI momentum soft")
    else:
        score = 32
        negatives.append("RSI weak")
    return score, positives, negatives, risks


def _score_kd(indicators: TechnicalIndicators) -> tuple[float, List[str], List[str], List[str]]:
    score = 50.0
    positives: List[str] = []
    negatives: List[str] = []
    risks: List[str] = []
    k_value = indicators.k_9
    d_value = indicators.d_9
    if k_value is None or d_value is None:
        return score, positives, negatives, risks

    if k_value > d_value and k_value < 80:
        score += 18
        positives.append("KD momentum positive")
    elif k_value < d_value:
        score -= 14
        negatives.append("KD momentum negative")
    if k_value >= 85 and d_value >= 80:
        score -= 10
        risks.append("KD overbought")
    elif k_value <= 20 and d_value <= 25:
        score += 6
        positives.append("KD near oversold recovery zone")
    return clamp_score(score), positives, negatives, risks


def _score_breakout(closes: List[float], window: int = 20) -> tuple[float, List[str], List[str]]:
    if len(closes) <= window:
        return 50.0, [], []
    previous = closes[-window - 1 : -1]
    latest = closes[-1]
    if latest > max(previous):
        return 82.0, ["price breakout above recent range"], []
    if latest < min(previous):
        return 24.0, [], ["price breakdown below recent range"]
    position = (latest - min(previous)) / max(max(previous) - min(previous), 1e-9)
    return clamp_score(35 + position * 35), [], []


def calculate_technical_score(
    indicators: TechnicalIndicators,
    closes: List[float],
    volumes: Optional[List[float]] = None,
) -> ScorePayload:
    """Return a 0-100 technical score with trend, MACD, RSI, KD, volume, and breakout explanations."""
    if not closes:
        return scoring_payload(score=0, risk_factors=["missing close prices"], confidence=0)

    positives: List[str] = []
    negatives: List[str] = []
    risks: List[str] = []

    trend_score, trend_pos, trend_neg = _score_ma_trend(indicators, closes)
    macd_score, macd_pos, macd_neg, macd_risks = _score_macd(closes)
    rsi_score, rsi_pos, rsi_neg, rsi_risks = _score_rsi(indicators)
    kd_score, kd_pos, kd_neg, kd_risks = _score_kd(indicators)
    breakout_score, breakout_pos, breakout_neg = _score_breakout(closes)

    volume_price_score = 50.0
    if volumes:
        histogram_series = macd_series(closes)["macd_hist"]
        divergence = analyze_volume_price_divergence(closes, volumes, histogram_series)
        volume_price_score = clamp_score(50 + float(divergence["score_signal"]) * 50)
        states = [str(state) for state in divergence["states"]]
        if "price_up_volume_up" in states:
            positives.append("price up with rising volume")
        if "price_up_volume_down" in states:
            negatives.append("price up while volume contracts")
        if "price_down_volume_down" in states:
            positives.append("selling pressure easing")
        if "price_down_volume_up" in states:
            risks.append("price down with rising volume")
        if divergence["bearish_divergence"]:
            risks.append("price new high without volume/OBV/MACD confirmation")
        if divergence["bullish_divergence"]:
            positives.append("price new low without MACD/OBV new low")

    positives.extend(trend_pos + macd_pos + rsi_pos + kd_pos + breakout_pos)
    negatives.extend(trend_neg + macd_neg + rsi_neg + kd_neg + breakout_neg)
    risks.extend(macd_risks + rsi_risks + kd_risks)

    score = (
        trend_score * 0.24
        + volume_price_score * 0.18
        + macd_score * 0.22
        + rsi_score * 0.12
        + kd_score * 0.10
        + breakout_score * 0.14
    )
    confidence = 72.0
    if len(closes) < 60:
        confidence -= 12
    if not volumes:
        confidence -= 10

    payload = scoring_payload(
        score=clamp_score(score),
        positive_factors=positives,
        negative_factors=negatives,
        risk_factors=risks,
        confidence=clamp_score(confidence),
    )
    payload.update(
        {
            "trend_score": trend_score,
            "volume_price_score": volume_price_score,
            "macd_score": macd_score,
            "rsi_score": rsi_score,
            "kd_score": kd_score,
            "breakout_score": breakout_score,
        }
    )
    return payload

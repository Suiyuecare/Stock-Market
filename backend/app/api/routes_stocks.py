from fastapi import APIRouter

from app.schemas import MarketSummary, RankingResponse, StockDetailResponse
from app.services.market_data import get_market_summary, get_prediction_signals
from app.services.scoring import DISCLAIMER
from app.services.data_providers.mock_provider import TW_INSTRUMENTS

router = APIRouter()


@router.get("/market/summary", response_model=MarketSummary)
def market_summary() -> MarketSummary:
    return get_market_summary()


@router.get("/stocks/ranking", response_model=RankingResponse)
def stock_ranking() -> RankingResponse:
    signals = sorted(get_prediction_signals(), key=lambda signal: signal.probability_up, reverse=True)
    return RankingResponse(disclaimer=DISCLAIMER, signals=signals)


@router.get("/stocks/{symbol}", response_model=StockDetailResponse)
def stock_detail(symbol: str) -> StockDetailResponse:
    normalized = symbol.upper()
    signals = {signal.symbol: signal for signal in get_prediction_signals()}
    instrument_map = {instrument["symbol"]: instrument for instrument in TW_INSTRUMENTS}
    if normalized not in signals:
        normalized = "2330"

    return StockDetailResponse(
        disclaimer=DISCLAIMER,
        instrument=instrument_map[normalized],
        signal=signals[normalized],
        factor_history=[
            {"date": "2026-05-27", "composite_score": 0.18, "risk_score": 0.34},
            {"date": "2026-05-28", "composite_score": 0.22, "risk_score": 0.33},
            {"date": "2026-05-29", "composite_score": 0.26, "risk_score": 0.31},
            {"date": "2026-06-01", "composite_score": signals[normalized].composite_score, "risk_score": signals[normalized].risk_score.total},
        ],
    )

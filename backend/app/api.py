from fastapi import APIRouter

from app.config import get_settings
from app.schemas import HealthResponse, MarketSummary, NewsParseRequest, NewsParseResponse, PredictionSignal
from app.services.market_data import get_market_summary, get_prediction_signals
from app.services.news_parser import NewsParser

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service=get_settings().app_name)


@router.get("/market/summary", response_model=MarketSummary)
def market_summary() -> MarketSummary:
    return get_market_summary()


@router.get("/predictions/signals", response_model=list[PredictionSignal])
def prediction_signals() -> list[PredictionSignal]:
    return get_prediction_signals()


@router.post("/news/parse", response_model=NewsParseResponse)
def parse_news(request: NewsParseRequest) -> NewsParseResponse:
    return NewsParser().parse(request)

from fastapi import APIRouter

from app.api.routes_news import router as news_router
from app.api.routes_monitoring import router as monitoring_router
from app.api.routes_scores import router as scores_router
from app.api.routes_stocks import router as stocks_router
from app.api.routes_us_market import router as us_market_router
from app.config import get_settings
from app.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service=get_settings().app_name)


router.include_router(stocks_router)
router.include_router(scores_router)
router.include_router(news_router)
router.include_router(us_market_router)
router.include_router(monitoring_router)

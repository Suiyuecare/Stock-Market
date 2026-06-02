from fastapi import APIRouter

from app.services.data_providers.mock_provider import get_mock_us_linkage

router = APIRouter()


@router.get("/us-market/linkage")
def us_market_linkage():
    return get_mock_us_linkage()

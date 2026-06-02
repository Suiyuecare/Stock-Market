from fastapi import APIRouter

from app.services.market_data import get_prediction_signals

router = APIRouter()


@router.get("/predictions/signals")
def prediction_signals():
    return get_prediction_signals()

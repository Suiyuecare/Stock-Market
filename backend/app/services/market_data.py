from datetime import date

from app.schemas import Instrument, MarketSummary, PredictionSignal
from app.services.factor_engine import DISCLAIMER, build_all_signals
from app.services.mock_provider import TW_INSTRUMENTS, get_mock_us_linkage


def get_market_summary() -> MarketSummary:
    return MarketSummary(
        session_date=date.today(),
        tw_status="after-close-ready",
        us_premarket_status="pending",
        disclaimer=DISCLAIMER,
        instruments=[Instrument(**instrument) for instrument in TW_INSTRUMENTS],
        us_linkage=get_mock_us_linkage(),
    )


def get_prediction_signals() -> list[PredictionSignal]:
    return build_all_signals()

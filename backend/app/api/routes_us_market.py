from fastapi import APIRouter

from app.services.data_providers.mock_provider import TW_INSTRUMENTS, get_mock_us_linkage
from app.services.scoring import DISCLAIMER
from app.services.scoring.us_market_score import calculate_us_market_score

router = APIRouter()


@router.get("/us-market/linkage")
def us_market_linkage():
    return get_mock_us_linkage()


@router.get("/us-market/radar")
def us_market_radar():
    linkage = get_mock_us_linkage()
    stocks = []
    for instrument in TW_INSTRUMENTS:
        profile = {
            "stock_id": instrument["symbol"],
            "stock_name": instrument["name"],
            "industry": instrument.get("sector"),
            "supply_chain_tags": instrument.get("supply_chain_tags", []),
        }
        score = calculate_us_market_score(linkage, profile)
        stocks.append(
            {
                "stock_id": instrument["symbol"],
                "stock_name": instrument["name"],
                "score": score["score"],
                "sensitivity_multiplier": score["sensitivity_multiplier"],
                "positive_factors": score["positive_factors"],
                "negative_factors": score["negative_factors"],
                "risk_factors": score["risk_factors"],
            }
        )
    stocks.sort(key=lambda row: row["score"], reverse=True)
    return {"disclaimer": DISCLAIMER, "linkage": linkage, "stocks": stocks}

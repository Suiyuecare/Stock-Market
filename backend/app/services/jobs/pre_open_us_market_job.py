from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.services.data_providers.mock_provider import MockMarketDataProvider
from app.services.jobs.persistence import persist_us_premarket_result
from app.services.scoring.us_market_score import calculate_us_market_score


def _stock_profile(instrument: Dict[str, object]) -> Dict[str, object]:
    return {
        "stock_id": instrument["symbol"],
        "stock_name": instrument["name"],
        "industry": instrument.get("sector"),
        "supply_chain_tags": instrument.get("supply_chain_tags", []),
    }


def run_us_premarket_job(provider: Optional[MockMarketDataProvider] = None, session: Optional[Session] = None) -> Dict[str, object]:
    """Run the US pre-open linkage mock pipeline and return a ranked radar."""
    started_at = datetime.utcnow()
    data_provider = provider or MockMarketDataProvider()
    linkage = data_provider.get_us_linkage()
    radar: List[Dict[str, object]] = []

    for instrument in data_provider.get_instruments():
        score = calculate_us_market_score(linkage, _stock_profile(instrument))
        radar.append(
            {
                "stock_id": instrument["symbol"],
                "stock_name": instrument["name"],
                "us_market_score": score["score"],
                "sensitivity_multiplier": score["sensitivity_multiplier"],
                "positive_factors": score["positive_factors"],
                "negative_factors": score["negative_factors"],
                "risk_factors": score["risk_factors"],
            }
        )
    radar.sort(key=lambda row: float(row["us_market_score"]), reverse=True)

    result = {
        "job": "us-premarket-linkage",
        "status": "completed",
        "started_at": started_at.isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "updated_us_market_symbols": len(linkage),
        "updated_us_linkage_scores": len(radar),
        "generated_pre_open_radar": True,
        "linkage": linkage,
        "radar": radar,
    }
    if session is not None:
        result["persisted"] = persist_us_premarket_result(session, result)
    return result

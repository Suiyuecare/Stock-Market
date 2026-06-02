from datetime import datetime
from typing import Dict, List, Optional

from app.schemas import TechnicalIndicators
from app.services.data_providers.mock_provider import MockMarketDataProvider
from app.services.indicators import build_technical_indicators
from app.services.scoring.chip_score import calculate_chip_score
from app.services.scoring.final_prediction_score import build_signal
from app.services.scoring.technical_score import calculate_technical_score


def run_tw_after_close_job(provider: Optional[MockMarketDataProvider] = None) -> Dict[str, object]:
    """Run the Taiwan after-market mock pipeline and return write-ready artifacts."""
    started_at = datetime.utcnow()
    data_provider = provider or MockMarketDataProvider()
    artifacts: List[Dict[str, object]] = []

    for instrument in data_provider.get_instruments():
        symbol = str(instrument["symbol"])
        series = data_provider.get_price_series(symbol)
        indicators_payload = build_technical_indicators(series["highs"], series["lows"], series["closes"], series["volumes"])
        indicators = TechnicalIndicators(**indicators_payload)
        technical_score = calculate_technical_score(indicators, series["closes"], series["volumes"])
        chip_score = calculate_chip_score(symbol)
        signal = build_signal(instrument)

        artifacts.append(
            {
                "stock_id": symbol,
                "stock_name": instrument["name"],
                "latest_close": series["closes"][-1],
                "latest_volume": series["volumes"][-1],
                "technical_indicators": {key: value for key, value in indicators_payload.items() if key != "signals"},
                "technical_score": technical_score,
                "chip_score": chip_score,
                "factor_score": {
                    "BullishScore": signal.bullish_score,
                    "RiskAdjustedScore": signal.risk_adjusted_score,
                    "probability_up_1d": signal.probability_up_1d,
                    "probability_up_5d": signal.probability_up_5d,
                    "probability_up_20d": signal.probability_up_20d,
                    "confidence": signal.confidence,
                },
            }
        )

    return {
        "job": "tw-after-close",
        "status": "completed",
        "started_at": started_at.isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "updated_prices": len(artifacts),
        "updated_institutional_rows": len(artifacts),
        "calculated_technical_indicators": len(artifacts),
        "calculated_factor_scores": len(artifacts),
        "stocks": artifacts,
    }

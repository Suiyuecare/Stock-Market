from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.schemas import NewsEvent, NewsParseRequest
from app.services.data_providers.mock_provider import MockMarketDataProvider
from app.services.jobs.persistence import persist_news_ingestion_result
from app.services.news_parser import NewsParser
from app.services.scoring.news_score import calculate_news_score


def run_news_ingestion_job(
    provider: Optional[MockMarketDataProvider] = None,
    parser: Optional[NewsParser] = None,
    session: Optional[Session] = None,
) -> Dict[str, object]:
    """Ingest mock news, classify events, and calculate per-stock NewsScore payloads."""
    started_at = datetime.utcnow()
    data_provider = provider or MockMarketDataProvider()
    event_parser = parser or NewsParser()
    stocks: List[Dict[str, object]] = []
    events_ingested = 0
    events_classified = 0

    for instrument in data_provider.get_instruments():
        symbol = str(instrument["symbol"])
        raw_events = data_provider.get_news(symbol)
        classified_events = []
        for raw_event in raw_events:
            parsed = event_parser.parse(
                NewsParseRequest(
                    title=str(raw_event["title"]),
                    body=str(raw_event.get("summary", raw_event["title"])),
                    source=str(raw_event["source"]),
                    published_at=raw_event["published_at"],
                )
            )
            event_payload = {
                **raw_event,
                "summary": parsed.summary,
                "classified_sentiment": parsed.sentiment,
                "classified_impact_score": parsed.impact_score,
                "parser_reasons": parsed.reasons,
            }
            classified_events.append(event_payload)
            events_classified += 1

        news_events = [NewsEvent(**event) for event in raw_events]
        news_score = calculate_news_score(news_events)
        events_ingested += len(raw_events)
        stocks.append(
            {
                "stock_id": symbol,
                "stock_name": instrument["name"],
                "events": classified_events,
                "news_score": news_score,
            }
        )

    result = {
        "job": "news-ingestion",
        "status": "completed",
        "started_at": started_at.isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "events_ingested": events_ingested,
        "events_classified": events_classified,
        "updated_news_scores": len(stocks),
        "stocks": stocks,
    }
    if session is not None:
        result["persisted"] = persist_news_ingestion_result(session, result)
    return result

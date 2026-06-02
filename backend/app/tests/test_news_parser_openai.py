from datetime import datetime, timezone

from app.schemas import NewsParseRequest
from app.services.news_parser import (
    OPENAI_NEWS_PARSER_ENDPOINTS,
    OPENAI_NEWS_PARSER_FIELDS,
    OPENAI_NEWS_PARSER_TASKS,
    NewsParser,
)


def test_openai_news_parser_exposes_official_api_endpoints() -> None:
    parser = NewsParser()

    assert parser.endpoints["platform"] == "https://platform.openai.com/"
    assert parser.endpoints["api_reference"].endswith("/docs/api-reference")
    assert parser.endpoints["responses_api"] == "https://api.openai.com/v1/responses"
    assert parser.endpoints["api_keys"] == "https://platform.openai.com/api-keys"
    assert parser.endpoints["pricing"] == "https://openai.com/api/pricing/"


def test_openai_news_parser_tracks_ai_classification_tasks() -> None:
    assert "news_summary" in OPENAI_NEWS_PARSER_TASKS
    assert "event_classification" in OPENAI_NEWS_PARSER_TASKS
    assert "company_ticker_matching" in OPENAI_NEWS_PARSER_TASKS
    assert "us_tw_supply_chain_reasoning" in OPENAI_NEWS_PARSER_TASKS
    assert "earnings_call_summary" in OPENAI_NEWS_PARSER_TASKS


def test_openai_news_parser_tracks_structured_output_fields() -> None:
    assert "summary" in OPENAI_NEWS_PARSER_FIELDS
    assert "tickers" in OPENAI_NEWS_PARSER_FIELDS
    assert "related_tw_stock_ids" in OPENAI_NEWS_PARSER_FIELDS
    assert "related_us_symbols" in OPENAI_NEWS_PARSER_FIELDS
    assert "event_type" in OPENAI_NEWS_PARSER_FIELDS
    assert "impact_score" in OPENAI_NEWS_PARSER_FIELDS
    assert "confidence" in OPENAI_NEWS_PARSER_FIELDS


def test_news_parser_rule_fallback_keeps_contract_without_api_call() -> None:
    parser = NewsParser()
    response = parser._parse_with_rules(
        NewsParseRequest(
            title="NVDA AI demand lifts TSM 2330 supply chain",
            body="AI growth and demand support semiconductor supply chain sentiment.",
            source="mock",
            published_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
    )

    assert "2330" in response.tickers
    assert "NVDA" in response.tickers
    assert response.sentiment == "positive"
    assert response.impact_score > 0
    assert "rule-based MVP parser" in response.reasons

from app.config import get_settings
from app.schemas import NewsParseRequest, NewsParseResponse

OPENAI_NEWS_PARSER_ENDPOINTS = {
    "platform": "https://platform.openai.com/",
    "api_reference": "https://platform.openai.com/docs/api-reference",
    "responses_api": "https://api.openai.com/v1/responses",
    "api_keys": "https://platform.openai.com/api-keys",
    "pricing": "https://openai.com/api/pricing/",
}

OPENAI_NEWS_PARSER_TASKS = [
    "news_summary",
    "sentiment_classification",
    "event_classification",
    "company_ticker_matching",
    "us_tw_supply_chain_reasoning",
    "earnings_call_summary",
]

OPENAI_NEWS_PARSER_FIELDS = [
    "summary",
    "tickers",
    "related_tw_stock_ids",
    "related_us_symbols",
    "event_type",
    "sentiment",
    "impact_score",
    "confidence",
    "reasons",
]


class NewsParser:
    endpoints = OPENAI_NEWS_PARSER_ENDPOINTS
    openai_tasks = OPENAI_NEWS_PARSER_TASKS
    structured_fields = OPENAI_NEWS_PARSER_FIELDS

    def parse(self, request: NewsParseRequest) -> NewsParseResponse:
        settings = get_settings()
        if settings.llm_provider == "openai" and settings.openai_api_key:
            return self._parse_with_openai(request)

        return self._parse_with_rules(request)

    def _parse_with_openai(self, request: NewsParseRequest) -> NewsParseResponse:
        # Keep the contract stable before enabling live Responses API calls.
        return self._parse_with_rules(request)

    def _parse_with_rules(self, request: NewsParseRequest) -> NewsParseResponse:
        text = f"{request.title} {request.body}".upper()
        tickers = [ticker for ticker in ["2330", "2454", "TSM", "NVDA", "AAPL"] if ticker in text]
        sentiment = "positive" if any(word in text for word in ["AI", "GROWTH", "上修", "需求"]) else "neutral"
        impact_score = 0.6 if sentiment == "positive" else 0.0

        return NewsParseResponse(
            summary=request.title,
            tickers=tickers,
            sentiment=sentiment,
            impact_score=impact_score,
            reasons=["rule-based MVP parser", "LLM provider interface is ready"],
        )

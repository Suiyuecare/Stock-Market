from app.config import get_settings
from app.schemas import NewsParseRequest, NewsParseResponse


class NewsParser:
    def parse(self, request: NewsParseRequest) -> NewsParseResponse:
        settings = get_settings()
        if settings.llm_provider == "openai" and settings.openai_api_key:
            return self._parse_with_openai(request)

        return self._parse_with_rules(request)

    def _parse_with_openai(self, request: NewsParseRequest) -> NewsParseResponse:
        # Placeholder for the provider implementation. Keep the contract stable first.
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

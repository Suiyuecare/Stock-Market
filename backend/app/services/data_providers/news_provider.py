from app.services.data_providers.base import NewsDataProvider


class NewsProvider(NewsDataProvider):
    """Placeholder for licensed news/event provider integration."""

    def get_news(self, symbol: str):
        return []

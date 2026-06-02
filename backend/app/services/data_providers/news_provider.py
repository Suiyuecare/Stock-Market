from app.services.data_providers.base import NewsDataProvider

NEWS_ENDPOINTS = {
    "cna_rss_documentation": "https://www.cna.com.tw/about/rss.aspx",
    "cna_finance_rss": "https://feeds.feedburner.com/rsscna/finance",
    "cna_technology_rss": "https://feeds.feedburner.com/rsscna/technology",
    "cnyes_openapi_documentation": "https://openapi.api.cnyes.com/swagger-ui.html",
    "cnyes_openapi_base": "https://openapi.api.cnyes.com/",
    "newsapi_documentation": "https://newsapi.org/docs",
    "newsapi_rest_base": "https://newsapi.org/v2",
    "newsapi_everything_endpoint": "https://newsapi.org/v2/everything",
    "reuters_api_integrations": "https://reutersagency.com/content-delivery-platforms/api-integrations/",
    "lseg_news_api": "https://developers.lseg.com/en/api-catalog/refinitiv-data-platform/news-API",
    "thomson_reuters_developer_portal": "https://developers.thomsonreuters.com/",
    "newsdata_io_documentation": "https://newsdata.io/documentation",
    "thenewsapi_documentation": "https://www.thenewsapi.com/documentation",
}

NEWS_NORMALIZED_FIELDS = [
    "event_time",
    "market",
    "stock_id",
    "related_symbol",
    "related_industry",
    "source",
    "title",
    "summary",
    "url",
    "sentiment_score",
    "event_type",
    "impact_score",
    "confidence",
]

NEWS_EVENT_TYPES = [
    "earnings",
    "revenue",
    "guidance",
    "material_information",
    "industry",
    "supply_chain",
    "macro",
    "regulatory",
    "geopolitical",
    "risk",
]


class NewsProvider(NewsDataProvider):
    """Placeholder for licensed news/event provider integration.

    CNA RSS can seed MVP news events when terms allow. Cnyes, NewsAPI,
    Reuters/LSEG, NewsData.io, and TheNewsAPI remain disabled until API keys,
    commercial rights, and redistribution/display rules are configured outside
    this repository.
    """

    endpoints = NEWS_ENDPOINTS
    normalized_fields = NEWS_NORMALIZED_FIELDS
    event_types = NEWS_EVENT_TYPES

    def get_news(self, symbol: str):
        return []

from app.services.data_providers.news_provider import (
    NEWS_ENDPOINTS,
    NEWS_EVENT_TYPES,
    NEWS_NORMALIZED_FIELDS,
    NewsProvider,
)


def test_news_provider_exposes_rss_and_commercial_endpoints() -> None:
    provider = NewsProvider()

    assert provider.endpoints["cna_rss_documentation"] == "https://www.cna.com.tw/about/rss.aspx"
    assert provider.endpoints["cna_finance_rss"].endswith("/rsscna/finance")
    assert NEWS_ENDPOINTS["cnyes_openapi_documentation"].endswith("/swagger-ui.html")
    assert NEWS_ENDPOINTS["newsapi_everything_endpoint"] == "https://newsapi.org/v2/everything"
    assert NEWS_ENDPOINTS["lseg_news_api"].endswith("/news-API")
    assert NEWS_ENDPOINTS["thenewsapi_documentation"].endswith("/documentation")


def test_news_provider_tracks_normalized_event_fields() -> None:
    assert "event_time" in NEWS_NORMALIZED_FIELDS
    assert "source" in NEWS_NORMALIZED_FIELDS
    assert "title" in NEWS_NORMALIZED_FIELDS
    assert "sentiment_score" in NEWS_NORMALIZED_FIELDS
    assert "impact_score" in NEWS_NORMALIZED_FIELDS
    assert "confidence" in NEWS_NORMALIZED_FIELDS


def test_news_provider_tracks_scoring_event_types() -> None:
    assert "earnings" in NEWS_EVENT_TYPES
    assert "revenue" in NEWS_EVENT_TYPES
    assert "supply_chain" in NEWS_EVENT_TYPES
    assert "geopolitical" in NEWS_EVENT_TYPES

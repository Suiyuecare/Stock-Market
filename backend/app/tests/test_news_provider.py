from app.services.data_providers.news_provider import (
    NEWS_ENDPOINTS,
    NEWS_EVENT_TYPES,
    NEWS_NORMALIZED_FIELDS,
    NewsProvider,
    normalize_twse_material_information,
    parse_rss_feed,
)


def test_news_provider_exposes_rss_and_commercial_endpoints() -> None:
    provider = NewsProvider()

    assert provider.endpoints["cna_rss_documentation"] == "https://www.cna.com.tw/about/rss.aspx"
    assert provider.endpoints["cna_finance_rss"].endswith("/rsscna/finance")
    assert NEWS_ENDPOINTS["cnyes_openapi_documentation"].endswith("/swagger-ui.html")
    assert NEWS_ENDPOINTS["newsapi_everything_endpoint"] == "https://newsapi.org/v2/everything"
    assert NEWS_ENDPOINTS["twse_material_information"].endswith("/opendata/t187ap04_L")
    assert NEWS_ENDPOINTS["twse_exchange_news"].endswith("/news/newsList")
    assert NEWS_ENDPOINTS["chinatimes_rss_documentation"].startswith("https://www.chinatimes.com/")
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


def test_news_provider_parses_cna_rss_items() -> None:
    xml = """
    <rss version="2.0">
      <channel>
        <item>
          <title>半導體景氣回溫</title>
          <description><![CDATA[AI 需求帶動供應鏈。]]></description>
          <media:content xmlns:media="http://search.yahoo.com/mrss/" url="https://example.com/image.jpg" />
          <link>https://example.com/news/1</link>
          <pubDate>Wed, 03 Jun 2026 08:00:00 GMT</pubDate>
        </item>
      </channel>
    </rss>
    """

    events = parse_rss_feed(xml, "CNA Finance RSS")

    assert events[0]["source"] == "CNA Finance RSS"
    assert events[0]["title"] == "半導體景氣回溫"
    assert events[0]["summary"] == "AI 需求帶動供應鏈。"
    assert events[0]["url"] == "https://example.com/news/1"
    assert events[0]["image_url"] == "https://example.com/image.jpg"
    assert events[0]["event_type"] == "supply_chain"


def test_news_provider_normalizes_twse_material_information() -> None:
    event = normalize_twse_material_information(
        {
            "公司代號": "2330",
            "公司名稱": "台積電",
            "發言日期": "1150603",
            "發言時間": "153000",
            "主旨": "法說會說明 AI 需求成長",
            "說明": "客戶需求成長，資本支出維持。",
        },
        "https://openapi.twse.com.tw/v1/opendata/t187ap04_L",
    )

    assert event is not None
    assert event["stock_id"] == "2330"
    assert event["related_symbols"] == ["2330"]
    assert event["published_at"] == "2026-06-03T15:30:00+08:00"
    assert event["sentiment"] == "positive"

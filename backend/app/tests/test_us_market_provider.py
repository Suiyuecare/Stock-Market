from app.services.data_providers.us_market_provider import US_MARKET_ENDPOINTS, US_MARKET_PROVIDER_PRIORITY, USMarketProvider


def test_us_market_provider_exposes_global_market_endpoints() -> None:
    provider = USMarketProvider()

    assert provider.endpoints["massive_polygon_docs"] == "https://massive.com/docs"
    assert US_MARKET_ENDPOINTS["massive_polygon_rest_base"] == "https://api.polygon.io"
    assert US_MARKET_ENDPOINTS["massive_polygon_websocket_stocks"] == "wss://socket.polygon.io/stocks"
    assert US_MARKET_ENDPOINTS["finnhub_rest_base"] == "https://finnhub.io/api/v1"
    assert US_MARKET_ENDPOINTS["nasdaq_data_link_api"] == "https://data.nasdaq.com/api/v3"
    assert US_MARKET_ENDPOINTS["alpha_vantage_base"] == "https://www.alphavantage.co/query"


def test_us_market_provider_tracks_priority_order() -> None:
    assert US_MARKET_PROVIDER_PRIORITY[0] == "massive_polygon"
    assert "cme" in US_MARKET_PROVIDER_PRIORITY
    assert "ice" in US_MARKET_PROVIDER_PRIORITY

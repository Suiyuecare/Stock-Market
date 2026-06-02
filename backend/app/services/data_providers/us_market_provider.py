from typing import Dict

US_MARKET_ENDPOINTS = {
    "massive_polygon_docs": "https://massive.com/docs",
    "massive_polygon_rest_base": "https://api.polygon.io",
    "massive_polygon_websocket_stocks": "wss://socket.polygon.io/stocks",
    "finnhub_docs": "https://finnhub.io/docs/api",
    "finnhub_rest_base": "https://finnhub.io/api/v1",
    "nasdaq_data_link_docs": "https://docs.data.nasdaq.com/",
    "nasdaq_data_link_api": "https://data.nasdaq.com/api/v3",
    "nasdaq_data_link_api_product": "https://www.nasdaq.com/solutions/data/nasdaq-data-link/api",
    "alpha_vantage_docs": "https://www.alphavantage.co/documentation/",
    "alpha_vantage_base": "https://www.alphavantage.co/query",
    "cme_market_data_apis": "https://www.cmegroup.com/market-data/market-data-api.html",
    "cme_realtime_futures_options_api": "https://www.cmegroup.com/market-data/real-time-futures-and-options-data-api.html",
    "cme_reference_data_api": "https://www.cmegroup.com/trading/market-tech-and-data-services/cme-reference-data-api.html",
    "ice_developer_center": "https://developer.theice.com/hc/en-us",
    "ice_commodity_energy_data": "https://developer.ice.com/fixed-income-data-services/catalog/ice-data-derivatives-commodity-energy-data",
    "intrinio_docs": "https://docs.intrinio.com/documentation/api_v2/getting_started",
    "twelve_data_docs": "https://twelvedata.com/docs",
    "eodhd_api": "https://eodhd.com/",
}

US_MARKET_PROVIDER_PRIORITY = [
    "massive_polygon",
    "finnhub",
    "cme",
    "nasdaq_data_link",
    "alpha_vantage",
    "intrinio",
    "twelve_data",
    "eodhd",
    "ice",
]


class USMarketProvider:
    """Placeholder for licensed US and global market linkage data."""

    endpoints = US_MARKET_ENDPOINTS
    provider_priority = US_MARKET_PROVIDER_PRIORITY

    def get_linkage_scores(self) -> Dict[str, float]:
        return {}

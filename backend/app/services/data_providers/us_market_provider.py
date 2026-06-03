from typing import Any, Dict, Optional

import httpx

from app.config import get_settings

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
    """US/global market linkage provider with keyed API adapters.

    Public no-key US quotes are not reliable enough for production. This
    provider enables Finnhub and Alpha Vantage when keys exist, and otherwise
    keeps deterministic linkage values available through the mock provider.
    """

    endpoints = US_MARKET_ENDPOINTS
    provider_priority = US_MARKET_PROVIDER_PRIORITY

    def __init__(self, client: Optional[httpx.Client] = None, timeout: float = 10.0) -> None:
        self.client = client or httpx.Client(timeout=timeout, follow_redirects=True)
        self.settings = get_settings()

    def get_linkage_scores(self) -> Dict[str, float]:
        symbols = {
            "NASDAQ": "^IXIC",
            "QQQ": "QQQ",
            "SOX": "^SOX",
            "SMH": "SMH",
            "S&P500": "^GSPC",
            "VIX": "^VIX",
            "TSM_ADR": "TSM",
            "NVDA": "NVDA",
            "AMD": "AMD",
            "AAPL": "AAPL",
            "AVGO": "AVGO",
            "MU": "MU",
            "MSFT": "MSFT",
            "META": "META",
            "GOOGL": "GOOGL",
            "AMZN": "AMZN",
        }
        scores: Dict[str, float] = {}
        for key, ticker in symbols.items():
            change_pct = self.get_us_quote_change_pct(ticker)
            if change_pct is not None:
                scores[key] = round(max(-1.0, min(1.0, change_pct / 8)), 3)
        return scores

    def get_us_quote_change_pct(self, ticker: str) -> Optional[float]:
        if self.settings.finnhub_api_key:
            value = self._finnhub_quote_change_pct(ticker)
            if value is not None:
                return value
        if self.settings.alpha_vantage_api_key:
            value = self._alpha_vantage_quote_change_pct(ticker)
            if value is not None:
                return value
        return None

    def _finnhub_quote_change_pct(self, ticker: str) -> Optional[float]:
        response = self.client.get(
            f"{self.endpoints['finnhub_rest_base']}/quote",
            params={"symbol": ticker, "token": self.settings.finnhub_api_key},
        )
        response.raise_for_status()
        payload = response.json()
        return _number(payload.get("dp"))

    def _alpha_vantage_quote_change_pct(self, ticker: str) -> Optional[float]:
        response = self.client.get(
            self.endpoints["alpha_vantage_base"],
            params={"function": "GLOBAL_QUOTE", "symbol": ticker, "apikey": self.settings.alpha_vantage_api_key},
        )
        response.raise_for_status()
        payload = response.json().get("Global Quote", {})
        return _number(str(payload.get("10. change percent", "")).replace("%", ""))


def _number(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(str(value).replace(",", "").strip())
    except ValueError:
        return None

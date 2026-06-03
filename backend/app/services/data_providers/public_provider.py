from typing import Any, Dict, List, Optional

from app.services.data_providers.base import MarketDataProvider, NewsDataProvider, PriceDataProvider
from app.services.data_providers.mock_provider import MockMarketDataProvider
from app.services.data_providers.mops_provider import MOPSProvider
from app.services.data_providers.news_provider import NewsProvider
from app.services.data_providers.tpex_provider import TPEXProvider
from app.services.data_providers.twse_provider import TWSEProvider


class PublicMarketDataProvider(MarketDataProvider, PriceDataProvider, NewsDataProvider):
    """Composite provider for sources that can be connected without paid keys.

    It prioritizes official public endpoints and falls back to deterministic mock
    data where a normalized historical series is not yet available. This keeps
    jobs and APIs live while making the source boundary explicit.
    """

    def __init__(
        self,
        twse: Optional[TWSEProvider] = None,
        mops: Optional[MOPSProvider] = None,
        tpex: Optional[TPEXProvider] = None,
        news: Optional[NewsProvider] = None,
        fallback: Optional[MockMarketDataProvider] = None,
    ) -> None:
        self.twse = twse or TWSEProvider(timeout=3.0)
        self.mops = mops or MOPSProvider(timeout=3.0)
        self.tpex = tpex or TPEXProvider(timeout=3.0)
        self.news = news or NewsProvider(timeout=3.0)
        self.fallback = fallback or MockMarketDataProvider()

    def get_instruments(self) -> List[Dict[str, Any]]:
        instruments: List[Dict[str, Any]] = []
        for loader in (self.twse.get_instruments, self.tpex.get_instruments):
            try:
                instruments.extend(loader())
            except Exception:
                continue
        if not instruments:
            instruments.extend(self.fallback.get_instruments())
        return unique_instruments(instruments)

    def get_price_series(self, symbol: str) -> Dict[str, List[float]]:
        # Historical K-line normalization is intentionally separate from quote
        # ingestion. Until official history is normalized, keep indicators stable
        # with deterministic sample series rather than mixing incomplete rows.
        return self.fallback.get_price_series(symbol)

    def get_news(self, symbol: str) -> List[Dict[str, Any]]:
        try:
            events = self.news.get_news(symbol)
            return events if events else self.fallback.get_news(symbol)
        except Exception:
            return self.fallback.get_news(symbol)

    def get_us_linkage(self) -> Dict[str, float]:
        return self.fallback.get_us_linkage()


def unique_instruments(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    unique = []
    for item in items:
        symbol = str(item.get("symbol") or item.get("stock_id") or "").strip()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        unique.append(item)
    return unique

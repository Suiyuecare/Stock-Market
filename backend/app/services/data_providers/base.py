from abc import ABC, abstractmethod
from typing import Any, Dict, List


class MarketDataProvider(ABC):
    @abstractmethod
    def get_instruments(self) -> List[Dict[str, Any]]:
        raise NotImplementedError


class PriceDataProvider(ABC):
    @abstractmethod
    def get_price_series(self, symbol: str) -> Dict[str, List[float]]:
        raise NotImplementedError


class NewsDataProvider(ABC):
    @abstractmethod
    def get_news(self, symbol: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

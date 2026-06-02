from app.services.data_providers.base import MarketDataProvider


class TWSEProvider(MarketDataProvider):
    """Placeholder for a legal Taiwan Stock Exchange data provider integration."""

    def get_instruments(self):
        return []

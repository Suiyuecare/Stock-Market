from app.services.data_providers.base import MarketDataProvider
from app.services.data_providers.twse_provider import TWSE_ENDPOINTS

TWSE_LICENSED_ENDPOINTS = {
    "twse_data_eshop": TWSE_ENDPOINTS["twse_data_eshop"],
    "twse_realtime_license": TWSE_ENDPOINTS["twse_realtime_license"],
    "twse_delayed_license": TWSE_ENDPOINTS["twse_delayed_license"],
    "twse_usage_rules": TWSE_ENDPOINTS["twse_usage_rules"],
}


class TWSELicensedProvider(MarketDataProvider):
    """TWSE licensed-data placeholder for future real-time/delayed feeds."""

    endpoints = TWSE_LICENSED_ENDPOINTS
    requires_license = True

    def get_instruments(self):
        return []

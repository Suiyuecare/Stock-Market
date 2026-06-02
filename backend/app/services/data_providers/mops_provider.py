from app.services.data_providers.base import MarketDataProvider
from app.services.data_providers.twse_provider import TWSE_ENDPOINTS

MOPS_ENDPOINTS = {
    "mops_portal": TWSE_ENDPOINTS["mops_portal"],
    "mops_financial_portal": TWSE_ENDPOINTS["mops_financial_portal"],
    "listed_company_profile_csv": TWSE_ENDPOINTS["listed_company_profile_csv"],
    "listed_material_information_csv": TWSE_ENDPOINTS["listed_material_information_csv"],
    "listed_monthly_revenue_csv": TWSE_ENDPOINTS["listed_monthly_revenue_csv"],
}


class MOPSProvider(MarketDataProvider):
    """MOPS/mopsfin provider placeholder for company profiles and disclosures."""

    endpoints = MOPS_ENDPOINTS

    def get_instruments(self):
        return []

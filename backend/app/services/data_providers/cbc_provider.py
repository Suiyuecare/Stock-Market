from app.services.data_providers.taiwan_macro_provider import (
    CBC_API_BASE_URL,
    CBC_ITEM_CODES,
    TaiwanMacroProvider,
)

CBC_ENDPOINTS = {
    "statistics_database": "https://cpx.cbc.gov.tw/",
    "api_docs": "https://cpx.cbc.gov.tw/Data/ExportToAPIInfo",
    "api_endpoint_format": f"{CBC_API_BASE_URL}?FileName={{ITEM_CODE}}",
}


class CBCProvider(TaiwanMacroProvider):
    """Central Bank of Taiwan macro provider placeholder."""

    endpoints = CBC_ENDPOINTS
    item_codes = CBC_ITEM_CODES

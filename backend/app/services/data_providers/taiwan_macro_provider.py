from app.services.data_providers.base import MarketDataProvider

CBC_API_BASE_URL = "https://cpx.cbc.gov.tw/API/DataAPI/Get"
DGBAS_STATISTICS_URL = "https://nstatdb.dgbas.gov.tw/dgbasall/webMain.aspx?k=main"

TAIWAN_MACRO_ENDPOINTS = {
    "cbc_statistics_database": "https://cpx.cbc.gov.tw/",
    "cbc_api_docs": "https://cpx.cbc.gov.tw/Data/ExportToAPIInfo",
    "cbc_api_endpoint_format": f"{CBC_API_BASE_URL}?FileName={{ITEM_CODE}}",
    "dgbas_statistics_database": DGBAS_STATISTICS_URL,
    "dgbas_api_docs_pdf": "https://nstatdb.dgbas.gov.tw/dgbasall/download/API說明文件.pdf",
    "government_open_data_platform": "https://data.gov.tw/",
}

CBC_ITEM_CODES = {
    "exchange_rate_daily": "BP01D01",
    "exchange_rate_monthly": "BP01M01",
    "important_financial_indicators_monthly": "EF01M01",
    "m2_change_monthly": "EF21M01",
    "central_bank_rates_daily": "EG28D01",
    "interbank_call_loan_rate_daily": "EG37D01",
}


class TaiwanMacroProvider(MarketDataProvider):
    """Official Taiwan macro provider placeholder.

    CBC and DGBAS sources are intended for MacroScore inputs such as exchange
    rates, interest rates, M2, CPI, GDP, unemployment, wages, export orders, and
    FX reserves. Live fetching remains disabled until item-code mappings and
    field normalization are implemented.
    """

    cbc_api_base_url = CBC_API_BASE_URL
    dgbas_statistics_url = DGBAS_STATISTICS_URL
    endpoints = TAIWAN_MACRO_ENDPOINTS
    cbc_item_codes = CBC_ITEM_CODES

    def get_instruments(self):
        return []

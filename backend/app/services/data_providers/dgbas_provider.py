from app.services.data_providers.taiwan_macro_provider import TaiwanMacroProvider

DGBAS_ENDPOINTS = {
    "statistics_database": "https://nstatdb.dgbas.gov.tw/dgbasall/webMain.aspx?k=main",
    "api_docs_pdf": "https://nstatdb.dgbas.gov.tw/dgbasall/download/API說明文件.pdf",
}


class DGBASProvider(TaiwanMacroProvider):
    """DGBAS macro statistics provider placeholder."""

    endpoints = DGBAS_ENDPOINTS

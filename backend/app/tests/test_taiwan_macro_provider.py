from app.services.data_providers.taiwan_macro_provider import CBC_ITEM_CODES, TAIWAN_MACRO_ENDPOINTS, TaiwanMacroProvider


def test_taiwan_macro_provider_exposes_official_endpoints() -> None:
    provider = TaiwanMacroProvider()

    assert provider.cbc_api_base_url == "https://cpx.cbc.gov.tw/API/DataAPI/Get"
    assert TAIWAN_MACRO_ENDPOINTS["cbc_api_docs"] == "https://cpx.cbc.gov.tw/Data/ExportToAPIInfo"
    assert TAIWAN_MACRO_ENDPOINTS["cbc_api_endpoint_format"].endswith("FileName={ITEM_CODE}")
    assert TAIWAN_MACRO_ENDPOINTS["dgbas_statistics_database"].startswith("https://nstatdb.dgbas.gov.tw")
    assert TAIWAN_MACRO_ENDPOINTS["government_open_data_platform"] == "https://data.gov.tw/"


def test_taiwan_macro_provider_tracks_cbc_item_codes() -> None:
    assert CBC_ITEM_CODES["exchange_rate_daily"] == "BP01D01"
    assert CBC_ITEM_CODES["m2_change_monthly"] == "EF21M01"
    assert CBC_ITEM_CODES["central_bank_rates_daily"] == "EG28D01"

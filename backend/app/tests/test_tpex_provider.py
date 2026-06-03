from app.services.data_providers.tpex_provider import TPEX_ENDPOINTS, TPEXProvider, normalize_tpex_quote, normalize_tpex_valuation


def test_tpex_provider_exposes_official_endpoints() -> None:
    provider = TPEXProvider()

    assert provider.base_url == "https://www.tpex.org.tw/openapi"
    assert TPEX_ENDPOINTS["openapi_home"] == "https://www.tpex.org.tw/openapi/"
    assert TPEX_ENDPOINTS["swagger_json"] == "https://www.tpex.org.tw/openapi/swagger.json"
    assert TPEX_ENDPOINTS["mainboard_daily_close_quotes"].endswith("/v1/tpex_mainboard_daily_close_quotes")
    assert TPEX_ENDPOINTS["mainboard_peratio_analysis"].endswith("/v1/tpex_mainboard_peratio_analysis")
    assert TPEX_ENDPOINTS["data_purchase"].endswith("/service/data/overview.html")
    assert TPEX_ENDPOINTS["after_market_download_system"] == "https://intd.tpex.org.tw"


def test_tpex_provider_normalizes_quote_rows() -> None:
    quote = normalize_tpex_quote(
        {
            "Date": "1150603",
            "SecuritiesCompanyCode": "3035",
            "CompanyName": "智原",
            "Open": "322",
            "High": "327",
            "Low": "292",
            "Close": "292",
            "Change": "-30",
            "TradingShares": "11,645",
            "TransactionAmount": "3,500,000",
            "TransactionNumber": "1,234",
        }
    )

    assert quote is not None
    assert quote["symbol"] == "3035"
    assert quote["close"] == 292
    assert quote["trade_volume"] == 11645


def test_tpex_provider_normalizes_valuation_rows() -> None:
    valuation = normalize_tpex_valuation(
        {
            "Date": "1150603",
            "SecuritiesCompanyCode": "3035",
            "CompanyName": "智原",
            "PriceEarningRatio": "38.2",
            "YieldRatio": "1.5",
            "PriceBookRatio": "4.8",
            "DividendPerShare": "6.0",
        }
    )

    assert valuation is not None
    assert valuation["symbol"] == "3035"
    assert valuation["pe_ratio"] == 38.2
    assert valuation["dividend_per_share"] == 6.0

from app.services.data_providers.tej_provider import TEJ_DATASET_EXAMPLES, TEJ_ENDPOINTS, TEJProvider


def test_tej_provider_exposes_commercial_endpoints() -> None:
    provider = TEJProvider()

    assert provider.rest_base_url == "https://api.tej.com.tw/api"
    assert TEJ_ENDPOINTS["official_portal"] == "https://api.tej.com.tw/"
    assert TEJ_ENDPOINTS["api_documentation"].endswith("/tej-api-document/")
    assert TEJ_ENDPOINTS["rest_api_documentation"].endswith("/tej-rest-api-document/")
    assert TEJ_ENDPOINTS["rest_base_url"] == "https://api.tej.com.tw/api/"


def test_tej_provider_tracks_dataset_examples() -> None:
    assert TEJ_DATASET_EXAMPLES["taiwan_adjusted_price_daily"] == "TWN/APRCD"

from app.services.data_providers.us_macro_provider import BLS_SERIES_EXAMPLES, FRED_SERIES_EXAMPLES, US_MACRO_ENDPOINTS, USMacroProvider


def test_us_macro_provider_exposes_fred_and_bls_endpoints() -> None:
    provider = USMacroProvider()

    assert provider.endpoints["fred_api_docs"] == "https://fred.stlouisfed.org/docs/api/fred/"
    assert US_MACRO_ENDPOINTS["fred_observations"] == "https://api.stlouisfed.org/fred/series/observations"
    assert US_MACRO_ENDPOINTS["bls_timeseries_v2"] == "https://api.bls.gov/publicAPI/v2/timeseries/data/"


def test_us_macro_provider_tracks_series_examples() -> None:
    assert FRED_SERIES_EXAMPLES["us_10y_treasury"] == "DGS10"
    assert FRED_SERIES_EXAMPLES["effective_fed_funds"] == "DFF"
    assert BLS_SERIES_EXAMPLES["cpi_all_urban_consumers"] == "CUSR0000SA0"
    assert BLS_SERIES_EXAMPLES["unemployment_rate"] == "LNS14000000"

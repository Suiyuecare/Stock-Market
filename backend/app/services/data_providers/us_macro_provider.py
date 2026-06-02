from app.services.data_providers.base import MarketDataProvider

FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"
BLS_TIMESERIES_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

US_MACRO_ENDPOINTS = {
    "fred_api_docs": "https://fred.stlouisfed.org/docs/api/fred/",
    "fred_observations": FRED_OBSERVATIONS_URL,
    "bls_api_docs": "https://www.bls.gov/developers/home.htm",
    "bls_timeseries_v2": BLS_TIMESERIES_URL,
}

FRED_SERIES_EXAMPLES = {
    "us_10y_treasury": "DGS10",
    "us_2y_treasury": "DGS2",
    "effective_fed_funds": "DFF",
    "ice_bofa_high_yield_spread": "BAMLH0A0HYM2",
    "trade_weighted_usd_index": "DTWEXBGS",
}

BLS_SERIES_EXAMPLES = {
    "cpi_all_urban_consumers": "CUSR0000SA0",
    "ppi_all_commodities": "WPU00000000",
    "unemployment_rate": "LNS14000000",
    "nonfarm_payrolls": "CES0000000001",
    "average_hourly_earnings": "CES0500000003",
}


class USMacroProvider(MarketDataProvider):
    """US macro provider placeholder for FRED and BLS.

    These sources can feed USMarketScore and RiskScore with Treasury yields,
    Fed Funds, credit spreads, USD strength, CPI, PPI, unemployment, payrolls,
    and wage data. Live fetching remains disabled until API keys, rate limits,
    and series mappings are configured.
    """

    endpoints = US_MACRO_ENDPOINTS
    fred_series_examples = FRED_SERIES_EXAMPLES
    bls_series_examples = BLS_SERIES_EXAMPLES

    def get_instruments(self):
        return []

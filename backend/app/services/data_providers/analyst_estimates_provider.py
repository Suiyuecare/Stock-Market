from app.services.data_providers.base import MarketDataProvider

ANALYST_ESTIMATES_ENDPOINTS = {
    "factset_developer": "https://developer.factset.com/",
    "factset_estimates_api": "https://developer.factset.com/api-catalog/factset-estimates-api",
    "factset_estimates_report_builder_api": "https://developer.factset.com/api-catalog/factset-estimates-report-builder-api",
    "lseg_ibes_estimates": "https://www.lseg.com/en/data-analytics/financial-data/company-data/ibes-estimates",
    "lseg_estimates_api_for_wealth": "https://developers.lseg.com/en/api-catalog/refinitiv-data-platform/estimates-API",
    "bloomberg_bpipe": "https://professional.bloomberg.com/products/data/enterprise-catalog/real-time-data-feed/",
    "bloomberg_sapi": "https://professional.bloomberg.com/products/data/data-connectivity/server-api/",
    "bloomberg_data_license": "https://professional.bloomberg.com/products/data/data-management/data-license/",
    "bloomberg_web_api_host": "https://api.bloomberg.com",
}

ANALYST_ESTIMATES_FIELDS = [
    "eps_consensus",
    "revenue_consensus",
    "target_price_mean",
    "target_price_high",
    "target_price_low",
    "rating_revision",
    "estimate_revision_direction",
    "analyst_count",
    "analyst_hit_rate",
    "data_freshness",
]


class AnalystEstimatesProvider(MarketDataProvider):
    """Commercial analyst estimates provider placeholder.

    FactSet, LSEG I/B/E/S, and Bloomberg can feed TargetPriceScore with EPS
    consensus, target prices, ratings, estimate revisions, and analyst-quality
    signals. Live fetching remains disabled until commercial licenses,
    credentials, and redistribution rules are configured outside the repository.
    """

    endpoints = ANALYST_ESTIMATES_ENDPOINTS
    normalized_fields = ANALYST_ESTIMATES_FIELDS

    def get_instruments(self):
        return []

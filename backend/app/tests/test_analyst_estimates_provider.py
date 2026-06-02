from app.services.data_providers.analyst_estimates_provider import (
    ANALYST_ESTIMATES_ENDPOINTS,
    ANALYST_ESTIMATES_FIELDS,
    AnalystEstimatesProvider,
)


def test_analyst_estimates_provider_exposes_commercial_endpoints() -> None:
    provider = AnalystEstimatesProvider()

    assert provider.endpoints["factset_developer"] == "https://developer.factset.com/"
    assert ANALYST_ESTIMATES_ENDPOINTS["factset_estimates_api"].endswith("/factset-estimates-api")
    assert ANALYST_ESTIMATES_ENDPOINTS["lseg_ibes_estimates"].endswith("/ibes-estimates")
    assert ANALYST_ESTIMATES_ENDPOINTS["lseg_estimates_api_for_wealth"].endswith("/estimates-API")
    assert ANALYST_ESTIMATES_ENDPOINTS["bloomberg_web_api_host"] == "https://api.bloomberg.com"


def test_analyst_estimates_provider_tracks_normalized_fields() -> None:
    assert "eps_consensus" in ANALYST_ESTIMATES_FIELDS
    assert "target_price_mean" in ANALYST_ESTIMATES_FIELDS
    assert "rating_revision" in ANALYST_ESTIMATES_FIELDS
    assert "analyst_hit_rate" in ANALYST_ESTIMATES_FIELDS

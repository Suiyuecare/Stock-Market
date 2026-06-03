from app.services.data_providers.analyst_estimates_provider import (
    ANALYST_ESTIMATES_ENDPOINTS,
    ANALYST_ESTIMATES_FIELDS,
    AnalystEstimatesProvider,
    extract_target_price_mentions,
    normalize_fmp_target_price,
)


def test_analyst_estimates_provider_exposes_commercial_endpoints() -> None:
    provider = AnalystEstimatesProvider()

    assert provider.endpoints["factset_developer"] == "https://developer.factset.com/"
    assert ANALYST_ESTIMATES_ENDPOINTS["factset_estimates_api"].endswith("/factset-estimates-api")
    assert ANALYST_ESTIMATES_ENDPOINTS["lseg_ibes_estimates"].endswith("/ibes-estimates")
    assert ANALYST_ESTIMATES_ENDPOINTS["lseg_estimates_api_for_wealth"].endswith("/estimates-API")
    assert ANALYST_ESTIMATES_ENDPOINTS["bloomberg_web_api_host"] == "https://api.bloomberg.com"
    assert ANALYST_ESTIMATES_ENDPOINTS["fmp_price_target_consensus"].endswith("/price-target-consensus")


def test_analyst_estimates_provider_tracks_normalized_fields() -> None:
    assert "eps_consensus" in ANALYST_ESTIMATES_FIELDS
    assert "target_price_mean" in ANALYST_ESTIMATES_FIELDS
    assert "rating_revision" in ANALYST_ESTIMATES_FIELDS
    assert "analyst_hit_rate" in ANALYST_ESTIMATES_FIELDS


def test_analyst_estimates_provider_normalizes_fmp_target_price() -> None:
    payload = normalize_fmp_target_price(
        "AAPL",
        {
            "targetConsensus": "215.5",
            "targetHigh": "250",
            "targetLow": "180",
            "numberOfAnalystOpinions": "36",
            "currency": "USD",
            "date": "2026-06-03",
        },
    )

    assert payload["target_price_mean"] == 215.5
    assert payload["target_price_high"] == 250
    assert payload["analyst_count"] == 36
    assert payload["source_type"] == "licensed_or_keyed_api"


def test_analyst_estimates_provider_extracts_target_price_mentions() -> None:
    mentions = extract_target_price_mentions("元大投顧看好 AI 需求，將欣興目標價調升至 118 元，評等買進。")

    assert mentions[0]["broker"] == "元大"
    assert mentions[0]["target_price"] == 118
    assert mentions[0]["rating"] == "買進"

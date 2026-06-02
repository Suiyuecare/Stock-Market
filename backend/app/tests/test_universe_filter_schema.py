from app.schemas import UniverseFilterCandidate, UniverseFilterConfig, UniverseFilterResult


def test_universe_filter_config_schema_uses_conservative_defaults() -> None:
    config = UniverseFilterConfig()

    assert config.min_listing_days == 250
    assert config.min_close_price == 10
    assert config.min_avg_turnover_20d_twd == 50_000_000
    assert config.exclude_disposition_stocks is True


def test_universe_filter_candidate_schema_tracks_quality_flags() -> None:
    candidate = UniverseFilterCandidate(
        stock_id="2330",
        listing_days=5000,
        close_price=950,
        avg_turnover_20d_twd=8_000_000_000,
        is_attention_stock=True,
        recent_gap_pct=0.03,
    )

    assert candidate.stock_id == "2330"
    assert candidate.is_attention_stock is True


def test_universe_filter_result_schema_explains_exclusion() -> None:
    result = UniverseFilterResult(
        stock_id="9999",
        included=False,
        exclusion_reasons=["low_liquidity"],
        risk_flags=["low_liquidity"],
    )

    assert result.included is False
    assert result.exclusion_reasons == ["low_liquidity"]

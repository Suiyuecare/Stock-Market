from app.schemas import UniverseFilterCandidate, UniverseFilterConfig
from app.services.universe_filter_engine import UniverseFilterEngine


def _candidate(**overrides: object) -> UniverseFilterCandidate:
    values = {
        "stock_id": "2330",
        "listing_days": 5000,
        "close_price": 950.0,
        "avg_turnover_20d_twd": 8_000_000_000.0,
        "is_full_delivery_stock": False,
        "is_disposition_stock": False,
        "is_attention_stock": False,
        "has_low_liquidity": False,
        "recent_gap_pct": 0.02,
        "has_missing_fundamental_data": False,
    }
    values.update(overrides)
    return UniverseFilterCandidate(**values)


def test_universe_filter_includes_high_quality_candidate() -> None:
    result = UniverseFilterEngine().evaluate(_candidate())

    assert result.included is True
    assert result.exclusion_reasons == []
    assert result.risk_flags == []


def test_universe_filter_excludes_short_history_low_price_and_missing_data() -> None:
    result = UniverseFilterEngine().evaluate(
        _candidate(
            listing_days=40,
            close_price=6.5,
            has_missing_fundamental_data=True,
        )
    )

    assert result.included is False
    assert "listing_history_too_short" in result.exclusion_reasons
    assert "close_price_below_minimum" in result.exclusion_reasons
    assert "missing_fundamental_data" in result.exclusion_reasons


def test_universe_filter_excludes_illiquid_and_special_risk_stocks() -> None:
    result = UniverseFilterEngine().evaluate(
        _candidate(
            avg_turnover_20d_twd=10_000_000,
            has_low_liquidity=True,
            is_full_delivery_stock=True,
            is_disposition_stock=True,
        )
    )

    assert result.included is False
    assert "turnover_below_minimum" in result.exclusion_reasons
    assert "low_liquidity" in result.exclusion_reasons
    assert "full_delivery_stock" in result.exclusion_reasons
    assert "disposition_stock" in result.exclusion_reasons


def test_universe_filter_attention_stock_can_be_allowed_outside_conservative_mode() -> None:
    result = UniverseFilterEngine().evaluate(
        _candidate(is_attention_stock=True),
        UniverseFilterConfig(exclude_attention_stocks_for_conservative_mode=False),
    )

    assert result.included is True
    assert "attention_stock" in result.risk_flags
    assert result.exclusion_reasons == []


def test_universe_filter_excludes_recent_extreme_gap() -> None:
    result = UniverseFilterEngine().evaluate(_candidate(recent_gap_pct=-0.12))

    assert result.included is False
    assert "recent_extreme_gap" in result.exclusion_reasons


def test_universe_filter_batch_returns_one_result_per_candidate() -> None:
    results = UniverseFilterEngine().filter([_candidate(stock_id="2330"), _candidate(stock_id="9999", close_price=5)])

    assert len(results) == 2
    assert results[0].included is True
    assert results[1].included is False

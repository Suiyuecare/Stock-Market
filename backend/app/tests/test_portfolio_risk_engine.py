from datetime import date

from app.schemas import PortfolioCandidate, PortfolioRiskConfig, PortfolioRiskState
from app.services.portfolio_risk_engine import PortfolioRiskEngine


def _candidate(stock_id: str, sector: str, score: float, weight: float = 0.12, electronics: bool = True) -> PortfolioCandidate:
    return PortfolioCandidate(
        stock_id=stock_id,
        signal_date=date(2026, 6, 2),
        selection_decision="primary_watchlist",
        score=score,
        sector=sector,
        proposed_weight=weight,
        volatility_20d=0.22,
        is_electronics=electronics,
    )


def test_portfolio_risk_engine_caps_single_stock_weight() -> None:
    result = PortfolioRiskEngine().build(
        [_candidate("2330", "semiconductor", 90, weight=0.25)],
        PortfolioRiskState(),
    )

    assert result.allocations[0].weight == 0.12
    assert "Single-stock weight capped." in result.allocations[0].reasons


def test_portfolio_risk_engine_limits_ai_server_sector_concentration() -> None:
    candidates = [
        _candidate("2382", "ai_server", 95),
        _candidate("3231", "ai_server", 94),
        _candidate("6669", "ai_server", 93),
        _candidate("2356", "ai_server", 92),
        _candidate("2330", "semiconductor", 91),
    ]

    result = PortfolioRiskEngine().build(
        candidates,
        PortfolioRiskState(),
        PortfolioRiskConfig(max_sector_weight=0.3, max_new_signals_per_day=5),
    )

    ai_weight = sum(allocation.weight for allocation in result.allocations if allocation.sector == "ai_server")
    assert round(ai_weight, 6) == 0.3
    assert any("Sector concentration cap applied." in allocation.reasons for allocation in result.allocations)


def test_portfolio_risk_engine_limits_daily_new_signals() -> None:
    candidates = [_candidate(str(2300 + index), "semiconductor", 100 - index) for index in range(8)]

    result = PortfolioRiskEngine().build(
        candidates,
        PortfolioRiskState(),
        PortfolioRiskConfig(max_new_signals_per_day=3, max_holdings=10),
    )

    assert len(result.allocations) == 3
    assert len(result.excluded) == 5


def test_portfolio_risk_engine_deleverages_for_drawdown_volatility_losses_and_vix() -> None:
    result = PortfolioRiskEngine().build(
        [_candidate("2330", "semiconductor", 95, weight=0.12)],
        PortfolioRiskState(
            current_drawdown=0.18,
            portfolio_volatility=0.31,
            consecutive_losses=4,
            vix_level=30,
        ),
    )

    allocation = result.allocations[0]
    assert allocation.weight < 0.05
    assert "max_drawdown_limit" in result.risk_flags
    assert "max_volatility_limit" in result.risk_flags
    assert "consecutive_loss_deleveraging" in result.risk_flags
    assert "high_vix_deleveraging" in result.risk_flags


def test_portfolio_risk_engine_reduces_electronics_when_us_futures_weak() -> None:
    result = PortfolioRiskEngine().build(
        [
            _candidate("2330", "semiconductor", 95, weight=0.1, electronics=True),
            _candidate("2912", "retail", 90, weight=0.1, electronics=False),
        ],
        PortfolioRiskState(us_futures_return=-0.02),
    )

    electronics = next(allocation for allocation in result.allocations if allocation.stock_id == "2330")
    retail = next(allocation for allocation in result.allocations if allocation.stock_id == "2912")

    assert electronics.weight == 0.065
    assert retail.weight == 0.1
    assert "weak_us_futures" in result.risk_flags


def test_portfolio_risk_engine_ignores_non_primary_watchlist_candidates() -> None:
    candidate = _candidate("2330", "semiconductor", 95)
    candidate.selection_decision = "high_risk_watchlist"

    result = PortfolioRiskEngine().build([candidate], PortfolioRiskState())

    assert result.allocations == []
    assert result.excluded == []

from datetime import date

from app.schemas import (
    PortfolioAllocation,
    PortfolioCandidate,
    PortfolioRiskConfig,
    PortfolioRiskResult,
    PortfolioRiskState,
)


def test_portfolio_candidate_schema_tracks_simulated_holding_inputs() -> None:
    candidate = PortfolioCandidate(
        stock_id="2330",
        signal_date=date(2026, 6, 2),
        selection_decision="primary_watchlist",
        score=92,
        sector="semiconductor",
        proposed_weight=0.12,
        volatility_20d=0.2,
        is_electronics=True,
    )

    assert candidate.stock_id == "2330"
    assert candidate.is_electronics is True


def test_portfolio_risk_config_schema_tracks_limits() -> None:
    config = PortfolioRiskConfig(max_single_stock_weight=0.1, max_sector_weight=0.3, max_new_signals_per_day=5)

    assert config.max_single_stock_weight == 0.1
    assert config.max_sector_weight == 0.3
    assert config.max_new_signals_per_day == 5


def test_portfolio_risk_result_schema_returns_allocations_and_flags() -> None:
    allocation = PortfolioAllocation(
        stock_id="2330",
        sector="semiconductor",
        weight=0.08,
        original_weight=0.12,
        risk_adjusted_weight=0.08,
        reasons=["High-VIX exposure reduction applied."],
    )
    result = PortfolioRiskResult(
        signal_date=date(2026, 6, 2),
        total_target_exposure=0.08,
        allocations=[allocation],
        excluded=[],
        risk_flags=["high_vix_deleveraging"],
        notes=["High VIX requires lower simulated exposure."],
    )

    assert result.allocations[0].weight == 0.08
    assert result.risk_flags == ["high_vix_deleveraging"]


def test_portfolio_risk_state_schema_tracks_market_controls() -> None:
    state = PortfolioRiskState(
        current_drawdown=0.12,
        portfolio_volatility=0.26,
        consecutive_losses=2,
        vix_level=24,
        us_futures_return=-0.005,
    )

    assert state.current_drawdown == 0.12
    assert state.us_futures_return == -0.005

from datetime import date
from typing import Dict, List, Tuple

from app.schemas import (
    PortfolioAllocation,
    PortfolioCandidate,
    PortfolioRiskConfig,
    PortfolioRiskResult,
    PortfolioRiskState,
)


class PortfolioRiskEngine:
    """Build a simulated research portfolio with concentration and market-risk controls."""

    def build(
        self,
        candidates: List[PortfolioCandidate],
        state: PortfolioRiskState,
        config: PortfolioRiskConfig = PortfolioRiskConfig(),
    ) -> PortfolioRiskResult:
        signal_date = candidates[0].signal_date if candidates else date.today()
        risk_flags, notes = self._portfolio_risk_flags(state, config)
        ranked = sorted(
            [candidate for candidate in candidates if candidate.selection_decision == "primary_watchlist"],
            key=lambda candidate: candidate.score,
            reverse=True,
        )

        allocations: List[PortfolioAllocation] = []
        excluded: List[PortfolioAllocation] = []
        sector_weights: Dict[str, float] = {}

        for candidate in ranked:
            if len(allocations) >= config.max_holdings or len(allocations) >= config.max_new_signals_per_day:
                excluded.append(self._excluded(candidate, "Portfolio holding or daily new-signal limit reached."))
                continue

            capped_weight, reasons = self._single_stock_weight(candidate, config)
            capped_weight, sector_reason = self._sector_weight(candidate, capped_weight, sector_weights, config)
            if sector_reason:
                reasons.append(sector_reason)
            capped_weight, market_reasons = self._apply_market_risk(candidate, capped_weight, state, config)
            reasons.extend(market_reasons)

            if capped_weight <= 0:
                excluded.append(self._excluded(candidate, "Sector limit left no available capacity."))
                continue

            allocation = PortfolioAllocation(
                stock_id=candidate.stock_id,
                sector=candidate.sector,
                weight=round(capped_weight, 6),
                original_weight=round(candidate.proposed_weight, 6),
                risk_adjusted_weight=round(capped_weight, 6),
                reasons=reasons,
            )
            allocations.append(allocation)
            sector_weights[candidate.sector] = sector_weights.get(candidate.sector, 0.0) + capped_weight

        total_exposure = round(sum(allocation.weight for allocation in allocations), 6)
        return PortfolioRiskResult(
            signal_date=signal_date,
            total_target_exposure=total_exposure,
            allocations=allocations,
            excluded=excluded,
            risk_flags=risk_flags,
            notes=notes,
        )

    def _portfolio_risk_flags(
        self,
        state: PortfolioRiskState,
        config: PortfolioRiskConfig,
    ) -> Tuple[List[str], List[str]]:
        risk_flags: List[str] = []
        notes: List[str] = []
        if state.current_drawdown >= config.max_drawdown_limit:
            risk_flags.append("max_drawdown_limit")
            notes.append("Current drawdown exceeds the configured risk limit.")
        if state.portfolio_volatility >= config.max_volatility_limit:
            risk_flags.append("max_volatility_limit")
            notes.append("Portfolio volatility exceeds the configured risk limit.")
        if state.consecutive_losses >= config.consecutive_loss_limit:
            risk_flags.append("consecutive_loss_deleveraging")
            notes.append("Consecutive losses require lower simulated exposure.")
        if state.vix_level >= config.high_vix_threshold:
            risk_flags.append("high_vix_deleveraging")
            notes.append("High VIX requires lower simulated exposure.")
        if state.us_futures_return <= config.weak_us_futures_threshold:
            risk_flags.append("weak_us_futures")
            notes.append("Weak US futures require lower electronics exposure.")
        return risk_flags, notes

    def _single_stock_weight(
        self,
        candidate: PortfolioCandidate,
        config: PortfolioRiskConfig,
    ) -> Tuple[float, List[str]]:
        weight = min(candidate.proposed_weight, config.max_single_stock_weight)
        reasons: List[str] = []
        if weight < candidate.proposed_weight:
            reasons.append("Single-stock weight capped.")
        return weight, reasons

    def _sector_weight(
        self,
        candidate: PortfolioCandidate,
        weight: float,
        sector_weights: Dict[str, float],
        config: PortfolioRiskConfig,
    ) -> Tuple[float, str]:
        remaining = max(0.0, config.max_sector_weight - sector_weights.get(candidate.sector, 0.0))
        capped = min(weight, remaining)
        if capped < weight:
            return capped, "Sector concentration cap applied."
        return capped, ""

    def _apply_market_risk(
        self,
        candidate: PortfolioCandidate,
        weight: float,
        state: PortfolioRiskState,
        config: PortfolioRiskConfig,
    ) -> Tuple[float, List[str]]:
        reasons: List[str] = []
        adjusted = weight
        if state.current_drawdown >= config.max_drawdown_limit:
            adjusted *= config.drawdown_exposure_multiplier
            reasons.append("Drawdown deleveraging applied.")
        if state.portfolio_volatility >= config.max_volatility_limit:
            adjusted *= config.volatility_exposure_multiplier
            reasons.append("Volatility deleveraging applied.")
        if state.consecutive_losses >= config.consecutive_loss_limit:
            adjusted *= config.consecutive_loss_exposure_multiplier
            reasons.append("Consecutive-loss deleveraging applied.")
        if state.vix_level >= config.high_vix_threshold:
            adjusted *= config.high_vix_exposure_multiplier
            reasons.append("High-VIX exposure reduction applied.")
        if candidate.is_electronics and state.us_futures_return <= config.weak_us_futures_threshold:
            adjusted *= config.weak_us_futures_electronics_multiplier
            reasons.append("Weak US futures reduced electronics exposure.")
        return adjusted, reasons

    def _excluded(self, candidate: PortfolioCandidate, reason: str) -> PortfolioAllocation:
        return PortfolioAllocation(
            stock_id=candidate.stock_id,
            sector=candidate.sector,
            weight=0.0,
            original_weight=round(candidate.proposed_weight, 6),
            risk_adjusted_weight=0.0,
            reasons=[reason],
        )

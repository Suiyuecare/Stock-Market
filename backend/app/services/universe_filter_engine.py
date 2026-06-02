from typing import List

from app.schemas import UniverseFilterCandidate, UniverseFilterConfig, UniverseFilterResult


class UniverseFilterEngine:
    """Exclude low-quality samples before modeling and signal generation."""

    def evaluate(
        self,
        candidate: UniverseFilterCandidate,
        config: UniverseFilterConfig = UniverseFilterConfig(),
    ) -> UniverseFilterResult:
        exclusion_reasons: List[str] = []
        risk_flags: List[str] = []

        if candidate.listing_days < config.min_listing_days:
            exclusion_reasons.append("listing_history_too_short")
            risk_flags.append("insufficient_history")

        if candidate.close_price < config.min_close_price:
            exclusion_reasons.append("close_price_below_minimum")
            risk_flags.append("low_price")

        if candidate.avg_turnover_20d_twd < config.min_avg_turnover_20d_twd:
            risk_flags.append("turnover_below_minimum")
            if config.exclude_low_liquidity:
                exclusion_reasons.append("turnover_below_minimum")

        if candidate.has_low_liquidity:
            risk_flags.append("low_liquidity")
            if config.exclude_low_liquidity:
                exclusion_reasons.append("low_liquidity")

        if candidate.is_full_delivery_stock:
            risk_flags.append("full_delivery_stock")
            if config.exclude_full_delivery_stocks:
                exclusion_reasons.append("full_delivery_stock")

        if candidate.is_disposition_stock:
            risk_flags.append("disposition_stock")
            if config.exclude_disposition_stocks:
                exclusion_reasons.append("disposition_stock")

        if candidate.is_attention_stock:
            risk_flags.append("attention_stock")
            if config.exclude_attention_stocks_for_conservative_mode:
                exclusion_reasons.append("attention_stock_conservative_mode")

        if abs(candidate.recent_gap_pct) >= config.extreme_gap_threshold:
            risk_flags.append("recent_extreme_gap")
            if config.exclude_recent_extreme_gap:
                exclusion_reasons.append("recent_extreme_gap")

        if candidate.has_missing_fundamental_data:
            risk_flags.append("missing_fundamental_data")
            if config.exclude_missing_fundamental_data:
                exclusion_reasons.append("missing_fundamental_data")

        return UniverseFilterResult(
            stock_id=candidate.stock_id,
            included=not exclusion_reasons,
            exclusion_reasons=sorted(set(exclusion_reasons)),
            risk_flags=sorted(set(risk_flags)),
        )

    def filter(
        self,
        candidates: List[UniverseFilterCandidate],
        config: UniverseFilterConfig = UniverseFilterConfig(),
    ) -> List[UniverseFilterResult]:
        return [self.evaluate(candidate, config) for candidate in candidates]

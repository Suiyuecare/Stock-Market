from typing import Mapping, Optional

from app.schemas import FactorWeightPresetCatalog, FactorWeightProfile


class FactorWeightProfileService:
    """Select manual MVP factor weights before model-learned weights exist."""

    def catalog(self) -> FactorWeightPresetCatalog:
        return FactorWeightPresetCatalog(
            general_tw_stock=FactorWeightProfile(
                name="general_tw_stock",
                description="General Taiwan stock scoring weights.",
                factor_weights={
                    "fundamental": 0.20,
                    "chip": 0.18,
                    "technical": 0.17,
                    "us_market": 0.15,
                    "news": 0.12,
                    "macro": 0.08,
                    "target_price": 0.05,
                    "liquidity": 0.05,
                },
                risk_score_weight=0.35,
                signal_policy_notes=["Use balanced multi-factor scoring for general Taiwan stocks."],
            ),
            electronics_semiconductor_ai=FactorWeightProfile(
                name="electronics_semiconductor_ai",
                description="Electronics, semiconductor, and AI supply-chain scoring weights.",
                factor_weights={
                    "fundamental": 0.17,
                    "chip": 0.17,
                    "technical": 0.16,
                    "us_market": 0.25,
                    "news": 0.10,
                    "macro": 0.05,
                    "target_price": 0.05,
                    "liquidity": 0.05,
                },
                risk_score_weight=0.35,
                signal_policy_notes=["Increase US market linkage weight for electronics and AI supply chains."],
            ),
            domestic_traditional_construction=FactorWeightProfile(
                name="domestic_traditional_construction",
                description="Domestic demand, traditional industry, and construction scoring weights.",
                factor_weights={
                    "fundamental": 0.25,
                    "chip": 0.20,
                    "technical": 0.20,
                    "us_market": 0.05,
                    "news": 0.15,
                    "macro": 0.10,
                    "target_price": 0.05,
                    "liquidity": 0.0,
                },
                risk_score_weight=0.35,
                signal_policy_notes=["Reduce US linkage weight for more local-demand-driven stocks."],
            ),
            bear_or_high_volatility=FactorWeightProfile(
                name="bear_or_high_volatility",
                description="Bear or high-volatility market scoring weights.",
                factor_weights={
                    "fundamental": 0.18,
                    "chip": 0.15,
                    "technical": 0.12,
                    "us_market": 0.10,
                    "news": 0.10,
                    "macro": 0.05,
                    "target_price": 0.05,
                    "liquidity": 0.05,
                },
                risk_score_weight=0.55,
                signal_policy_notes=[
                    "Raise risk penalty in bear or high-volatility regimes.",
                    "Increase selection thresholds and reduce signal count rather than broadening the watchlist.",
                ],
            ),
        )

    def select_profile(
        self,
        stock_profile: Optional[Mapping[str, object]] = None,
        market_regime: Optional[object] = None,
        profile_name: Optional[str] = None,
    ) -> FactorWeightProfile:
        catalog = self.catalog()
        if profile_name:
            profile = getattr(catalog, profile_name, None)
            if profile is not None:
                return profile
        if self._is_bear_or_high_volatility(market_regime):
            return catalog.bear_or_high_volatility
        if self._is_electronics_semiconductor_ai(stock_profile):
            return catalog.electronics_semiconductor_ai
        if self._is_domestic_traditional_construction(stock_profile):
            return catalog.domestic_traditional_construction
        return catalog.general_tw_stock

    def _is_bear_or_high_volatility(self, market_regime: Optional[object]) -> bool:
        if market_regime is None:
            return False
        primary = self._regime_value(market_regime, "primary_regime")
        active = self._regime_value(market_regime, "active_regimes") or []
        return primary == "bear_market" or "high_volatility" in active

    def _is_electronics_semiconductor_ai(self, stock_profile: Optional[Mapping[str, object]]) -> bool:
        values = self._profile_terms(stock_profile)
        keywords = {"electronics", "semiconductor", "ai", "ai_server", "server", "foundry", "ic_design"}
        return bool(values & keywords)

    def _is_domestic_traditional_construction(self, stock_profile: Optional[Mapping[str, object]]) -> bool:
        values = self._profile_terms(stock_profile)
        keywords = {
            "domestic",
            "domestic_demand",
            "traditional",
            "construction",
            "building",
            "cement",
            "retail",
            "food",
        }
        return bool(values & keywords)

    def _profile_terms(self, stock_profile: Optional[Mapping[str, object]]) -> set:
        if not stock_profile:
            return set()
        raw_values = [
            stock_profile.get("industry"),
            stock_profile.get("sector"),
            stock_profile.get("sub_industry"),
            stock_profile.get("market_type"),
        ]
        tags = stock_profile.get("supply_chain_tags", [])
        if isinstance(tags, list):
            raw_values.extend(tags)
        return {str(value).lower() for value in raw_values if value}

    def _regime_value(self, market_regime: object, key: str) -> object:
        if isinstance(market_regime, Mapping):
            return market_regime.get(key)
        return getattr(market_regime, key, None)

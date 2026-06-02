from typing import List

from pydantic import BaseModel


class StrategyObjectiveDefaults(BaseModel):
    primary: str = "maximize_out_of_sample_win_rate_lower_bound"
    secondary: List[str] = [
        "positive_expected_value",
        "profit_factor_above_1_2",
        "max_drawdown_below_limit",
        "enough_trade_samples",
    ]


class LabelDefaults(BaseModel):
    main_target: str = "up_5d_relative"
    auxiliary_targets: List[str] = ["up_1d_absolute", "up_20d_relative"]
    benchmark: str = "TAIEX"
    min_excess_return: float = 0.003
    entry_price: str = "next_open"
    exit_price: str = "close_after_horizon"
    include_transaction_costs: bool = True
    include_slippage: bool = True


class UniverseDefaults(BaseModel):
    min_listing_days: int = 250
    min_close_price: float = 10.0
    min_avg_turnover_20d_twd: float = 50_000_000.0
    exclude_full_delivery: bool = True
    exclude_disposition: bool = True
    exclude_missing_data: bool = True


class SignalFilterDefaults(BaseModel):
    min_probability_up_5d: float = 0.60
    min_confidence: float = 0.60
    max_risk_score: float = 55.0
    min_risk_adjusted_score: float = 50.0
    top_k_per_day: int = 20
    max_per_industry: int = 5
    require_no_major_negative_news: bool = True


class TechnicalFilterDefaults(BaseModel):
    allow_macd_golden_cross: bool = True
    allow_macd_above_zero: bool = True
    reject_macd_bearish_divergence: bool = True
    reject_high_price_volume_divergence: bool = True
    require_volume_confirmation_for_breakout: bool = True


class ChipFilterDefaults(BaseModel):
    require_institutional_net_buy: bool = False
    prefer_foreign_and_trust_sync_buy: bool = True
    min_institutional_net_ratio: float = 0.03
    reject_three_institutions_sync_sell: bool = True


class USMarketFilterDefaults(BaseModel):
    use_us_market_score: bool = True
    min_us_market_score_for_electronics: float = 55.0
    reject_high_vix_spike: bool = True
    reject_us_futures_sharp_reversal_for_high_beta_electronics: bool = True


class RiskManagementDefaults(BaseModel):
    stop_loss_type: str = "atr_or_percent"
    stop_loss_pct: float = 0.06
    take_profit_pct: float = 0.10
    trailing_stop_enabled: bool = True
    max_holding_days: int = 5
    cooldown_days_after_loss: int = 3


class ValidationDefaults(BaseModel):
    method: str = "walk_forward"
    train_window_days: int = 756
    validation_window_days: int = 126
    test_window_days: int = 126
    retrain_frequency: str = "monthly"
    min_trades_per_fold: int = 100
    min_total_trades: int = 500
    evaluate_by_industry: bool = True
    evaluate_by_market_regime: bool = True


class MVPStrategyDefaults(BaseModel):
    strategy_objective: StrategyObjectiveDefaults = StrategyObjectiveDefaults()
    label: LabelDefaults = LabelDefaults()
    universe: UniverseDefaults = UniverseDefaults()
    signal_filter: SignalFilterDefaults = SignalFilterDefaults()
    technical_filter: TechnicalFilterDefaults = TechnicalFilterDefaults()
    chip_filter: ChipFilterDefaults = ChipFilterDefaults()
    us_market_filter: USMarketFilterDefaults = USMarketFilterDefaults()
    risk_management: RiskManagementDefaults = RiskManagementDefaults()
    validation: ValidationDefaults = ValidationDefaults()
    intent_summary: List[str] = [
        "Mainly optimize 5-day relative win-rate reliability.",
        "Avoid low-liquidity stocks and high-risk signals.",
        "Require enough model confidence and historical trade samples.",
        "Limit daily and industry concentration.",
        "Reject obvious high-level technical divergence.",
        "Downgrade electronics exposure when US market linkage turns sharply weaker.",
    ]

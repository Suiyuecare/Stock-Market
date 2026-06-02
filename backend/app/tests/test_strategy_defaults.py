from app.schemas import MVPStrategyDefaults
from app.services.strategy_defaults import StrategyDefaultsService


def test_mvp_strategy_defaults_match_recommended_initial_settings() -> None:
    defaults = MVPStrategyDefaults()

    assert defaults.strategy_objective.primary == "maximize_out_of_sample_win_rate_lower_bound"
    assert "positive_expected_value" in defaults.strategy_objective.secondary
    assert defaults.label.main_target == "up_5d_relative"
    assert defaults.label.benchmark == "TAIEX"
    assert defaults.label.min_excess_return == 0.003
    assert defaults.universe.min_listing_days == 250
    assert defaults.universe.min_close_price == 10
    assert defaults.universe.min_avg_turnover_20d_twd == 50_000_000
    assert defaults.signal_filter.min_probability_up_5d == 0.60
    assert defaults.signal_filter.top_k_per_day == 20
    assert defaults.signal_filter.max_per_industry == 5


def test_mvp_strategy_defaults_include_technical_chip_us_risk_and_validation_filters() -> None:
    defaults = StrategyDefaultsService().mvp_defaults()

    assert defaults.technical_filter.reject_macd_bearish_divergence is True
    assert defaults.technical_filter.require_volume_confirmation_for_breakout is True
    assert defaults.chip_filter.require_institutional_net_buy is False
    assert defaults.chip_filter.min_institutional_net_ratio == 0.03
    assert defaults.us_market_filter.min_us_market_score_for_electronics == 55
    assert defaults.us_market_filter.reject_high_vix_spike is True
    assert defaults.risk_management.stop_loss_pct == 0.06
    assert defaults.risk_management.take_profit_pct == 0.10
    assert defaults.risk_management.max_holding_days == 5
    assert defaults.validation.method == "walk_forward"
    assert defaults.validation.min_trades_per_fold == 100
    assert defaults.validation.min_total_trades == 500

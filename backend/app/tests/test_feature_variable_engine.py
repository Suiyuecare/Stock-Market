from app.schemas import (
    ChipFeatureInput,
    FundamentalFeatureInput,
    NewsFeatureInput,
    RiskFeatureInput,
    TechnicalFeatureInput,
    USMarketFeatureInput,
)
from app.services.feature_variable_engine import FeatureVariableEngine


def test_fundamental_features_include_raw_and_derived_variables() -> None:
    result = FeatureVariableEngine().fundamental_features(
        FundamentalFeatureInput(
            revenue_yoy=0.12,
            revenue_mom=0.03,
            previous_revenue_yoy=-0.04,
            revenue_yoy_history_3m=[0.08, 0.1, 0.12],
            eps_yoy=0.15,
            eps_qoq=0.04,
            gross_margin_delta_qoq=0.02,
            gross_margin_delta_yoy=0.03,
            operating_margin_delta=0.01,
            debt_ratio=0.28,
            operating_cash_flow_quality=0.8,
            inventory_growth_vs_revenue_growth=-0.02,
            accounts_receivable_growth_vs_revenue_growth=0.01,
            industry_growth_score=72,
        )
    )

    assert result.feature_group == "fundamental"
    assert result.features["revenue_yoy"] == 0.12
    assert result.features["revenue_yoy_acceleration"] == 0.16
    assert result.features["revenue_3m_yoy_avg"] == 0.1
    assert result.features["fundamental_turnaround"] == 100.0
    assert result.features["quality_growth"] > 0


def test_quality_growth_requires_revenue_margin_and_cash_flow_alignment() -> None:
    weak = FeatureVariableEngine().fundamental_features(
        FundamentalFeatureInput(
            revenue_yoy=-0.05,
            gross_margin_delta_qoq=-0.01,
            gross_margin_delta_yoy=-0.02,
            operating_cash_flow_quality=-0.2,
        )
    )
    strong = FeatureVariableEngine().fundamental_features(
        FundamentalFeatureInput(
            revenue_yoy=0.2,
            gross_margin_delta_qoq=0.03,
            operating_cash_flow_quality=0.9,
        )
    )

    assert weak.features["quality_growth"] == 0
    assert strong.features["quality_growth"] > weak.features["quality_growth"]


def test_chip_features_include_institutional_and_tdcc_variables() -> None:
    result = FeatureVariableEngine().chip_features(
        ChipFeatureInput(
            foreign_net_ratio=0.03,
            investment_trust_net_ratio=0.02,
            dealer_net_ratio=0.0,
            institutional_net_ratio=0.055,
            foreign_consecutive_buy_days=5,
            trust_consecutive_buy_days=4,
            dealer_consecutive_buy_days=1,
            institutional_sync_buy=True,
            foreign_reversal_to_buy=True,
            trust_accumulation_score=78,
            dealer_hedge_pressure=0.05,
            tdcc_large_holder_ratio=0.62,
            tdcc_large_holder_ratio_delta=0.02,
            margin_balance_delta=0.01,
            short_interest_delta=-0.01,
            borrow_sell_balance_delta=-0.02,
        )
    )

    assert result.feature_group == "chip"
    assert result.features["foreign_net_ratio"] == 0.03
    assert result.features["institutional_sync_buy"] == 1.0
    assert result.features["foreign_reversal_to_buy"] == 1.0
    assert result.features["chip_alignment_score"] > 90


def test_chip_alignment_penalizes_sync_sell_and_hedge_pressure() -> None:
    aligned = FeatureVariableEngine().chip_features(
        ChipFeatureInput(
            foreign_net_ratio=0.03,
            investment_trust_net_ratio=0.02,
            dealer_net_ratio=0.01,
            institutional_net_ratio=0.05,
            tdcc_large_holder_ratio_delta=0.01,
        )
    )
    weak = FeatureVariableEngine().chip_features(
        ChipFeatureInput(
            foreign_net_ratio=-0.03,
            investment_trust_net_ratio=-0.02,
            dealer_net_ratio=-0.01,
            institutional_net_ratio=-0.05,
            institutional_sync_sell=True,
            dealer_hedge_pressure=0.2,
            tdcc_large_holder_ratio_delta=-0.01,
        )
    )

    assert aligned.features["chip_alignment_score"] == 100.0
    assert weak.features["chip_alignment_score"] == 0.0


def test_technical_features_include_trend_macd_and_volume_price_variables() -> None:
    result = FeatureVariableEngine().technical_features(
        TechnicalFeatureInput(
            ma5=105,
            ma20=100,
            ma60=95,
            previous_ma20=98,
            previous_ma60=94,
            close_price=108,
            high_20d=108,
            high_60d=110,
            volume=1500,
            volume_ma20=1000,
            obv_slope=0.4,
            rsi14=62,
            kd_k=70,
            kd_d=65,
            atr_pct=0.03,
            volatility_20d=0.22,
            macd_dif=1.2,
            macd_dea=0.8,
            macd_hist=0.4,
            previous_macd_hist_3d=0.1,
            macd_golden_cross=True,
            price_up_volume_up=True,
            new_high_volume_not_confirmed=True,
        )
    )

    assert result.feature_group == "technical"
    assert result.features["ma5_above_ma20"] == 1.0
    assert result.features["breakout_20d_high"] == 1.0
    assert result.features["volume_ma20_ratio"] == 1.5
    assert result.features["macd_hist_slope_3d"] == 0.3
    assert result.features["new_high_volume_not_confirmed"] == 1.0


def test_us_market_features_include_alignment_score() -> None:
    result = FeatureVariableEngine().us_market_features(
        USMarketFeatureInput(
            nasdaq_return_1d=0.012,
            sox_return_1d=0.018,
            tsm_adr_premium_discount=0.01,
            nvda_return_1d=0.03,
            nq_futures_return_preopen=0.006,
            us_supply_chain_sensitivity=1.2,
            chip_alignment_score=80,
        )
    )

    assert result.feature_group == "us_market"
    assert result.features["nasdaq_return_1d"] == 0.012
    assert result.features["us_market_alignment_score"] > 90


def test_news_features_include_event_flags_and_effective_score() -> None:
    result = FeatureVariableEngine().news_features(
        NewsFeatureInput(
            news_sentiment_score=80,
            news_impact_score=75,
            news_confidence=90,
            positive_news_count_24h=3,
            news_volume_spike=True,
            event_type="guidance",
            event_novelty_score=70,
            source_reliability_score=85,
            guidance_news_flag=True,
            supply_chain_linkage_score=80,
            fundamental_consistency_score=75,
        )
    )

    assert result.feature_group == "news"
    assert result.features["guidance_news_flag"] == 1.0
    assert result.features["event_type"] == 4.0
    assert result.features["news_effective_score"] > 70


def test_news_effective_score_penalizes_reflected_or_high_risk_news() -> None:
    clean = FeatureVariableEngine().news_features(
        NewsFeatureInput(news_sentiment_score=80, news_impact_score=80, news_confidence=80)
    )
    risky = FeatureVariableEngine().news_features(
        NewsFeatureInput(
            news_sentiment_score=80,
            news_impact_score=80,
            news_confidence=80,
            already_reflected_in_price=True,
            lawsuit_risk_flag=True,
            default_risk_flag=True,
        )
    )

    assert risky.features["news_effective_score"] < clean.features["news_effective_score"]


def test_risk_features_include_hard_exclusion_flags() -> None:
    result = FeatureVariableEngine().risk_features(
        RiskFeatureInput(
            risk_score=82,
            volatility_20d=0.35,
            atr_pct=0.05,
            beta_to_taiex=1.4,
            beta_to_sox=1.8,
            max_drawdown_60d=-0.2,
            max_drawdown_120d=-0.35,
            liquidity_score=30,
            negative_news_risk=88,
            high_volume_price_divergence=True,
            institutional_reversal_to_sell=True,
            is_electronics=True,
            us_futures_reversal_risk=75,
        )
    )

    assert result.feature_group == "risk"
    assert result.features["risk_exclusion_high_risk_score"] == 1.0
    assert result.features["risk_exclusion_low_liquidity"] == 1.0
    assert result.features["risk_exclusion_major_negative_news"] == 1.0
    assert result.features["risk_exclusion_high_divergence_institutional_sell"] == 1.0
    assert result.features["risk_downgrade_electronics_us_futures_weak"] == 1.0

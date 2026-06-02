from app.models.us_tw_supply_chain_map import USTWSupplyChainMapping
from app.services.scoring.us_market_score import calculate_us_market_score, us_linkage_score


def test_sox_nvda_strong_up_increases_ai_semiconductor_taiwan_stocks() -> None:
    linkage = {
        "NASDAQ": 0.25,
        "QQQ": 0.2,
        "S&P500": 0.1,
        "SOX": 0.65,
        "SMH": 0.5,
        "NVDA": 0.8,
        "AMD": 0.35,
        "AVGO": 0.3,
        "TSM_ADR": 0.4,
        "VIX": -0.1,
        "US_NEWS_SENTIMENT": 0.2,
    }
    profile = {"stock_id": "2330", "industry": "半導體", "supply_chain_tags": ["semiconductor", "foundry", "AI"]}
    payload = calculate_us_market_score(linkage, profile)

    assert payload["score"] > 65
    assert payload["us_semiconductor_ai_score"] > 65
    assert "SOX strength supports semiconductor linkage" in payload["positive_factors"]
    assert "NVDA strength supports AI/semiconductor supply chain" in payload["positive_factors"]


def test_aapl_weak_guidance_hurts_apple_supply_chain_stocks() -> None:
    linkage = {
        "NASDAQ": 0.05,
        "S&P500": 0.02,
        "AAPL": -0.55,
        "AAPL_GUIDANCE": -0.7,
        "US_NEWS_SENTIMENT": -0.35,
        "VIX": 0.02,
    }
    profile = {"stock_id": "2317", "industry": "電子代工", "supply_chain_tags": ["Apple", "EMS"]}
    payload = calculate_us_market_score(linkage, profile)

    assert payload["score"] < 50
    assert "AAPL weakness pressures Apple supply chain" in payload["negative_factors"]
    assert "US news sentiment is negative" in payload["negative_factors"]


def test_ai_server_stock_uses_cloud_and_gpu_leaders() -> None:
    linkage = {
        "NASDAQ": 0.15,
        "NVDA": 0.75,
        "AMD": 0.45,
        "AVGO": 0.4,
        "MSFT": 0.35,
        "META": 0.3,
        "GOOGL": 0.28,
        "AMZN": 0.25,
        "VIX": -0.08,
    }
    profile = {"stock_id": "6669", "industry": "AI Server", "supply_chain_tags": ["AI-server", "cloud"]}
    payload = calculate_us_market_score(linkage, profile)

    assert payload["score"] > 60
    assert payload["us_supply_chain_stock_score"] > 65
    assert "NVDA strength supports AI/semiconductor supply chain" in payload["positive_factors"]


def test_memory_stock_uses_mu_and_memory_news() -> None:
    positive = calculate_us_market_score(
        {"MU": 0.65, "MEMORY_NEWS_SENTIMENT": 0.45, "SOX": 0.25, "NASDAQ": 0.1, "VIX": -0.05},
        {"stock_id": "2408", "industry": "記憶體", "supply_chain_tags": ["memory", "DRAM"]},
    )
    negative = calculate_us_market_score(
        {"MU": -0.55, "MEMORY_NEWS_SENTIMENT": -0.45, "SOX": -0.2, "NASDAQ": -0.05, "VIX": 0.1},
        {"stock_id": "2408", "industry": "記憶體", "supply_chain_tags": ["memory", "DRAM"]},
    )

    assert positive["score"] > negative["score"]
    assert positive["us_semiconductor_ai_score"] > 55
    assert "MU strength supports memory supply chain" in positive["positive_factors"]
    assert "memory-related US news sentiment is negative" in negative["negative_factors"]


def test_financial_stock_uses_yields_sp500_and_vix() -> None:
    payload = calculate_us_market_score(
        {"S&P500": -0.25, "US10Y": 0.55, "VIX": 0.45, "NASDAQ": -0.1},
        {"stock_id": "2882", "industry": "金融", "supply_chain_tags": ["financial", "bank"]},
    )

    assert payload["score"] < 50
    assert payload["us_macro_liquidity_score"] < 45
    assert "US yields or volatility increase financial linkage risk" in payload["risk_factors"]


def test_vix_spike_increases_risk_factors() -> None:
    payload = calculate_us_market_score(
        {"NASDAQ": -0.15, "S&P500": -0.2, "SOX": -0.25, "VIX": 0.65},
        {"stock_id": "2330", "industry": "半導體", "supply_chain_tags": ["semiconductor"]},
    )

    assert "VIX spike raises US market risk" in payload["risk_factors"]
    assert "US volatility increased" in payload["negative_factors"]
    assert payload["us_macro_liquidity_score"] < 50


def test_strong_us_market_low_sensitivity_only_adds_small_score() -> None:
    linkage = {
        "NASDAQ": 0.7,
        "QQQ": 0.65,
        "S&P500": 0.6,
        "SOX": 0.7,
        "NVDA": 0.8,
        "AAPL": 0.5,
        "VIX": -0.3,
        "US_NEWS_SENTIMENT": 0.4,
    }
    profile = {
        "stock_id": "2912",
        "industry": "retail",
        "supply_chain_tags": ["domestic-demand"],
        "us_market_sensitivity": 0.4,
    }
    payload = calculate_us_market_score(linkage, profile)

    assert 50 < payload["score"] < 58
    assert payload["sensitivity_multiplier"] <= 0.45
    assert "low US market sensitivity limits signal impact" in payload["risk_factors"]


def test_sensitivity_mapping_can_raise_supply_chain_impact() -> None:
    linkage = {"NVDA": 0.6, "SOX": 0.4, "NASDAQ": 0.2, "VIX": -0.1}
    profile = {"stock_id": "6669", "industry": "半導體", "supply_chain_tags": ["AI"]}
    mappings = [
        USTWSupplyChainMapping(
            us_ticker="NVDA",
            us_company_name="NVIDIA",
            tw_stock_id="6669",
            tw_stock_name="緯穎",
            relation_type="customer",
            supply_chain_tag="AI",
            sensitivity_weight=1.3,
            confidence=0.9,
        )
    ]
    mapped = calculate_us_market_score(linkage, profile, mappings)
    unmapped = calculate_us_market_score(linkage, profile)

    assert mapped["score"] > unmapped["score"]
    assert mapped["sensitivity_multiplier"] > unmapped["sensitivity_multiplier"]


def test_us_linkage_score_keeps_legacy_normalized_contract() -> None:
    score = us_linkage_score({"NASDAQ": 0.4, "SOX": 0.5, "NVDA": 0.6, "VIX": -0.2})

    assert 0 < score <= 1

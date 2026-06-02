from app.services.data_providers.brokerage_provider import (
    BROKERAGE_CAPABILITIES,
    BROKERAGE_ENDPOINTS,
    BROKERAGE_MVP_DISABLED_ACTIONS,
    BrokerageProvider,
)


def test_brokerage_provider_exposes_future_integration_endpoints() -> None:
    provider = BrokerageProvider()

    assert provider.endpoints["sinopac_shioaji_official"].endswith("/python/Main/index.aspx")
    assert provider.endpoints["shioaji_github_docs"] == "https://sinotrade.github.io/"
    assert provider.endpoints["fubon_neo_trading_docs"].endswith("/trading/introduction")
    assert provider.endpoints["fubon_neo_market_data"].endswith("/market-data/intro/")
    assert provider.endpoints["yuanta_spark_api"].endswith("/API/page/index.html")
    assert BROKERAGE_ENDPOINTS["yuanta_futures_api"].endswith("/api/download.html")


def test_brokerage_provider_tracks_trading_and_quote_capabilities() -> None:
    assert "real_time_quotes" in BROKERAGE_CAPABILITIES
    assert "paper_trading" in BROKERAGE_CAPABILITIES
    assert "order_routing" in BROKERAGE_CAPABILITIES
    assert "account_balances" in BROKERAGE_CAPABILITIES
    assert "execution_reports" in BROKERAGE_CAPABILITIES


def test_brokerage_provider_keeps_live_trading_disabled_for_mvp() -> None:
    provider = BrokerageProvider()

    assert "live_order_placement" in provider.disabled_actions
    assert "account_balance_sync" in BROKERAGE_MVP_DISABLED_ACTIONS
    assert "position_sync" in BROKERAGE_MVP_DISABLED_ACTIONS
    assert "client_side_broker_credentials" in BROKERAGE_MVP_DISABLED_ACTIONS

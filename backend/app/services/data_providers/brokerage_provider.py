from app.services.data_providers.base import MarketDataProvider

BROKERAGE_ENDPOINTS = {
    "sinopac_shioaji_official": "https://ai.sinotrade.com.tw/python/Main/index.aspx",
    "shioaji_github_docs": "https://sinotrade.github.io/",
    "fubon_neo_trading_docs": "https://www.fbs.com.tw/TradeAPI/en/docs/trading/introduction",
    "fubon_neo_market_data": "https://www.fbs.com.tw/TradeAPI/en/docs/market-data/intro/",
    "fubon_neo_futures_market_data": "https://www.fbs.com.tw/TradeAPI/en/docs/market-data-future/intro",
    "yuanta_spark_api": "https://www.yuanta.com.tw/file-repository/content/API/page/index.html",
    "yuanta_api_order": "https://www.yuanta.com.tw/eyuanta/Securities/DigitalArea/ApiOrder",
    "yuanta_futures_api": "https://www.yuantafutures.com.tw/ytf/easywin/api/download.html",
}

BROKERAGE_CAPABILITIES = [
    "real_time_quotes",
    "historical_quotes",
    "paper_trading",
    "order_routing",
    "account_balances",
    "positions",
    "order_reports",
    "execution_reports",
]

BROKERAGE_MVP_DISABLED_ACTIONS = [
    "live_order_placement",
    "account_balance_sync",
    "position_sync",
    "execution_report_sync",
    "client_side_broker_credentials",
]


class BrokerageProvider(MarketDataProvider):
    """Future brokerage integration placeholder.

    The current MVP is an analysis and alerting app, so broker APIs stay
    disabled. Real order routing, account data, and position sync require a
    separate product scope, broker approval, credentials/certificates, user
    opt-in, paper-trading validation, and risk controls.
    """

    endpoints = BROKERAGE_ENDPOINTS
    capabilities = BROKERAGE_CAPABILITIES
    disabled_actions = BROKERAGE_MVP_DISABLED_ACTIONS

    def get_instruments(self):
        return []

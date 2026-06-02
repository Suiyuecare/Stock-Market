from app.services.data_providers.brokerage_provider import (
    BROKERAGE_CAPABILITIES,
    BROKERAGE_ENDPOINTS,
    BROKERAGE_MVP_DISABLED_ACTIONS,
    BrokerageProvider,
)


class BrokerProvider(BrokerageProvider):
    """Alias provider for optional future broker integrations."""

    endpoints = BROKERAGE_ENDPOINTS
    capabilities = BROKERAGE_CAPABILITIES
    disabled_actions = BROKERAGE_MVP_DISABLED_ACTIONS

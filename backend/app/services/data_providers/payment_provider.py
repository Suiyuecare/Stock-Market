from app.services.data_providers.app_operations_provider import AppOperationsProvider

PAYMENT_ENDPOINTS = {
    "stripe_api_docs": AppOperationsProvider.endpoints["stripe_api_docs"],
    "stripe_rest_base": AppOperationsProvider.endpoints["stripe_rest_base"],
}


class PaymentProvider(AppOperationsProvider):
    """Billing and payments provider placeholder."""

    endpoints = PAYMENT_ENDPOINTS
    capabilities = ["billing"]
    secret_env_vars = ["STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"]
    public_env_vars = ["NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY"]

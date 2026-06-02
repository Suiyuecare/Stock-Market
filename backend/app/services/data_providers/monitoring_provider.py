from app.services.data_providers.app_operations_provider import AppOperationsProvider

MONITORING_ENDPOINTS = {
    "sentry_api_docs": AppOperationsProvider.endpoints["sentry_api_docs"],
    "sentry_rest_base": AppOperationsProvider.endpoints["sentry_rest_base"],
}


class MonitoringProvider(AppOperationsProvider):
    """Error monitoring provider placeholder."""

    endpoints = MONITORING_ENDPOINTS
    capabilities = ["error_monitoring"]
    secret_env_vars = ["SENTRY_AUTH_TOKEN"]
    public_env_vars = ["NEXT_PUBLIC_SENTRY_DSN"]

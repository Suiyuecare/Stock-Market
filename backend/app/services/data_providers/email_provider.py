from app.services.data_providers.app_operations_provider import AppOperationsProvider

EMAIL_ENDPOINTS = {
    "sendgrid_api_reference": AppOperationsProvider.endpoints["sendgrid_api_reference"],
    "sendgrid_mail_send": AppOperationsProvider.endpoints["sendgrid_mail_send"],
}


class EmailProvider(AppOperationsProvider):
    """Transactional email provider placeholder."""

    endpoints = EMAIL_ENDPOINTS
    capabilities = ["transactional_email"]
    secret_env_vars = ["SENDGRID_API_KEY"]

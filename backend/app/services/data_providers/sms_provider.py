from app.services.data_providers.app_operations_provider import AppOperationsProvider

SMS_ENDPOINTS = {
    "twilio_messaging_api": AppOperationsProvider.endpoints["twilio_messaging_api"],
    "twilio_sms_send": AppOperationsProvider.endpoints["twilio_sms_send"],
}


class SMSProvider(AppOperationsProvider):
    """SMS alert provider placeholder."""

    endpoints = SMS_ENDPOINTS
    capabilities = ["sms_alerts"]
    secret_env_vars = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN"]

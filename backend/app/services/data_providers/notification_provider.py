from app.services.data_providers.app_operations_provider import AppOperationsProvider

NOTIFICATION_ENDPOINTS = {
    "firebase_cloud_messaging_docs": AppOperationsProvider.endpoints["firebase_cloud_messaging_docs"],
    "firebase_cloud_messaging_rest_docs": AppOperationsProvider.endpoints["firebase_cloud_messaging_rest_docs"],
    "firebase_cloud_messaging_send": AppOperationsProvider.endpoints["firebase_cloud_messaging_send"],
}


class NotificationProvider(AppOperationsProvider):
    """Push notification provider placeholder."""

    endpoints = NOTIFICATION_ENDPOINTS
    capabilities = ["push_notifications"]
    secret_env_vars = ["FCM_SERVICE_ACCOUNT_JSON"]

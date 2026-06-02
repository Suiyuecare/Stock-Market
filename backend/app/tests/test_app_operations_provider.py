from app.services.data_providers.app_operations_provider import (
    APP_OPERATIONS_CAPABILITIES,
    APP_OPERATIONS_ENDPOINTS,
    APP_OPERATIONS_PUBLIC_ENV_VARS,
    APP_OPERATIONS_SECRET_ENV_VARS,
    AppOperationsProvider,
)


def test_app_operations_provider_exposes_notification_and_billing_endpoints() -> None:
    provider = AppOperationsProvider()

    assert provider.endpoints["firebase_cloud_messaging_send"].endswith("/messages:send")
    assert provider.endpoints["sendgrid_mail_send"] == "https://api.sendgrid.com/v3/mail/send"
    assert provider.endpoints["twilio_sms_send"].endswith("/Messages.json")
    assert provider.endpoints["stripe_rest_base"] == "https://api.stripe.com/v1"
    assert APP_OPERATIONS_ENDPOINTS["sentry_rest_base"] == "https://sentry.io/api/0"


def test_app_operations_provider_exposes_auth_and_management_endpoints() -> None:
    assert APP_OPERATIONS_ENDPOINTS["supabase_auth_docs"].endswith("/guides/auth")
    assert APP_OPERATIONS_ENDPOINTS["supabase_data_api_docs"].endswith("/guides/api")
    assert APP_OPERATIONS_ENDPOINTS["supabase_management_api"] == "https://api.supabase.com/api/v1"
    assert APP_OPERATIONS_ENDPOINTS["auth0_tenant_api_base"] == "https://{YOUR_DOMAIN}/api/v2/"
    assert APP_OPERATIONS_ENDPOINTS["clerk_rest_base"] == "https://api.clerk.com/v1"


def test_app_operations_provider_tracks_capabilities() -> None:
    assert "push_notifications" in APP_OPERATIONS_CAPABILITIES
    assert "transactional_email" in APP_OPERATIONS_CAPABILITIES
    assert "sms_alerts" in APP_OPERATIONS_CAPABILITIES
    assert "billing" in APP_OPERATIONS_CAPABILITIES
    assert "google_oauth" in APP_OPERATIONS_CAPABILITIES
    assert "error_monitoring" in APP_OPERATIONS_CAPABILITIES


def test_app_operations_provider_separates_secret_and_public_env_vars() -> None:
    assert "SUPABASE_SERVICE_ROLE_KEY" in APP_OPERATIONS_SECRET_ENV_VARS
    assert "STRIPE_SECRET_KEY" in APP_OPERATIONS_SECRET_ENV_VARS
    assert "SENTRY_AUTH_TOKEN" in APP_OPERATIONS_SECRET_ENV_VARS
    assert "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY" in APP_OPERATIONS_PUBLIC_ENV_VARS
    assert "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY" in APP_OPERATIONS_PUBLIC_ENV_VARS
    assert "SUPABASE_SERVICE_ROLE_KEY" not in APP_OPERATIONS_PUBLIC_ENV_VARS

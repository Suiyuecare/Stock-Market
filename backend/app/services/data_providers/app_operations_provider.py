APP_OPERATIONS_ENDPOINTS = {
    "firebase_cloud_messaging_docs": "https://firebase.google.com/docs/cloud-messaging",
    "firebase_cloud_messaging_rest_docs": "https://firebase.google.com/docs/reference/fcm/rest",
    "firebase_cloud_messaging_send": "https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send",
    "sendgrid_api_reference": "https://www.twilio.com/docs/sendgrid/api-reference",
    "sendgrid_mail_send": "https://api.sendgrid.com/v3/mail/send",
    "twilio_messaging_api": "https://www.twilio.com/docs/messaging/api",
    "twilio_sms_send": "https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json",
    "stripe_api_docs": "https://docs.stripe.com/api",
    "stripe_rest_base": "https://api.stripe.com/v1",
    "supabase_auth_docs": "https://supabase.com/docs/guides/auth",
    "supabase_data_api_docs": "https://supabase.com/docs/guides/api",
    "supabase_management_api": "https://api.supabase.com/api/v1",
    "auth0_management_api": "https://auth0.com/docs/api/management/v2",
    "auth0_tenant_api_base": "https://{YOUR_DOMAIN}/api/v2/",
    "clerk_backend_api": "https://clerk.com/docs/reference/backend-api",
    "clerk_rest_base": "https://api.clerk.com/v1",
    "sentry_api_docs": "https://docs.sentry.io/api/",
    "sentry_rest_base": "https://sentry.io/api/0",
}

APP_OPERATIONS_CAPABILITIES = [
    "push_notifications",
    "transactional_email",
    "sms_alerts",
    "billing",
    "google_oauth",
    "user_sessions",
    "management_api",
    "error_monitoring",
]

APP_OPERATIONS_SECRET_ENV_VARS = [
    "FCM_SERVICE_ACCOUNT_JSON",
    "SENDGRID_API_KEY",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "SUPABASE_SERVICE_ROLE_KEY",
    "AUTH0_MANAGEMENT_API_TOKEN",
    "CLERK_SECRET_KEY",
    "SENTRY_AUTH_TOKEN",
]

APP_OPERATIONS_PUBLIC_ENV_VARS = [
    "NEXT_PUBLIC_SUPABASE_URL",
    "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY",
    "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY",
    "NEXT_PUBLIC_SENTRY_DSN",
]


class AppOperationsProvider:
    """Configuration map for operational integrations.

    These services support notifications, email, SMS, billing, auth, and
    monitoring. The MVP should use mock adapters first; live external calls
    require explicit product scope, server-side secrets, and user consent where
    notifications or billing are involved.
    """

    endpoints = APP_OPERATIONS_ENDPOINTS
    capabilities = APP_OPERATIONS_CAPABILITIES
    secret_env_vars = APP_OPERATIONS_SECRET_ENV_VARS
    public_env_vars = APP_OPERATIONS_PUBLIC_ENV_VARS

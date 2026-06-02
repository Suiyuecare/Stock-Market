from app.services.data_providers.app_operations_provider import AppOperationsProvider

AUTH_ENDPOINTS = {
    "supabase_auth_docs": AppOperationsProvider.endpoints["supabase_auth_docs"],
    "supabase_data_api_docs": AppOperationsProvider.endpoints["supabase_data_api_docs"],
    "supabase_management_api": AppOperationsProvider.endpoints["supabase_management_api"],
    "auth0_management_api": AppOperationsProvider.endpoints["auth0_management_api"],
    "auth0_tenant_api_base": AppOperationsProvider.endpoints["auth0_tenant_api_base"],
    "clerk_backend_api": AppOperationsProvider.endpoints["clerk_backend_api"],
    "clerk_rest_base": AppOperationsProvider.endpoints["clerk_rest_base"],
}


class AuthProvider(AppOperationsProvider):
    """Auth provider placeholder, with Supabase Auth preferred for MVP."""

    endpoints = AUTH_ENDPOINTS
    capabilities = ["google_oauth", "user_sessions", "management_api"]
    preferred_provider = "supabase"
    secret_env_vars = ["SUPABASE_SERVICE_ROLE_KEY", "AUTH0_MANAGEMENT_API_TOKEN", "CLERK_SECRET_KEY"]
    public_env_vars = ["NEXT_PUBLIC_SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY"]

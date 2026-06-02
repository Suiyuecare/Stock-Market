from app.services.data_providers.analyst_estimates_provider import (
    ANALYST_ESTIMATES_ENDPOINTS,
    ANALYST_ESTIMATES_FIELDS,
    AnalystEstimatesProvider,
)


class EstimatesProvider(AnalystEstimatesProvider):
    """Alias provider for analyst estimates and target-price sources."""

    endpoints = ANALYST_ESTIMATES_ENDPOINTS
    normalized_fields = ANALYST_ESTIMATES_FIELDS

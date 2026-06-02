from pathlib import Path

from app.services.data_providers.auth_provider import AuthProvider
from app.services.data_providers.bls_provider import BLSProvider
from app.services.data_providers.broker_provider import BrokerProvider
from app.services.data_providers.cbc_provider import CBCProvider
from app.services.data_providers.cme_provider import CMEProvider
from app.services.data_providers.dgbas_provider import DGBASProvider
from app.services.data_providers.email_provider import EmailProvider
from app.services.data_providers.estimates_provider import EstimatesProvider
from app.services.data_providers.fred_provider import FREDProvider
from app.services.data_providers.mops_provider import MOPSProvider
from app.services.data_providers.monitoring_provider import MonitoringProvider
from app.services.data_providers.notification_provider import NotificationProvider
from app.services.data_providers.openai_analysis_provider import OpenAIAnalysisProvider
from app.services.data_providers.payment_provider import PaymentProvider
from app.services.data_providers.sec_edgar_provider import SECEdgarProvider
from app.services.data_providers.sms_provider import SMSProvider
from app.services.data_providers.twse_licensed_provider import TWSELicensedProvider


EXPECTED_PROVIDER_FILES = [
    "base.py",
    "twse_provider.py",
    "twse_licensed_provider.py",
    "tpex_provider.py",
    "taifex_provider.py",
    "tdcc_provider.py",
    "mops_provider.py",
    "tej_provider.py",
    "cbc_provider.py",
    "dgbas_provider.py",
    "us_market_provider.py",
    "cme_provider.py",
    "fred_provider.py",
    "bls_provider.py",
    "sec_edgar_provider.py",
    "estimates_provider.py",
    "news_provider.py",
    "openai_analysis_provider.py",
    "broker_provider.py",
    "notification_provider.py",
    "email_provider.py",
    "sms_provider.py",
    "payment_provider.py",
    "auth_provider.py",
    "monitoring_provider.py",
]


def test_requested_data_provider_files_exist() -> None:
    provider_dir = Path(__file__).parents[1] / "services" / "data_providers"

    missing = [filename for filename in EXPECTED_PROVIDER_FILES if not (provider_dir / filename).exists()]

    assert missing == []


def test_split_market_provider_aliases_expose_expected_endpoints() -> None:
    assert TWSELicensedProvider.endpoints["twse_realtime_license"].endswith("/real-time.html")
    assert MOPSProvider.endpoints["listed_monthly_revenue_csv"].endswith("t187ap05_L.csv")
    assert CBCProvider.endpoints["api_endpoint_format"].endswith("FileName={ITEM_CODE}")
    assert DGBASProvider.endpoints["api_docs_pdf"].endswith("API說明文件.pdf")
    assert CMEProvider.endpoints["market_data_apis"].endswith("/market-data-api.html")
    assert FREDProvider.endpoints["observations"].endswith("/series/observations")
    assert BLSProvider.endpoints["timeseries_v2"].endswith("/timeseries/data/")
    assert SECEdgarProvider.endpoints["ticker_to_cik"].endswith("/company_tickers.json")
    assert EstimatesProvider.endpoints["factset_estimates_api"].endswith("/factset-estimates-api")


def test_operations_provider_aliases_keep_secret_boundaries() -> None:
    assert OpenAIAnalysisProvider.endpoints["responses_api"] == "https://api.openai.com/v1/responses"
    assert "live_order_placement" in BrokerProvider.disabled_actions
    assert NotificationProvider.secret_env_vars == ["FCM_SERVICE_ACCOUNT_JSON"]
    assert EmailProvider.secret_env_vars == ["SENDGRID_API_KEY"]
    assert SMSProvider.secret_env_vars == ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN"]
    assert PaymentProvider.public_env_vars == ["NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY"]
    assert AuthProvider.preferred_provider == "supabase"
    assert "SUPABASE_SERVICE_ROLE_KEY" not in AuthProvider.public_env_vars
    assert MonitoringProvider.public_env_vars == ["NEXT_PUBLIC_SENTRY_DSN"]

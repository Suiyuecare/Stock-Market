from datetime import datetime


def run_us_premarket_job() -> dict[str, str]:
    return {
        "job": "us-premarket-linkage",
        "status": "queued",
        "started_at": datetime.utcnow().isoformat(),
    }

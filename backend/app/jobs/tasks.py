from datetime import datetime


def run_tw_after_close_job() -> dict[str, str]:
    return {
        "job": "tw-after-close",
        "status": "queued",
        "started_at": datetime.utcnow().isoformat(),
    }


def run_us_premarket_job() -> dict[str, str]:
    return {
        "job": "us-premarket-linkage",
        "status": "queued",
        "started_at": datetime.utcnow().isoformat(),
    }

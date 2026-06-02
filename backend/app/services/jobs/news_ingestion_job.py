from datetime import datetime


def run_news_ingestion_job() -> dict[str, str]:
    return {
        "job": "news-ingestion",
        "status": "queued",
        "started_at": datetime.utcnow().isoformat(),
    }

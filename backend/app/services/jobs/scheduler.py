from apscheduler.schedulers.blocking import BlockingScheduler

from app.services.jobs.daily_after_market_job import run_tw_after_close_job
from app.services.jobs.news_ingestion_job import run_news_ingestion_job
from app.services.jobs.pre_open_us_market_job import run_us_premarket_job


def main() -> None:
    scheduler = BlockingScheduler(timezone="Asia/Taipei")
    scheduler.add_job(run_tw_after_close_job, "cron", day_of_week="mon-fri", hour=15, minute=20)
    scheduler.add_job(run_us_premarket_job, "cron", day_of_week="mon-fri", hour=20, minute=30)
    scheduler.add_job(run_news_ingestion_job, "cron", day_of_week="mon-fri", hour=20, minute=45)
    scheduler.start()


if __name__ == "__main__":
    main()

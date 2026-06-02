from apscheduler.schedulers.blocking import BlockingScheduler

from app.jobs.tasks import run_tw_after_close_job, run_us_premarket_job


def main() -> None:
    scheduler = BlockingScheduler(timezone="Asia/Taipei")
    scheduler.add_job(run_tw_after_close_job, "cron", day_of_week="mon-fri", hour=15, minute=20)
    scheduler.add_job(run_us_premarket_job, "cron", day_of_week="mon-fri", hour=20, minute=30)
    scheduler.start()


if __name__ == "__main__":
    main()

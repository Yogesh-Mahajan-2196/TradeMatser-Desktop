# scheduler.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from modules.reports.repository import daily_report, send_daily_report
from utils.database import AsyncSessionLocal


scheduler = AsyncIOScheduler()


async def scheduled_daily_report():

    async with AsyncSessionLocal() as db:
        report = await daily_report(db)
        await send_daily_report(report)


def start_scheduler():

    scheduler.add_job(
        scheduled_daily_report,
        trigger="cron",
        hour=19,
        minute=00,
        id="daily_report",
        replace_existing=True,
    )

    scheduler.start()
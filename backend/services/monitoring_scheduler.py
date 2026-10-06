import asyncio
import logging
from typing import Optional, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.config import settings
from backend.database import SessionLocal
from backend.models.competitor import Competitor
from backend.services.detection_engine import DetectionEngine

logger = logging.getLogger(__name__)

class MonitoringScheduler:
    """
    Continuous Background Monitoring Scheduler.
    Runs periodic checks across all active competitors using an asyncio worker pool
    with semaphore rate-limiting to isolate failures and guarantee concurrent scalability.
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        self.interval_minutes = settings.DEFAULT_MONITORING_INTERVAL_MINUTES
        self.concurrency_limit = settings.CONCURRENT_WORKERS
        self.semaphore = asyncio.Semaphore(self.concurrency_limit)
        self.current_running_checks = 0

    def start(self):
        if not self.is_running:
            self.scheduler.add_job(
                self.run_scheduled_checks,
                trigger=IntervalTrigger(minutes=self.interval_minutes),
                id="continuous_competitor_monitoring",
                name="Continuous Competitor Blog Monitoring",
                replace_existing=True,
            )
            self.scheduler.start()
            self.is_running = True
            logger.info(f"Monitoring Scheduler started. Interval: {self.interval_minutes} minutes.")

    def stop(self):
        if self.is_running:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info("Monitoring Scheduler stopped.")

    def update_interval(self, minutes: int):
        self.interval_minutes = max(1, minutes)
        if self.is_running and self.scheduler.get_job("continuous_competitor_monitoring"):
            self.scheduler.reschedule_job(
                "continuous_competitor_monitoring",
                trigger=IntervalTrigger(minutes=self.interval_minutes)
            )
            logger.info(f"Rescheduled monitoring interval to {self.interval_minutes} minutes.")

    async def run_scheduled_checks(self):
        """
        Executes concurrent checks for all enabled competitors.
        """
        logger.info("Starting scheduled monitoring cycle...")
        db = SessionLocal()
        try:
            competitors = db.query(Competitor).filter(
                Competitor.monitoring_enabled == True
            ).all()
            competitor_ids = [c.id for c in competitors]
        finally:
            db.close()

        if not competitor_ids:
            logger.info("No active competitors to check.")
            return

        logger.info(f"Scheduling checks for {len(competitor_ids)} competitors with concurrency={self.concurrency_limit}.")
        tasks = [self.check_single_competitor_with_worker(cid) for cid in competitor_ids]
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("Scheduled monitoring cycle completed.")

    async def check_single_competitor_with_worker(self, competitor_id: int):
        """
        Wraps individual competitor check in an async semaphore worker pool.
        """
        async with self.semaphore:
            self.current_running_checks += 1
            db = SessionLocal()
            try:
                # Mark competitor as CHECKING
                comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
                if comp:
                    comp.monitoring_status = "CHECKING"
                    db.commit()

                engine = DetectionEngine(db)
                await engine.run_check_for_competitor(competitor_id)
            except Exception as e:
                logger.error(f"Error checking competitor {competitor_id}: {e}")
            finally:
                self.current_running_checks = max(0, self.current_running_checks - 1)
                db.close()

    async def check_competitor_now(self, competitor_id: int):
        """
        Direct on-demand execution for a single competitor.
        """
        db = SessionLocal()
        try:
            engine = DetectionEngine(db)
            return await engine.run_check_for_competitor(competitor_id)
        finally:
            db.close()

# Singleton instance
monitoring_scheduler = MonitoringScheduler()

import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from backend.app.core.config import settings
from backend.app.db.session import SessionLocal
from backend.app.models.field import Field
from backend.app.services.weather.service import weather_service

logger = logging.getLogger(__name__)

class WeatherScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.interval_minutes = settings.WEATHER_POLL_INTERVAL_MINUTES
        self._is_running = False

    async def poll_all_fields(self):
        """Cron/Interval job: queries weather for all active fields in the database."""
        logger.info("Executing scheduled meteorological polling for all registered fields...")
        db = SessionLocal()
        try:
            fields = db.query(Field).all()
            if not fields:
                logger.info("No registered fields found for weather polling.")
                return

            for field in fields:
                try:
                    await weather_service.fetch_weather_for_field(db=db, field=field, force_refresh=True)
                except Exception as e:
                    logger.error(f"Scheduled weather polling failed for Field {field.id} ({field.name}): {e}")
        finally:
            db.close()

    def start(self):
        """Start the background weather poller scheduler."""
        if self._is_running:
            return

        self.scheduler.add_job(
            self.poll_all_fields,
            trigger=IntervalTrigger(minutes=self.interval_minutes),
            id="weather_poll_job",
            name="Periodic Meteorological Telemetry Poller",
            replace_existing=True
        )
        self.scheduler.start()
        self._is_running = True
        logger.info(f"Weather Poller Scheduler started (Interval: {self.interval_minutes} minutes).")

    def stop(self):
        """Shut down the background weather scheduler."""
        if self._is_running:
            self.scheduler.shutdown(wait=False)
            self._is_running = False
            logger.info("Weather Poller Scheduler stopped.")

weather_scheduler = WeatherScheduler()

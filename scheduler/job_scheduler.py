import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.job import Job
from core.config import settings

logger = logging.getLogger(__name__)


class SchedulerManager:
    """
    Manages APScheduler for background job scheduling
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=settings.SCHEDULER_TIMEZONE)
        self.is_running = False
        self._paused_jobs = set()  # Track paused jobs
        
    async def start_scheduler(self):
        """
        Start the scheduler and add the corporate events scraper job
        """
        if not settings.SCHEDULER_ENABLED:
            logger.info("Scheduler is disabled in settings")
            return
            
        if not self.is_running:
            try:
                # Import here to avoid circular imports
                from scheduler.job_manager import execute_corporate_events_job, execute_notification_job
                
                # Add the main scraper job - execute every hour
                self.scheduler.add_job(
                    func=execute_corporate_events_job,
                    trigger=IntervalTrigger(hours=settings.SCRAPER_JOB_INTERVAL_HOURS),
                    id="corporate_events_scraper",
                    name="Corporate Events Scraper",
                    replace_existing=True,
                    max_instances=settings.JOB_MAX_INSTANCES  # Prevent overlapping executions
                )
                
                # Add the notification processor job - execute every hour
                self.scheduler.add_job(
                    func=execute_notification_job,
                    trigger=IntervalTrigger(hours=settings.NOTIFICATION_JOB_INTERVAL_HOURS),
                    id="notification_processor",
                    name="Notification Processor",
                    replace_existing=True,
                    max_instances=settings.JOB_MAX_INSTANCES  # Prevent overlapping executions
                )
                
                # Execute scraper immediately on startup
                self.scheduler.add_job(
                    func=execute_corporate_events_job,
                    trigger=DateTrigger(run_date=datetime.now() + timedelta(seconds=5)),
                    id="corporate_events_scraper_immediate",
                    name="Corporate Events Scraper - Immediate Execution",
                    max_instances=1
                )
                
                # Execute notification processor immediately on startup (with slight delay)
                self.scheduler.add_job(
                    func=execute_notification_job,
                    trigger=DateTrigger(run_date=datetime.now() + timedelta(seconds=15)),
                    id="notification_processor_immediate",
                    name="Notification Processor - Immediate Execution",
                    max_instances=1
                )
                
                self.scheduler.start()
                self.is_running = True
                logger.info("✅ Job scheduler started successfully")
                logger.info(f"Corporate events scraper will run every {settings.SCRAPER_JOB_INTERVAL_HOURS} hour(s)")
                logger.info(f"Notification processor will run every {settings.NOTIFICATION_JOB_INTERVAL_HOURS} hour(s)")
                
            except Exception as e:
                logger.error(f"Failed to start scheduler: {e}")
                raise
                
    async def shutdown_scheduler(self):
        """
        Gracefully shutdown the scheduler
        """
        if self.is_running:
            try:
                self.scheduler.shutdown(wait=True)
                self.is_running = False
                logger.info("⛔ Job scheduler stopped gracefully")
            except Exception as e:
                logger.error(f"Error shutting down scheduler: {e}")
                
    def pause_job(self, job_id: str = "corporate_events_scraper"):
        """
        Pause a specific job
        """
        try:
            if self.scheduler.get_job(job_id):
                self.scheduler.pause_job(job_id)
                self._paused_jobs.add(job_id)
                logger.info(f"Job {job_id} paused")
                return True
        except Exception as e:
            logger.error(f"Failed to pause job {job_id}: {e}")
        return False
        
    def resume_job(self, job_id: str = "corporate_events_scraper"):
        """
        Resume a paused job
        """
        try:
            if self.scheduler.get_job(job_id):
                self.scheduler.resume_job(job_id)
                self._paused_jobs.discard(job_id)
                logger.info(f"Job {job_id} resumed")
                return True
        except Exception as e:
            logger.error(f"Failed to resume job {job_id}: {e}")
        return False
        
    def schedule_job_resume(self, job_id: str = "corporate_events_scraper", hours_delay: int = 6):
        """
        Schedule a job to resume after specified hours
        """
        resume_time = datetime.now() + timedelta(hours=hours_delay)
        
        self.scheduler.add_job(
            func=self._resume_job_callback,
            trigger=DateTrigger(run_date=resume_time),
            id=f"{job_id}_resume",
            args=[job_id],
            replace_existing=True
        )
        
        logger.info(f"Job {job_id} scheduled to resume at {resume_time}")
        
    def _resume_job_callback(self, job_id: str):
        """
        Callback function to resume a job
        """
        self.resume_job(job_id)
        
        # Also need to record the resume event
        asyncio.create_task(self._record_resume_event(job_id))
        
    async def _record_resume_event(self, job_id: str):
        """
        Record job resume event in database
        """
        try:
            from scheduler.job_manager import record_job_event
            await record_job_event(
                status="resumed",
                error_message="任務已自動恢復"
            )
        except Exception as e:
            logger.error(f"Failed to record resume event: {e}")
        
    def is_job_running(self, job_id: str = "corporate_events_scraper") -> bool:
        """
        Check if a job is currently scheduled and not paused
        """
        job = self.scheduler.get_job(job_id)
        return job is not None and job_id not in self._paused_jobs
        
    def is_job_paused(self, job_id: str = "corporate_events_scraper") -> bool:
        """
        Check if a job is paused
        """
        return job_id in self._paused_jobs
        
    def get_job_info(self, job_id: str = "corporate_events_scraper") -> Optional[dict]:
        """
        Get information about a specific job
        """
        job = self.scheduler.get_job(job_id)
        if job:
            return {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time,
                "is_paused": job_id in self._paused_jobs
            }
        return None
        
    def get_next_run_time(self, job_id: str = "corporate_events_scraper") -> Optional[datetime]:
        """
        Get the next run time for a job
        """
        job = self.scheduler.get_job(job_id)
        return job.next_run_time if job else None

    def get_all_jobs(self) -> list:
        """
        Get information about all scheduled jobs
        
        Returns:
            List of job information dictionaries
        """
        if not self.is_running:
            return []
            
        # Import Taiwan datetime formatting function
        from core.datetime_utils import format_datetime_taiwan
            
        jobs_info = []
        for job in self.scheduler.get_jobs():
            job_info = {
                "id": job.id,
                "name": job.name,
                "function": f"{job.func.__module__}.{job.func.__name__}",
                "trigger": str(job.trigger),
                "next_run_time": format_datetime_taiwan(job.next_run_time),
                "is_paused": job.id in self._paused_jobs,
                "max_instances": getattr(job, 'max_instances', 1),
                "args": job.args,
                "kwargs": job.kwargs
            }
            jobs_info.append(job_info)
            
        return jobs_info

    def get_scheduler_summary(self) -> dict:
        """
        Get a comprehensive summary of the scheduler status
        
        Returns:
            Dictionary containing scheduler and jobs information
        """
        jobs = self.get_all_jobs()
        
        summary = {
            "scheduler_enabled": settings.SCHEDULER_ENABLED,
            "scheduler_running": self.is_running,
            "scheduler_timezone": settings.SCHEDULER_TIMEZONE,
            "total_jobs": len(jobs),
            "active_jobs": len([j for j in jobs if not j["is_paused"]]),
            "paused_jobs": len([j for j in jobs if j["is_paused"]]),
            "jobs": jobs,
            "settings": {
                "scraper_interval_hours": settings.SCRAPER_JOB_INTERVAL_HOURS,
                "job_max_instances": settings.JOB_MAX_INSTANCES,
                "job_retry_max": settings.JOB_RETRY_MAX
            }
        }
        
        return summary


# Global scheduler manager instance
scheduler_manager = SchedulerManager()
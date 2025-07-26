import asyncio
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from database.session import get_db
from crud.crud_job_execution_history import crud_job_execution_history
from schemas.job_execution_history import JobExecutionHistoryCreate, JobExecutionHistoryUpdate
from core.config import settings

logger = logging.getLogger(__name__)


async def execute_corporate_events_job():
    """
    Main function to execute the corporate events scraper job
    Handles retry logic, error handling, and database logging
    """
    db = next(get_db())
    
    try:
        # Clean up old records first (3 months)
        cleaned_count = crud_job_execution_history.cleanup_old_records(db)
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old execution records")
        
        # Check if job is currently paused
        if crud_job_execution_history.is_job_paused(db):
            logger.info("Job is paused, skipping execution")
            return
            
        # Check consecutive failures
        consecutive_failures = crud_job_execution_history.get_consecutive_failures(db)
        if consecutive_failures >= settings.JOB_RETRY_MAX:
            logger.warning(f"Job has {consecutive_failures} consecutive failures, pausing job")
            await _pause_job_due_to_failures(db, consecutive_failures)
            return
            
        # Create initial execution record
        execution_record = _create_execution_record(db, "running")
        
        # Execute the scraper job with retry logic
        await _execute_with_retry(db, execution_record)
        
    except Exception as e:
        logger.error(f"Unexpected error in job execution: {e}")
    finally:
        db.close()


async def _execute_with_retry(db: Session, execution_record):
    """
    Execute the scraper job with retry logic
    """
    start_time = time.time()
    retry_count = 0
    max_retries = settings.JOB_RETRY_MAX
    
    while retry_count <= max_retries:
        try:
            # Call the actual scraper API
            result = await _call_corporate_events_scraper(db)
            
            # Calculate duration
            duration = int(time.time() - start_time)
            
            # Update execution record with success
            update_data = JobExecutionHistoryUpdate(
                status="success",
                completed_at=datetime.utcnow(),
                duration=duration,
                scraped_count=result.get("total_scraped", 0),
                saved_new_count=result.get("total_saved_new", 0),
                result_data=result,
                retry_count=retry_count
            )
            
            crud_job_execution_history.update(db=db, db_obj=execution_record, obj_in=update_data)
            logger.info(f"✅ Job executed successfully in {duration}s, scraped: {result.get('total_scraped', 0)}, saved new: {result.get('total_saved_new', 0)}")
            return
            
        except Exception as e:
            retry_count += 1
            error_message = str(e)
            
            if retry_count > max_retries:
                # Final failure - update record
                duration = int(time.time() - start_time)
                update_data = JobExecutionHistoryUpdate(
                    status="failed",
                    completed_at=datetime.utcnow(),
                    duration=duration,
                    error_message=error_message,
                    retry_count=retry_count
                )
                
                crud_job_execution_history.update(db=db, db_obj=execution_record, obj_in=update_data)
                logger.error(f"❌ Job failed after {retry_count} attempts: {error_message}")
                
                # Send failure notification
                await _send_failure_notification(error_message, retry_count)
                return
            else:
                # Wait before retry
                wait_time = 60 * retry_count  # 1min, 2min, 3min
                logger.warning(f"Job failed (attempt {retry_count}/{max_retries}), retrying in {wait_time}s: {error_message}")
                await asyncio.sleep(wait_time)


async def _call_corporate_events_scraper(db: Session) -> Dict[str, Any]:
    """
    Call the corporate events scraper API internally
    """
    try:
        # Import here to avoid circular imports
        from app.api.v1.endpoints.scraper import get_corporate_events
        
        # Call the scraper function directly
        response = await get_corporate_events(db=db)
        
        if not response.success:
            raise Exception(f"Scraper API failed: {response.message}")
            
        return response.data
        
    except Exception as e:
        logger.error(f"Error calling corporate events scraper: {e}")
        raise


def _create_execution_record(db: Session, status: str, error_message: str = None, job_name: str = "corporate_events_scraper") -> object:
    """
    Create a new execution record in the database
    """
    execution_data = JobExecutionHistoryCreate(
        job_name=job_name,
        status=status,
        started_at=datetime.utcnow(),
        error_message=error_message
    )
    
    return crud_job_execution_history.create(db=db, obj_in=execution_data)


async def _pause_job_due_to_failures(db: Session, consecutive_failures: int):
    """
    Pause the job due to consecutive failures
    """
    try:
        # Import here to avoid circular imports
        from scheduler.job_scheduler import scheduler_manager
        
        # Pause the job in scheduler
        scheduler_manager.pause_job("corporate_events_scraper")
        
        # Schedule resume after 6 hours
        scheduler_manager.schedule_job_resume("corporate_events_scraper", hours_delay=6)
        
        # Record the pause event
        await record_job_event(
            status="paused",
            error_message=f"連續失敗 {consecutive_failures} 次，任務已暫停，將於 6 小時後自動恢復"
        )
        
        # Send notification
        await _send_failure_notification(
            f"任務連續失敗 {consecutive_failures} 次已暫停",
            consecutive_failures
        )
        
        logger.warning(f"Job paused due to {consecutive_failures} consecutive failures, will resume in 6 hours")
        
    except Exception as e:
        logger.error(f"Failed to pause job: {e}")


async def record_job_event(status: str, error_message: str = None, job_name: str = "corporate_events_scraper"):
    """
    Record a job event (pause, resume, etc.) in the database
    """
    db = next(get_db())
    try:
        execution_data = JobExecutionHistoryCreate(
            job_name=job_name,
            status=status,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            error_message=error_message
        )
        
        crud_job_execution_history.create(db=db, obj_in=execution_data)
        logger.info(f"Recorded job event: {status} for {job_name}")
        
    except Exception as e:
        logger.error(f"Failed to record job event: {e}")
    finally:
        db.close()


async def _send_failure_notification(error_message: str, retry_count: int):
    """
    Send failure notification (email placeholder)
    """
    try:
        # Import here to avoid circular imports
        from notifications.job_notifications import send_job_failure_notification
        await send_job_failure_notification(error_message, retry_count)
    except Exception as e:
        logger.error(f"Failed to send failure notification: {e}")


# Manual trigger function for API endpoints
async def execute_notification_job():
    """
    Main function to execute the notification processing job
    Handles retry logic, error handling, and database logging
    """
    db = next(get_db())
    
    try:
        # Clean up old records first (3 months) - shared with scraper job
        cleaned_count = crud_job_execution_history.cleanup_old_records(db)
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old execution records")
        
        # Check if notification job is currently paused
        if crud_job_execution_history.is_job_paused(db, job_name="notification_processor"):
            logger.info("Notification job is paused, skipping execution")
            return
            
        # Check consecutive failures for notification job
        consecutive_failures = crud_job_execution_history.get_consecutive_failures(db, job_name="notification_processor")
        if consecutive_failures >= settings.JOB_RETRY_MAX:
            logger.warning(f"Notification job has {consecutive_failures} consecutive failures, pausing job")
            await _pause_notification_job_due_to_failures(db, consecutive_failures)
            return
            
        # Create initial execution record
        execution_record = _create_execution_record(db, "running", job_name="notification_processor")
        
        # Execute the notification job with retry logic
        await _execute_notification_with_retry(db, execution_record)
        
    except Exception as e:
        logger.error(f"Unexpected error in notification job execution: {e}")
    finally:
        db.close()


async def _execute_notification_with_retry(db: Session, execution_record):
    """
    Execute the notification job with retry logic
    """
    start_time = time.time()
    retry_count = 0
    max_retries = settings.JOB_RETRY_MAX
    
    while retry_count <= max_retries:
        try:
            # Call the actual notification processor
            result = await _call_notification_processor()
            
            # Calculate duration
            duration = int(time.time() - start_time)
            
            # Update execution record with success
            update_data = JobExecutionHistoryUpdate(
                status="success",
                completed_at=datetime.utcnow(),
                duration=duration,
                scraped_count=result.get("users_processed", 0),  # Track users processed
                saved_new_count=result.get("notifications_sent", 0),  # Track notifications sent
                result_data=result,
                retry_count=retry_count
            )
            
            crud_job_execution_history.update(db=db, db_obj=execution_record, obj_in=update_data)
            logger.info(f"✅ Notification job executed successfully in {duration}s, users processed: {result.get('users_processed', 0)}, notifications sent: {result.get('notifications_sent', 0)}")
            return
            
        except Exception as e:
            retry_count += 1
            error_message = str(e)
            
            if retry_count > max_retries:
                # Final failure - update record
                duration = int(time.time() - start_time)
                update_data = JobExecutionHistoryUpdate(
                    status="failed",
                    completed_at=datetime.utcnow(),
                    duration=duration,
                    error_message=error_message,
                    retry_count=retry_count
                )
                
                crud_job_execution_history.update(db=db, db_obj=execution_record, obj_in=update_data)
                logger.error(f"❌ Notification job failed after {retry_count} attempts: {error_message}")
                
                # Send failure notification
                await _send_notification_failure_notification(error_message, retry_count)
                return
            else:
                # Wait before retry
                wait_time = 60 * retry_count  # 1min, 2min, 3min
                logger.warning(f"Notification job failed (attempt {retry_count}/{max_retries}), retrying in {wait_time}s: {error_message}")
                await asyncio.sleep(wait_time)


async def _call_notification_processor() -> Dict[str, Any]:
    """
    Call the notification processor function
    """
    try:
        # Import here to avoid circular imports
        from app.jobs.notification_job import process_and_notify_users
        
        # Track execution results
        result = {
            "users_processed": 0,
            "notifications_sent": 0,
            "events_processed": 0,
            "execution_time": datetime.utcnow().isoformat()
        }
        
        # Execute the notification processing function (sync function)
        process_and_notify_users()
        
        # For now, return basic result - can enhance with actual metrics later
        result.update({
            "users_processed": 1,  # Placeholder - enhance to track actual metrics
            "notifications_sent": 1,  # Placeholder - enhance to track actual metrics
            "status": "completed"
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Error calling notification processor: {e}")
        raise


async def _pause_notification_job_due_to_failures(db: Session, consecutive_failures: int):
    """
    Pause the notification job due to consecutive failures
    """
    try:
        # Import here to avoid circular imports
        from scheduler.job_scheduler import scheduler_manager
        
        # Pause the job in scheduler
        scheduler_manager.pause_job("notification_processor")
        
        # Schedule resume after 6 hours
        scheduler_manager.schedule_job_resume("notification_processor", hours_delay=6)
        
        # Record the pause event
        await record_job_event(
            status="paused",
            error_message=f"通知任務連續失敗 {consecutive_failures} 次，任務已暫停，將於 6 小時後自動恢復",
            job_name="notification_processor"
        )
        
        # Send notification
        await _send_notification_failure_notification(
            f"通知任務連續失敗 {consecutive_failures} 次已暫停",
            consecutive_failures
        )
        
        logger.warning(f"Notification job paused due to {consecutive_failures} consecutive failures, will resume in 6 hours")
        
    except Exception as e:
        logger.error(f"Failed to pause notification job: {e}")


async def _send_notification_failure_notification(error_message: str, retry_count: int):
    """
    Send failure notification for notification job (email placeholder)
    """
    try:
        # Import here to avoid circular imports
        from notifications.job_notifications import send_job_failure_notification
        await send_job_failure_notification(f"Notification Job: {error_message}", retry_count)
    except Exception as e:
        logger.error(f"Failed to send notification job failure notification: {e}")


async def trigger_corporate_events_job() -> Dict[str, Any]:
    """
    Manually trigger the corporate events job
    Used by API endpoints for manual execution
    """
    logger.info("Manual job trigger requested")
    await execute_corporate_events_job()
    return {"message": "Job execution triggered"}


async def trigger_notification_job() -> Dict[str, Any]:
    """
    Manually trigger the notification processing job
    Used by API endpoints for manual execution
    """
    logger.info("Manual notification job trigger requested")
    await execute_notification_job()
    return {"message": "Notification job execution triggered"}


# Job control functions
async def get_job_status() -> Dict[str, Any]:
    """
    Get current job status information
    """
    db = next(get_db())
    try:
        # Import here to avoid circular imports
        from scheduler.job_scheduler import scheduler_manager
        from core.datetime_utils import format_datetime_taiwan
        
        # Get scheduler status
        is_running = scheduler_manager.is_job_running("corporate_events_scraper")
        is_paused = scheduler_manager.is_job_paused("corporate_events_scraper")
        next_run_time = scheduler_manager.get_next_run_time("corporate_events_scraper")
        
        # Get latest execution
        latest_execution = crud_job_execution_history.get_latest_execution(db)
        
        # Get consecutive failures
        consecutive_failures = crud_job_execution_history.get_consecutive_failures(db)
        
        status = "stopped"
        if is_paused:
            status = "paused"
        elif is_running:
            status = "running"
            
        result = {
            "job_status": status,
            "last_execution_time": format_datetime_taiwan(latest_execution.started_at) if latest_execution else None,
            "last_execution_result": {
                "status": latest_execution.status,
                "scraped_count": latest_execution.scraped_count,
                "saved_new_count": latest_execution.saved_new_count,
                "duration": latest_execution.duration,
                "error_message": latest_execution.error_message
            } if latest_execution else None,
            "next_run_time": format_datetime_taiwan(next_run_time),
            "is_paused": is_paused,
            "consecutive_failures": consecutive_failures
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise
    finally:
        db.close()


async def stop_job() -> Dict[str, Any]:
    """
    Stop/pause the job manually
    """
    try:
        from scheduler.job_scheduler import scheduler_manager
        
        success = scheduler_manager.pause_job("corporate_events_scraper")
        
        if success:
            await record_job_event(
                status="paused", 
                error_message="任務已手動停止"
            )
            return {"message": "Job stopped successfully"}
        else:
            return {"message": "Failed to stop job"}
            
    except Exception as e:
        logger.error(f"Error stopping job: {e}")
        raise
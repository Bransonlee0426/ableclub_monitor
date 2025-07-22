from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from models.job_execution_history import JobExecutionHistory
from schemas.job_execution_history import JobExecutionHistoryCreate, JobExecutionHistoryUpdate


class CRUDJobExecutionHistory:
    def create(self, db: Session, *, obj_in: JobExecutionHistoryCreate) -> JobExecutionHistory:
        """
        Create a new job execution history record
        """
        db_obj = JobExecutionHistory(
            job_name=obj_in.job_name,
            status=obj_in.status,
            started_at=obj_in.started_at,
            completed_at=obj_in.completed_at,
            duration=obj_in.duration,
            scraped_count=obj_in.scraped_count,
            saved_new_count=obj_in.saved_new_count,
            result_data=obj_in.result_data,
            error_message=obj_in.error_message,
            retry_count=obj_in.retry_count
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int) -> Optional[JobExecutionHistory]:
        """
        Get job execution history by ID
        """
        return db.query(JobExecutionHistory).filter(JobExecutionHistory.id == id).first()

    def get_by_job_name(
        self, 
        db: Session, 
        job_name: str = "corporate_events_scraper",
        skip: int = 0,
        limit: int = 10
    ) -> List[JobExecutionHistory]:
        """
        Get job execution history by job name with pagination
        """
        return (
            db.query(JobExecutionHistory)
            .filter(JobExecutionHistory.job_name == job_name)
            .order_by(desc(JobExecutionHistory.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_latest_execution(
        self, 
        db: Session, 
        job_name: str = "corporate_events_scraper"
    ) -> Optional[JobExecutionHistory]:
        """
        Get the latest execution record for a job
        """
        return (
            db.query(JobExecutionHistory)
            .filter(JobExecutionHistory.job_name == job_name)
            .order_by(desc(JobExecutionHistory.created_at))
            .first()
        )

    def get_consecutive_failures(
        self, 
        db: Session, 
        job_name: str = "corporate_events_scraper"
    ) -> int:
        """
        Count consecutive failures from the latest execution backwards
        """
        recent_executions = (
            db.query(JobExecutionHistory)
            .filter(JobExecutionHistory.job_name == job_name)
            .order_by(desc(JobExecutionHistory.created_at))
            .limit(10)
            .all()
        )
        
        consecutive_failures = 0
        for execution in recent_executions:
            if execution.status == "failed":
                consecutive_failures += 1
            else:
                break
                
        return consecutive_failures

    def update(
        self, 
        db: Session, 
        *, 
        db_obj: JobExecutionHistory, 
        obj_in: JobExecutionHistoryUpdate
    ) -> JobExecutionHistory:
        """
        Update job execution history record
        """
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def cleanup_old_records(
        self, 
        db: Session, 
        job_name: str = "corporate_events_scraper",
        months_to_keep: int = 3
    ) -> int:
        """
        Clean up job execution history records older than specified months
        Returns number of deleted records
        """
        cutoff_date = datetime.utcnow() - timedelta(days=months_to_keep * 30)
        
        deleted_count = (
            db.query(JobExecutionHistory)
            .filter(
                and_(
                    JobExecutionHistory.job_name == job_name,
                    JobExecutionHistory.created_at < cutoff_date
                )
            )
            .delete()
        )
        
        db.commit()
        return deleted_count

    def get_execution_stats(
        self, 
        db: Session, 
        job_name: str = "corporate_events_scraper",
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get execution statistics for the last N days
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        executions = (
            db.query(JobExecutionHistory)
            .filter(
                and_(
                    JobExecutionHistory.job_name == job_name,
                    JobExecutionHistory.created_at >= start_date,
                    JobExecutionHistory.status.in_(["success", "failed"])
                )
            )
            .all()
        )
        
        total_executions = len(executions)
        successful_executions = len([e for e in executions if e.status == "success"])
        failed_executions = len([e for e in executions if e.status == "failed"])
        
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
        
        # Calculate average duration for successful executions
        successful_durations = [e.duration for e in executions if e.status == "success" and e.duration]
        avg_duration = sum(successful_durations) / len(successful_durations) if successful_durations else 0
        
        # Get recent failure reasons
        recent_failures = [
            e.error_message for e in executions 
            if e.status == "failed" and e.error_message
        ][:3]  # Last 3 failure reasons
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": round(success_rate, 1),
            "average_duration_seconds": round(avg_duration, 1),
            "recent_failure_reasons": recent_failures
        }

    def is_job_paused(
        self, 
        db: Session, 
        job_name: str = "corporate_events_scraper"
    ) -> bool:
        """
        Check if the job is currently paused
        """
        latest_execution = self.get_latest_execution(db, job_name)
        return latest_execution and latest_execution.status == "paused"


crud_job_execution_history = CRUDJobExecutionHistory()
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class JobExecutionHistoryBase(BaseModel):
    """
    Base schema for job execution history
    """
    job_name: str = "corporate_events_scraper"
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[int] = None
    scraped_count: Optional[int] = None
    saved_new_count: Optional[int] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0


class JobExecutionHistoryCreate(JobExecutionHistoryBase):
    """
    Schema for creating job execution history record
    """
    pass


class JobExecutionHistoryUpdate(BaseModel):
    """
    Schema for updating job execution history record
    """
    status: Optional[str] = None
    completed_at: Optional[datetime] = None
    duration: Optional[int] = None
    scraped_count: Optional[int] = None
    saved_new_count: Optional[int] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: Optional[int] = None


class JobExecutionHistoryInDB(JobExecutionHistoryBase):
    """
    Schema for job execution history in database
    """
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class JobExecutionHistoryResponse(JobExecutionHistoryInDB):
    """
    Schema for job execution history API response
    """
    pass


class JobStatsResponse(BaseModel):
    """
    Schema for job execution statistics
    """
    total_executions: int
    successful_executions: int
    failed_executions: int
    success_rate: float
    average_duration_seconds: float
    recent_failure_reasons: list[str]


class JobStatusResponse(BaseModel):
    """
    Schema for job status response
    """
    job_status: str  # "running", "stopped", "paused"
    last_execution_time: Optional[datetime] = None
    last_execution_result: Optional[Dict[str, Any]] = None
    next_run_time: Optional[datetime] = None
    is_paused: bool = False
    consecutive_failures: int = 0
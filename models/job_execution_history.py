from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.sql import func
from database.session import Base


class JobExecutionHistory(Base):
    """
    Job execution history model for tracking scheduled task executions
    """
    __tablename__ = "job_execution_history"

    id = Column(Integer, primary_key=True, index=True)
    job_name = Column(String(100), nullable=False, default="corporate_events_scraper", index=True)
    status = Column(String(50), nullable=False, index=True)  # "running", "success", "failed", "paused", "resumed"
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, nullable=True)  # Duration in seconds
    scraped_count = Column(Integer, nullable=True)  # Number of events scraped
    saved_new_count = Column(Integer, nullable=True)  # Number of new events saved
    result_data = Column(JSON, nullable=True)  # Complete scraping result data
    error_message = Column(Text, nullable=True)  # Error message if failed
    retry_count = Column(Integer, default=0, nullable=False)  # Number of retries attempted
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<JobExecutionHistory(id={self.id}, job_name={self.job_name}, status={self.status}, started_at={self.started_at})>"
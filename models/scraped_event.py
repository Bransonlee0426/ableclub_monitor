from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from database.session import Base


class ScrapedEvent(Base):
    """
    SQLAlchemy model representing the 'scraped_events' table in the database.
    Stores events scraped from AbleClub website with composite unique constraint.
    """
    __tablename__ = "scraped_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    start_date = Column(Date, index=True, nullable=False)
    end_date = Column(Date, nullable=True)
    is_processed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('title', 'start_date', name='_title_start_date_uc'),
    )
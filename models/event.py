from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, ConfigDict
import datetime

# SQLAlchemy model base class
Base = declarative_base()

# --- Pydantic Models (for API data validation) ---
class EventBase(BaseModel):
    """
    Pydantic model for basic event data. Used for creation and reading.
    """
    title: str | None = None
    url: str | None = None

    model_config = ConfigDict(
        # Allows the model to be created from ORM objects
        from_attributes=True
    )

# --- SQLAlchemy Model (for database interaction) ---
class Event(Base):
    """
    SQLAlchemy model representing the 'events' table in the database.
    """
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

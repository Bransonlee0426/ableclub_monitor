from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime
from core.datetime_utils import TaiwanDatetimeMixin, datetime_field


class ScrapedEventBase(BaseModel):
    """
    Base Pydantic model for ScrapedEvent containing core fields.
    Used as a foundation for other ScrapedEvent schemas.
    """
    title: str
    start_date: date
    end_date: Optional[date] = None


class ScrapedEventCreate(ScrapedEventBase):
    """
    Pydantic model for creating a new ScrapedEvent.
    Inherits all fields from ScrapedEventBase without modification.
    """
    pass


class ScrapedEvent(ScrapedEventBase, TaiwanDatetimeMixin):
    """
    Pydantic model for ScrapedEvent API responses.
    Includes additional fields beyond the base model for complete representation.
    """
    id: int
    is_processed: bool
    created_at: datetime = datetime_field("建立時間")
    
    model_config = ConfigDict(from_attributes=True)
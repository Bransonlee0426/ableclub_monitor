"""
Datetime utilities for consistent time formatting across the application
"""
from datetime import datetime
import pytz
from typing import Optional
from pydantic import field_serializer, Field

# Taiwan timezone
TAIWAN_TZ = pytz.timezone('Asia/Taipei')

def format_datetime_taiwan(dt: Optional[datetime]) -> Optional[str]:
    """
    Convert datetime to Taiwan timezone and format as YYYY-MM-DD-HH:mm
    
    Args:
        dt: datetime object (can be timezone-aware or naive)
        
    Returns:
        Formatted string in YYYY-MM-DD-HH:mm format or None if input is None
    """
    if dt is None:
        return None
    
    # If datetime is naive, assume it's UTC
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    
    # Convert to Taiwan timezone
    taiwan_dt = dt.astimezone(TAIWAN_TZ)
    
    # Format as YYYY-MM-DD-HH:mm
    return taiwan_dt.strftime('%Y-%m-%d-%H:%M')

def datetime_field(description: str) -> Field:
    """
    Create a datetime field that automatically formats to Taiwan time
    
    Args:
        description: Field description
        
    Returns:
        Pydantic Field with custom serializer
    """
    return Field(
        ..., 
        description=description,
        json_schema_extra={
            "example": "2024-01-01-00:00",
            "format": "YYYY-MM-DD-HH:mm (Taiwan Time)"
        }
    )

class TaiwanDatetimeMixin:
    """
    Mixin class to add Taiwan datetime formatting to Pydantic models
    """
    
    @field_serializer('created_at', 'updated_at', 'execution_time', 'started_at', 'ended_at', 
                     'expires_at', 'completed_at', 'last_execution_time', 'next_run_time',
                     when_used='json', check_fields=False)
    def serialize_datetime_fields(self, value: Optional[datetime]) -> Optional[str]:
        """Serialize datetime fields to Taiwan timezone format"""
        return format_datetime_taiwan(value)
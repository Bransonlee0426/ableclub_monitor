from sqlalchemy.orm import Session
from models.scraped_event import ScrapedEvent
from schemas.scraped_event import ScrapedEventCreate
from typing import Optional, List
from datetime import date


def create_or_ignore(db: Session, event_in: ScrapedEventCreate) -> ScrapedEvent:
    """
    Create a new ScrapedEvent or return existing one if title and start_date combination already exists.
    
    Args:
        db: Database session
        event_in: ScrapedEventCreate schema with event data
        
    Returns:
        ScrapedEvent object (either existing or newly created)
    """
    # Check if event with same title and start_date already exists
    existing_event = db.query(ScrapedEvent).filter(
        ScrapedEvent.title == event_in.title,
        ScrapedEvent.start_date == event_in.start_date
    ).first()
    
    if existing_event:
        return existing_event
    
    # Create new event if it doesn't exist
    db_obj = ScrapedEvent(**event_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_event_by_id(db: Session, event_id: int) -> Optional[ScrapedEvent]:
    """
    Get a ScrapedEvent by its ID.
    
    Args:
        db: Database session
        event_id: ID of the event to retrieve
        
    Returns:
        ScrapedEvent object if found, None otherwise
    """
    return db.query(ScrapedEvent).filter(ScrapedEvent.id == event_id).first()


def get_event_by_title_and_date(db: Session, title: str, start_date: date) -> Optional[ScrapedEvent]:
    """
    Get a ScrapedEvent by its title and start_date combination.
    
    Args:
        db: Database session
        title: Title of the event
        start_date: Start date of the event
        
    Returns:
        ScrapedEvent object if found, None otherwise
    """
    return db.query(ScrapedEvent).filter(
        ScrapedEvent.title == title,
        ScrapedEvent.start_date == start_date
    ).first()


def get_events(db: Session, skip: int = 0, limit: int = 100) -> List[ScrapedEvent]:
    """
    Get a list of ScrapedEvents with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        List of ScrapedEvent objects
    """
    return db.query(ScrapedEvent).offset(skip).limit(limit).all()


def get_unprocessed_events(db: Session, skip: int = 0, limit: int = 100) -> List[ScrapedEvent]:
    """
    Get a list of unprocessed ScrapedEvents.
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        List of unprocessed ScrapedEvent objects
    """
    return db.query(ScrapedEvent).filter(
        ScrapedEvent.is_processed == False
    ).offset(skip).limit(limit).all()



def delete_event(db: Session, event_id: int) -> bool:
    """
    Delete a ScrapedEvent by its ID.
    
    Args:
        db: Database session
        event_id: ID of the event to delete
        
    Returns:
        True if event was deleted, False if event was not found
    """
    event = db.query(ScrapedEvent).filter(ScrapedEvent.id == event_id).first()
    if event:
        db.delete(event)
        db.commit()
        return True
    return False
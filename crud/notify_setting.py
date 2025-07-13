# This file contains all the database operations (CRUD) for the NotifySetting model.
from sqlalchemy.orm import Session
from models.notify_setting import NotifySetting
from schemas.notify_setting import NotifySettingCreate, NotifySettingUpdate
from typing import Optional, List, Tuple


def create_notify_setting(
    db: Session, 
    user_id: int, 
    notify_setting_data: NotifySettingCreate
) -> NotifySetting:
    """
    Create a new notification setting for a user.
    
    Args:
        db: Database session
        user_id: ID of the user (extracted from JWT token)
        notify_setting_data: Notification setting creation data
        
    Returns:
        Created NotifySetting object
    """
    db_notify_setting = NotifySetting(
        user_id=user_id,
        notify_type=notify_setting_data.notify_type,
        email_address=notify_setting_data.email_address,
        is_active=True
    )
    
    db.add(db_notify_setting)
    db.commit()
    db.refresh(db_notify_setting)
    
    return db_notify_setting


def get_notify_setting_by_id(
    db: Session, 
    notify_setting_id: int, 
    user_id: int
) -> Optional[NotifySetting]:
    """
    Get a notification setting by ID and user ID.
    
    Args:
        db: Database session
        notify_setting_id: ID of the notification setting
        user_id: ID of the user (for ownership verification)
        
    Returns:
        NotifySetting object if found and owned by user, None otherwise
    """
    return db.query(NotifySetting).filter(
        NotifySetting.id == notify_setting_id,
        NotifySetting.user_id == user_id
    ).first()


def get_notify_setting_by_user_and_type(
    db: Session, 
    user_id: int, 
    notify_type: str
) -> Optional[NotifySetting]:
    """
    Get a notification setting by user ID and notification type.
    Used to check for duplicates before creation.
    
    Args:
        db: Database session
        user_id: ID of the user
        notify_type: Type of notification
        
    Returns:
        NotifySetting object if found, None otherwise
    """
    return db.query(NotifySetting).filter(
        NotifySetting.user_id == user_id,
        NotifySetting.notify_type == notify_type
    ).first()


def get_user_notify_settings(
    db: Session, 
    user_id: int
) -> Tuple[List[NotifySetting], int]:
    """
    Get all notification settings for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Tuple of (notify_settings_list, total_count)
    """
    query = db.query(NotifySetting).filter(NotifySetting.user_id == user_id)
    
    # Get total count
    total = query.count()
    
    # Get all settings ordered by creation date (newest first)
    notify_settings = query.order_by(NotifySetting.created_at.desc()).all()
    
    return notify_settings, total


def update_notify_setting(
    db: Session, 
    notify_setting_id: int, 
    user_id: int, 
    update_data: NotifySettingUpdate
) -> Optional[NotifySetting]:
    """
    Update a notification setting.
    
    Args:
        db: Database session
        notify_setting_id: ID of the notification setting
        user_id: ID of the user (for ownership verification)
        update_data: Update data
        
    Returns:
        Updated NotifySetting object if found and updated, None otherwise
    """
    db_notify_setting = get_notify_setting_by_id(db, notify_setting_id, user_id)
    
    if not db_notify_setting:
        return None
    
    # Update fields that are provided
    update_dict = update_data.model_dump(exclude_unset=True)
    
    for field, value in update_dict.items():
        setattr(db_notify_setting, field, value)
    
    db.commit()
    db.refresh(db_notify_setting)
    
    return db_notify_setting


def delete_notify_setting(
    db: Session, 
    notify_setting_id: int, 
    user_id: int
) -> bool:
    """
    Delete a notification setting.
    
    Args:
        db: Database session
        notify_setting_id: ID of the notification setting
        user_id: ID of the user (for ownership verification)
        
    Returns:
        True if deleted successfully, False if not found
    """
    db_notify_setting = get_notify_setting_by_id(db, notify_setting_id, user_id)
    
    if not db_notify_setting:
        return False
    
    db.delete(db_notify_setting)
    db.commit()
    
    return True


def validate_final_state(notify_type: str, email_address: Optional[str]) -> bool:
    """
    Validate the final state of a notification setting.
    Used during updates to ensure data consistency.
    
    Args:
        notify_type: Type of notification
        email_address: Email address (can be None)
        
    Returns:
        True if valid, False if invalid
    """
    if notify_type == "email":
        return email_address is not None and email_address.strip() != ""
    return True
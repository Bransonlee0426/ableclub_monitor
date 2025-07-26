# This file contains all the database operations (CRUD) for the NotifySetting model.
from sqlalchemy.orm import Session, joinedload, selectinload
from models.notify_setting import NotifySetting
from models.user import User
from models.keyword import Keyword
from schemas.notify_setting import NotifySettingCreate, NotifySettingUpdate
from crud import keyword as crud_keyword
from typing import Optional, List, Tuple


def get_by_owner(db: Session, owner_id: int) -> Optional[NotifySetting]:
    """
    Gets a notification setting by owner_id, eagerly loading related user and keywords.
    This is the definitive method to fetch the setting object, ensuring all data
    needed for API serialization is loaded upfront to prevent lazy-load issues.
    """
    return (
        db.query(NotifySetting)
        .filter(NotifySetting.user_id == owner_id)
        .options(
            # Use joinedload for the one-to-one relationship (NotifySetting -> User)
            # Then, use selectinload for the one-to-many relationship (User -> Keywords)
            joinedload(NotifySetting.user).selectinload(User.keywords)
        )
        .first()
    )


def create_with_owner(
    db: Session, 
    owner_id: int, 
    obj_in: NotifySettingCreate
) -> NotifySetting:
    """
    Create a new notification setting for an owner (user) with keywords.
    
    Args:
        db: Database session
        owner_id: ID of the user (owner)
        obj_in: Notification setting creation data including keywords
        
    Returns:
        Created NotifySetting object
    """
    try:
        # Extract keywords from the schema data
        keywords_list = obj_in.keywords if hasattr(obj_in, 'keywords') else []
        
        # Create the notification setting object (excluding keywords from the data)
        notify_setting_dict = obj_in.model_dump(exclude={'keywords'})
        
        db_notify_setting = NotifySetting(
            user_id=owner_id,
            **notify_setting_dict,
            is_active=True
        )
        
        db.add(db_notify_setting)
        db.flush()  # Flush to get ID without committing
        
        # Handle keywords replacement atomically within the same transaction
        if keywords_list:
            try:
                crud_keyword.replace_keywords_for_user(db=db, user_id=owner_id, keywords=keywords_list)
            except Exception as e:
                db.rollback()
                raise e
        
        # Commit the entire transaction (notify setting + keywords)
        db.commit()
        
        # Use a clean query to get the created object instead of refresh
        # This avoids potential state inconsistency issues after commit
        created_setting = get_by_owner(db=db, owner_id=owner_id)
        return created_setting
        
    except Exception as e:
        db.rollback()
        raise e


def create_notify_setting(
    db: Session, 
    user_id: int, 
    notify_setting_data: NotifySettingCreate
) -> NotifySetting:
    """
    Create a new notification setting for a user with keywords.
    
    Args:
        db: Database session
        user_id: ID of the user (extracted from JWT token)
        notify_setting_data: Notification setting creation data including keywords
        
    Returns:
        Created NotifySetting object
    """
    # Extract keywords from the schema data
    keywords_list = notify_setting_data.keywords if hasattr(notify_setting_data, 'keywords') else []
    
    # Create the notification setting object (excluding keywords from the data)
    notify_setting_dict = notify_setting_data.model_dump(exclude={'keywords'})
    
    db_notify_setting = NotifySetting(
        user_id=user_id,
        **notify_setting_dict,
        is_active=True
    )
    
    db.add(db_notify_setting)
    
    # Handle keywords replacement atomically within the same transaction
    if keywords_list:
        crud_keyword.replace_keywords_for_user(db=db, user_id=user_id, keywords=keywords_list)
    
    # Commit the entire transaction (notify setting + keywords)
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


def get_multi(db: Session, *, skip: int = 0, limit: int = 100) -> List[dict]:
    """
    Get multiple notification settings with pagination, including keywords.
    
    This function fetches notification settings with their associated keywords
    to avoid N+1 queries. Each setting includes the user's complete keyword list.
    
    Args:
        db: Database session
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of notification setting dictionaries with keywords included
    """
    from crud.keyword import get_by_user_id as get_keywords_by_user_id
    
    # Get notification settings with pagination
    notify_settings = (
        db.query(NotifySetting)
        .order_by(NotifySetting.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    # Get all unique user IDs to fetch keywords efficiently
    user_ids = list(set(setting.user_id for setting in notify_settings))
    
    # Fetch keywords for all users at once to avoid N+1 queries
    user_keywords_map = {}
    for user_id in user_ids:
        keywords_objs = get_keywords_by_user_id(db, user_id)
        user_keywords_map[user_id] = [keyword.keyword for keyword in keywords_objs]
    
    # Convert notification settings to dicts and add keywords
    settings_with_keywords = []
    for setting in notify_settings:
        setting_dict = {
            "id": setting.id,
            "user_id": setting.user_id,
            "notify_type": setting.notify_type,
            "email_address": setting.email_address,
            "is_active": setting.is_active,
            "created_at": setting.created_at,
            "updated_at": setting.updated_at,
            "keywords": user_keywords_map.get(setting.user_id, [])
        }
        settings_with_keywords.append(setting_dict)
    
    return settings_with_keywords


def get_user_notify_settings(
    db: Session, 
    user_id: int
) -> Tuple[List[NotifySetting], int]:
    """
    Get all notification settings for a user with optimized query to avoid N+1 problem.
    
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


def update(
    db: Session, 
    db_obj: NotifySetting, 
    obj_in: NotifySettingUpdate
) -> NotifySetting:
    """
    Update a notification setting with keywords support.
    
    Args:
        db: Database session
        db_obj: The NotifySetting object to update
        obj_in: Update data including optional keywords
        
    Returns:
        Updated NotifySetting object
    """
    # Extract keywords from update data
    keywords_list = obj_in.keywords if hasattr(obj_in, 'keywords') and obj_in.keywords is not None else None
    
    # Update notification setting fields (excluding keywords)
    update_dict = obj_in.model_dump(exclude_unset=True, exclude={'keywords'})
    
    for field, value in update_dict.items():
        setattr(db_obj, field, value)
    
    # Handle keywords replacement if provided (even if empty array)
    if keywords_list is not None:
        crud_keyword.replace_keywords_for_user(db=db, user_id=db_obj.user_id, keywords=keywords_list)
    
    # Commit all changes (notify setting + keywords if applicable)
    db.commit()
    db.refresh(db_obj)
    
    return db_obj


def update_notify_setting(
    db: Session, 
    notify_setting_id: int, 
    user_id: int, 
    update_data: NotifySettingUpdate
) -> Optional[NotifySetting]:
    """
    Update a notification setting with keywords support.
    
    Args:
        db: Database session
        notify_setting_id: ID of the notification setting
        user_id: ID of the user (for ownership verification)
        update_data: Update data including optional keywords
        
    Returns:
        Updated NotifySetting object if found and updated, None otherwise
    """
    db_notify_setting = get_notify_setting_by_id(db, notify_setting_id, user_id)
    
    if not db_notify_setting:
        return None
    
    # Extract keywords from update data
    keywords_list = update_data.keywords if hasattr(update_data, 'keywords') and update_data.keywords is not None else None
    
    # Update notification setting fields (excluding keywords)
    update_dict = update_data.model_dump(exclude_unset=True, exclude={'keywords'})
    
    for field, value in update_dict.items():
        setattr(db_notify_setting, field, value)
    
    # Handle keywords replacement if provided (even if empty array)
    if keywords_list is not None:
        crud_keyword.replace_keywords_for_user(db=db, user_id=user_id, keywords=keywords_list)
    
    # Commit all changes (notify setting + keywords if applicable)
    db.commit()
    db.refresh(db_notify_setting)
    
    return db_notify_setting


def remove_by_owner(db: Session, owner_id: int) -> bool:
    """
    Delete notification setting by owner (user) ID.
    
    Args:
        db: Database session
        owner_id: ID of the user (owner)
        
    Returns:
        True if deleted successfully, False if not found
    """
    db_notify_setting = get_by_owner(db, owner_id)
    
    if not db_notify_setting:
        return False
    
    db.delete(db_notify_setting)
    db.commit()
    
    return True


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


def get_settings_with_keywords_by_user_id(db: Session, user_id: int) -> Tuple[List[dict], int]:
    """
    Get all notification settings for a user with their keywords included using optimized query.
    This query avoids N+1 problem by using selectinload to eagerly fetch user and keywords.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Tuple of (list of notification settings with keywords as dicts, total count)
    """
    # Optimized query with selectinload to avoid N+1 problem
    query = db.query(NotifySetting).filter(NotifySetting.user_id == user_id)
    
    # Get total count
    total = query.count()
    
    # Get notification settings with eagerly loaded user and keywords relationship
    notify_settings = query.options(
        selectinload(NotifySetting.user).selectinload(User.keywords)
    ).order_by(NotifySetting.created_at.desc()).all()
    
    # Convert to dict format with keywords as string list
    settings_with_keywords = []
    for setting in notify_settings:
        # Get user's keywords and convert to string list
        keywords_list = [keyword.keyword for keyword in setting.user.keywords] if setting.user and setting.user.keywords else []
        
        setting_dict = {
            "id": setting.id,
            "user_id": setting.user_id,
            "notify_type": setting.notify_type,
            "email_address": setting.email_address,
            "is_active": setting.is_active,
            "created_at": setting.created_at,
            "updated_at": setting.updated_at,
            "keywords": keywords_list
        }
        settings_with_keywords.append(setting_dict)
    
    return settings_with_keywords, total
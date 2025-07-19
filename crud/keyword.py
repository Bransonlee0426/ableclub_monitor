# This file contains all the database operations (CRUD) for the Keyword model.
from sqlalchemy.orm import Session
from models.keyword import Keyword
from typing import List


def get_by_user_id(db: Session, user_id: int) -> List[Keyword]:
    """
    Get all keywords for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        List of Keyword objects for the user
    """
    return db.query(Keyword).filter(Keyword.user_id == user_id).all()


def replace_keywords_for_user(db: Session, *, user_id: int, keywords: List[str]) -> None:
    """
    Replace all keywords for a user with a new list using atomic operation.
    This function does NOT commit the transaction, allowing the caller to control commit timing.
    
    Args:
        db: Database session
        user_id: ID of the user
        keywords: List of keyword strings to replace all existing keywords
        
    Returns:
        None (this function does not commit or refresh)
    """
    # First step: Delete all existing keywords for the user
    db.query(Keyword).filter(Keyword.user_id == user_id).delete()
    
    # Second step: Create new keywords for each keyword in the list
    for keyword_text in keywords:
        keyword_obj = Keyword(
            user_id=user_id,
            keyword=keyword_text
        )
        db.add(keyword_obj)
    
    # Important: This function does NOT execute db.commit() or db.refresh()
    # The caller is responsible for committing the transaction


def sync_for_user(db: Session, user_id: int, keywords: List[str]) -> List[Keyword]:
    """
    Synchronize keywords for a user using "delete all then insert" approach.
    This ensures complete replacement of the user's keywords.
    
    Args:
        db: Database session
        user_id: ID of the user
        keywords: List of keyword strings to set for the user
        
    Returns:
        List of created Keyword objects
    """
    # First, delete all existing keywords for the user
    db.query(Keyword).filter(Keyword.user_id == user_id).delete()
    
    # Then, create new keywords
    created_keywords = []
    for keyword_text in keywords:
        keyword_obj = Keyword(
            user_id=user_id,
            keyword=keyword_text
        )
        db.add(keyword_obj)
        created_keywords.append(keyword_obj)
    
    # Commit all changes
    db.commit()
    
    # Refresh all created objects to get their IDs and timestamps
    for keyword_obj in created_keywords:
        db.refresh(keyword_obj)
    
    return created_keywords


def delete_all_for_user(db: Session, user_id: int) -> bool:
    """
    Delete all keywords for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        True if any keywords were deleted, False otherwise
    """
    deleted_count = db.query(Keyword).filter(Keyword.user_id == user_id).delete()
    db.commit()
    return deleted_count > 0 
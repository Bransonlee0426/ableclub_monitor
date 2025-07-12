# This file will contain all the database operations (CRUD) for the User model.
from sqlalchemy.orm import Session
from models.user import User
from schemas.auth import LoginOrRegisterRequest
from core.security import get_password_hash
from typing import Optional, List


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Get a user by username (email).
    
    Args:
        db: Database session
        username: User's username (email address)
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, username: str, password: str, invite_code: Optional[str] = None) -> User:
    """
    Create a new user with hashed password.
    
    Args:
        db: Database session
        username: User's username (email address)
        password: Plain text password
        invite_code: Invitation code used for registration
        
    Returns:
        Created User object
    """
    # Hash the password
    password_hash = get_password_hash(password)
    
    # Create new user instance
    db_user = User(
        username=username,
        password_hash=password_hash,
        invite_code_used=invite_code,
        is_active=True
    )
    
    # Add to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Get a user by ID.
    
    Args:
        db: Database session
        user_id: User's ID
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()


def update_user_active_status(db: Session, user_id: int, is_active: bool) -> Optional[User]:
    """
    Update user's active status.
    
    Args:
        db: Database session
        user_id: User's ID
        is_active: New active status
        
    Returns:
        Updated User object if found, None otherwise
    """
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db_user.is_active = is_active
        db.commit()
        db.refresh(db_user)
    return db_user


def get_users(
    db: Session, 
    is_active: Optional[bool] = None,
    page: int = 1,
    size: int = 20
) -> tuple[List[User], int]:
    """
    Get users with filtering and pagination.
    
    Args:
        db: Database session
        is_active: Filter by active status
        page: Page number (1-based)
        size: Items per page
        
    Returns:
        Tuple of (users_list, total_count)
    """
    query = db.query(User)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    users = query.order_by(User.created_at.desc()).offset(offset).limit(size).all()
    
    return users, total


def soft_delete_user(db: Session, user_id: int) -> Optional[User]:
    """
    Soft delete (deactivate) a user.
    
    Args:
        db: Database session
        user_id: User's ID
        
    Returns:
        Updated User object if found, None otherwise
    """
    return update_user_active_status(db, user_id, False)

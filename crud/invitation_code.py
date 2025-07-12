# This file will contain all the database operations (CRUD) for the InvitationCode model.
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.invitation_code import InvitationCode
from schemas.invitation_code import InvitationCodeCreate, InvitationCodeUpdate
from typing import Optional, List
from datetime import datetime
import math


def get_valid_code(db: Session, code: str) -> InvitationCode | None:
    """
    Get a valid (active) invitation code by code string.
    
    Args:
        db: Database session
        code: Invitation code string
        
    Returns:
        InvitationCode if found and active, None otherwise
    """
    return db.query(InvitationCode).filter(
        and_(
            InvitationCode.code == code,
            InvitationCode.is_active == True
        )
    ).first()


def get_invitation_code_by_id(db: Session, code_id: int) -> Optional[InvitationCode]:
    """
    Get invitation code by ID.
    
    Args:
        db: Database session
        code_id: Invitation code ID
        
    Returns:
        InvitationCode if found, None otherwise
    """
    return db.query(InvitationCode).filter(InvitationCode.id == code_id).first()


def get_invitation_code_by_code(db: Session, code: str) -> Optional[InvitationCode]:
    """
    Get invitation code by code string (regardless of active status).
    
    Args:
        db: Database session
        code: Invitation code string
        
    Returns:
        InvitationCode if found, None otherwise
    """
    return db.query(InvitationCode).filter(InvitationCode.code == code).first()


def create_invitation_code(db: Session, invitation_code: InvitationCodeCreate) -> InvitationCode:
    """
    Create a new invitation code.
    
    Args:
        db: Database session
        invitation_code: Invitation code creation data
        
    Returns:
        Created InvitationCode object
    """
    db_invitation_code = InvitationCode(
        code=invitation_code.code,
        description=invitation_code.description,
        expires_at=invitation_code.expires_at,
        is_active=True
    )
    db.add(db_invitation_code)
    db.commit()
    db.refresh(db_invitation_code)
    return db_invitation_code


def get_invitation_codes(
    db: Session, 
    is_active: Optional[bool] = None,
    page: int = 1,
    size: int = 20
) -> tuple[List[InvitationCode], int]:
    """
    Get invitation codes with filtering and pagination.
    
    Args:
        db: Database session
        is_active: Filter by active status
        page: Page number (1-based)
        size: Items per page
        
    Returns:
        Tuple of (invitation_codes_list, total_count)
    """
    query = db.query(InvitationCode)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(InvitationCode.is_active == is_active)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    invitation_codes = query.order_by(InvitationCode.created_at.desc()).offset(offset).limit(size).all()
    
    return invitation_codes, total


def update_invitation_code(
    db: Session, 
    code_id: int, 
    invitation_code_update: InvitationCodeUpdate
) -> Optional[InvitationCode]:
    """
    Update an existing invitation code.
    
    Args:
        db: Database session
        code_id: Invitation code ID
        invitation_code_update: Update data
        
    Returns:
        Updated InvitationCode if found, None otherwise
    """
    db_invitation_code = get_invitation_code_by_id(db, code_id)
    if not db_invitation_code:
        return None
    
    # Update only provided fields
    update_data = invitation_code_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_invitation_code, field, value)
    
    db.commit()
    db.refresh(db_invitation_code)
    return db_invitation_code


def soft_delete_invitation_code(db: Session, code_id: int) -> Optional[InvitationCode]:
    """
    Soft delete (deactivate) an invitation code.
    
    Args:
        db: Database session
        code_id: Invitation code ID
        
    Returns:
        Updated InvitationCode if found, None otherwise
    """
    db_invitation_code = get_invitation_code_by_id(db, code_id)
    if not db_invitation_code:
        return None
    
    db_invitation_code.is_active = False
    db.commit()
    db.refresh(db_invitation_code)
    return db_invitation_code

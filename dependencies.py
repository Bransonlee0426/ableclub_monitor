"""
Dependencies for FastAPI dependency injection system.

This module contains dependency functions that can be injected into API endpoints
to provide authentication, authorization, and other cross-cutting concerns.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from core.security import verify_and_decode_token
from crud import user as crud_user
from models.user import User
from database.session import get_db


# HTTPBearer scheme for extracting Bearer tokens from Authorization header
# This will automatically look for "Authorization: Bearer <token>" in requests
security = HTTPBearer()


async def get_current_active_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency function to get the current authenticated and active user.
    
    This function:
    1. Extracts the JWT token from the Authorization header
    2. Verifies and decodes the token to get user_id
    3. Retrieves the user from the database
    4. Validates that the user exists and is active
    
    Args:
        credentials: HTTP Authorization credentials containing the Bearer token
        db: Database session
        
    Returns:
        User: The authenticated and active user object
        
    Raises:
        HTTPException: 
            - 401 if token is invalid/expired (handled by verify_and_decode_token)
            - 401 if user not found
            - 400 if user account is deactivated
    """
    # Extract token from credentials and verify
    token = credentials.credentials
    username = verify_and_decode_token(token)
    
    # Get user from database
    user = crud_user.get_user_by_username(db, username=username)
    
    # Check if user exists
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="找不到使用者"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="使用者帳號已被停用"
        )
    
    return user
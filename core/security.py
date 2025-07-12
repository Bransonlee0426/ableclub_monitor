# This file will contain security-related functions like password hashing and JWT creation.
from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status

from core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hashes a password using bcrypt.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    Creates a new JWT access token.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_and_decode_token(token: str) -> int:
    """
    Verifies and decodes a JWT token, returning the user_id.
    
    Args:
        token: The JWT token string to verify and decode
        
    Returns:
        int: The user_id extracted from the token's 'sub' field
        
    Raises:
        HTTPException: If the token is invalid, expired, or missing required fields
    """
    try:
        # Decode and verify the token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Extract the 'sub' field (user identifier)
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="憑證無效或已過期"
            )
        
        # Convert to integer and return
        try:
            user_id = int(user_id_str)
            return user_id
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="憑證無效或已過期"
            )
            
    except JWTError:
        # This catches all JWT-related errors: expired, invalid signature, etc.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="憑證無效或已過期"
        )

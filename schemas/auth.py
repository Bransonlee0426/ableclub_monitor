from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any

class LoginOrRegisterRequest(BaseModel):
    """
    Pydantic model for the login or register request body.
    It includes validation rules for the input fields.
    """
    # Use EmailStr to automatically validate the email format.
    username: EmailStr = Field(..., description="User's email address.")
    
    # Password must not be empty.
    password: str = Field(..., min_length=1, description="User's password.")
    
    # inviteCode is optional for login, but might be required for registration.
    inviteCode: Optional[str] = Field(None, description="Invitation code for new user registration.")

class Token(BaseModel):
    """
    Pydantic model for the JWT token response.
    """
    access_token: str
    token_type: str = "bearer"

class ResponseModel(BaseModel):
    """
    A generic response model to standardize API responses.
    Enhanced to support detailed error information in development environment.
    """
    success: bool
    message: str
    token: Optional[Token] = None
    errors: Optional[List[Dict[str, Any]]] = None  # Detailed error info for debugging
    error_code: Optional[str] = None  # Error code for frontend handling

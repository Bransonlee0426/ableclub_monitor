"""
Unified response models for all API endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Generic, TypeVar, Union

# Generic type for data payload
T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    """
    Base response model for all API endpoints
    """
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="回應訊息")
    data: Optional[T] = Field(None, description="回應資料")
    error_code: Optional[str] = Field(None, description="錯誤代碼")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="詳細錯誤資訊（僅開發環境）")
    timestamp: Optional[str] = Field(None, description="回應時間戳")

class SuccessResponse(BaseResponse[T]):
    """
    Success response model
    """
    success: bool = Field(True, description="操作成功")
    message: str = Field("操作成功", description="成功訊息")
    
    def __init__(self, data: T = None, message: str = "操作成功", **kwargs):
        super().__init__(success=True, message=message, data=data, **kwargs)

class ErrorResponse(BaseResponse[None]):
    """
    Error response model
    """
    success: bool = Field(False, description="操作失敗")
    data: None = Field(None, description="錯誤回應無資料")
    
    def __init__(self, message: str, error_code: str = None, errors: List[Dict[str, Any]] = None, **kwargs):
        super().__init__(success=False, message=message, data=None, error_code=error_code, errors=errors, **kwargs)

# Common response types
class EmptyResponse(BaseResponse[None]):
    """
    Empty response for operations that don't return data
    """
    pass

class ListResponse(BaseModel, Generic[T]):
    """
    Response model for list/pagination endpoints
    """
    success: bool = Field(True, description="操作是否成功")
    message: str = Field("查詢成功", description="回應訊息")
    data: Dict[str, Any] = Field(..., description="列表資料")
    
    def __init__(self, items: List[T], total: int, page: int = 1, size: int = 20, **kwargs):
        import math
        pages = math.ceil(total / size) if total > 0 else 1
        data = {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        }
        super().__init__(success=True, message="查詢成功", data=data, **kwargs)

# Specific response models for different data types
class TokenResponse(BaseModel):
    """
    Token data model
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None

class AuthResponse(BaseResponse[TokenResponse]):
    """
    Authentication response model
    """
    pass

# Error code constants
class ErrorCodes:
    """
    Standard error codes for the application
    """
    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    REQUIRED_FIELD_MISSING = "REQUIRED_FIELD_MISSING"
    INVALID_FORMAT = "INVALID_FORMAT"
    
    # Authentication errors
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    ACCOUNT_DISABLED = "ACCOUNT_DISABLED"
    
    # Authorization errors
    PERMISSION_DENIED = "PERMISSION_DENIED"
    INSUFFICIENT_PRIVILEGES = "INSUFFICIENT_PRIVILEGES"
    
    # Resource errors
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    
    # Business logic errors
    INVALID_INVITATION_CODE = "INVALID_INVITATION_CODE"
    REGISTRATION_REQUIRED = "REGISTRATION_REQUIRED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    
    # System errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    EMAIL_SEND_FAILED = "EMAIL_SEND_FAILED"
    
    # Development errors
    DEV_ENVIRONMENT_ONLY = "DEV_ENVIRONMENT_ONLY"
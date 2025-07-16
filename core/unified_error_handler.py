"""
Unified error handling middleware for consistent API responses
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from typing import Union, Dict, Any, List
import logging
from datetime import datetime
import traceback

from core.config import settings
from schemas.response import ErrorResponse, ErrorCodes
from core.error_handler import ErrorMessageMapper

logger = logging.getLogger(__name__)

class UnifiedErrorHandler:
    """
    Unified error handler that converts all exceptions to consistent ResponseModel format
    """
    
    @staticmethod
    def create_error_response(
        message: str,
        error_code: str = None,
        status_code: int = 400,
        errors: List[Dict[str, Any]] = None,
        include_timestamp: bool = True
    ) -> JSONResponse:
        """
        Create a standardized error response
        
        Args:
            message: Error message for the user
            error_code: Error code for programmatic handling
            status_code: HTTP status code
            errors: Detailed error information (for debugging)
            include_timestamp: Whether to include timestamp
            
        Returns:
            JSONResponse with standardized error format
        """
        response_data = ErrorResponse(
            message=message,
            error_code=error_code,
            errors=errors if settings.LOG_LEVEL == "DEBUG" else None
        )
        
        if include_timestamp:
            response_data.timestamp = datetime.utcnow().isoformat()
        
        return JSONResponse(
            status_code=status_code,
            content=response_data.model_dump(exclude_none=True)
        )
    
    @staticmethod
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """
        Handle HTTPException and convert to unified format
        """
        logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
        
        # Map HTTP status codes to error codes
        error_code_map = {
            400: ErrorCodes.VALIDATION_ERROR,
            401: ErrorCodes.AUTHENTICATION_FAILED,
            403: ErrorCodes.PERMISSION_DENIED,
            404: ErrorCodes.RESOURCE_NOT_FOUND,
            409: ErrorCodes.RESOURCE_CONFLICT,
            422: ErrorCodes.VALIDATION_ERROR,
            500: ErrorCodes.INTERNAL_SERVER_ERROR,
        }
        
        error_code = error_code_map.get(exc.status_code, ErrorCodes.INTERNAL_SERVER_ERROR)
        
        # Handle specific business logic error codes
        detail = str(exc.detail)
        if "邀請碼無效" in detail:
            error_code = ErrorCodes.INVALID_INVITATION_CODE
        elif "密碼錯誤" in detail:
            error_code = ErrorCodes.INVALID_CREDENTIALS
        elif "憑證無效" in detail or "已過期" in detail:
            error_code = ErrorCodes.TOKEN_INVALID
        elif "帳號已被停用" in detail:
            error_code = ErrorCodes.ACCOUNT_DISABLED
        elif "不存在" in detail:
            error_code = ErrorCodes.RESOURCE_NOT_FOUND
        elif "已存在" in detail:
            error_code = ErrorCodes.RESOURCE_ALREADY_EXISTS
        elif "開發環境" in detail:
            error_code = ErrorCodes.DEV_ENVIRONMENT_ONLY
        
        return UnifiedErrorHandler.create_error_response(
            message=detail,
            error_code=error_code,
            status_code=exc.status_code
        )
    
    @staticmethod
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """
        Handle validation errors and convert to unified format
        """
        logger.warning(f"Validation Error: {exc.errors()}")
        
        # Use existing error mapper for consistent messages
        primary_message = ErrorMessageMapper.get_primary_error_message(exc.errors())
        
        # Prepare debug information if needed
        debug_errors = None
        if settings.LOG_LEVEL == "DEBUG":
            debug_errors = [
                {
                    "field": error.get('loc', [])[-1] if error.get('loc') else 'unknown',
                    "type": error.get('type', 'unknown'),
                    "message": error.get('msg', ''),
                    "input": error.get('input', ''),
                    "location": error.get('loc', [])
                }
                for error in exc.errors()
            ]
        
        return UnifiedErrorHandler.create_error_response(
            message=primary_message,
            error_code=ErrorCodes.VALIDATION_ERROR,
            status_code=400,
            errors=debug_errors
        )
    
    @staticmethod
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Handle unexpected exceptions
        """
        logger.error(f"Unexpected error: {str(exc)}")
        logger.error(traceback.format_exc())
        
        # Don't expose internal error details in production
        message = "內部伺服器錯誤" if settings.LOG_LEVEL != "DEBUG" else str(exc)
        
        debug_errors = None
        if settings.LOG_LEVEL == "DEBUG":
            debug_errors = [
                {
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "traceback": traceback.format_exc()
                }
            ]
        
        return UnifiedErrorHandler.create_error_response(
            message=message,
            error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
            status_code=500,
            errors=debug_errors
        )
    
    @staticmethod
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """
        Handle SQLAlchemy database errors
        """
        logger.error(f"Database error: {str(exc)}")
        
        message = "資料庫操作失敗" if settings.LOG_LEVEL != "DEBUG" else str(exc)
        
        return UnifiedErrorHandler.create_error_response(
            message=message,
            error_code=ErrorCodes.DATABASE_ERROR,
            status_code=500
        )


# Custom exception classes for business logic
class BusinessLogicException(Exception):
    """
    Custom exception for business logic errors
    """
    def __init__(self, message: str, error_code: str = None, status_code: int = 400):
        self.message = message
        self.error_code = error_code or ErrorCodes.VALIDATION_ERROR
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationException(BusinessLogicException):
    """
    Custom exception for authentication errors
    """
    def __init__(self, message: str = "認證失敗"):
        super().__init__(message, ErrorCodes.AUTHENTICATION_FAILED, 401)


class PermissionException(BusinessLogicException):
    """
    Custom exception for permission errors
    """
    def __init__(self, message: str = "權限不足"):
        super().__init__(message, ErrorCodes.PERMISSION_DENIED, 403)


class ResourceNotFoundException(BusinessLogicException):
    """
    Custom exception for resource not found errors
    """
    def __init__(self, message: str = "資源不存在"):
        super().__init__(message, ErrorCodes.RESOURCE_NOT_FOUND, 404)


class ResourceConflictException(BusinessLogicException):
    """
    Custom exception for resource conflict errors
    """
    def __init__(self, message: str = "資源衝突"):
        super().__init__(message, ErrorCodes.RESOURCE_CONFLICT, 409)


class ExternalServiceException(BusinessLogicException):
    """
    Custom exception for external service errors
    """
    def __init__(self, message: str = "外部服務錯誤"):
        super().__init__(message, ErrorCodes.EXTERNAL_SERVICE_ERROR, 500)
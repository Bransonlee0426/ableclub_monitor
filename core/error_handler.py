"""
Enhanced error handling module for better validation error messages
"""

from typing import Dict, Tuple, List, Optional, Any
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
from schemas.auth import ResponseModel
from core.config import settings


class ErrorMessageMapper:
    """
    Maps validation errors to user-friendly messages
    """
    
    # Error type mappings for different fields and error types
    ERROR_MESSAGES = {
        # Username field errors - keeping backward compatibility with tests
        ('username', 'missing'): "帳號錯誤、請重新確認。",
        ('username', 'value_error.email'): "帳號錯誤、請重新確認。",
        ('username', 'value_error.any_str.min_length'): "帳號錯誤、請重新確認。",
        ('username', 'value_error.str.regex'): "帳號錯誤、請重新確認。",
        ('username', 'type_error.str'): "帳號錯誤、請重新確認。",
        
        # Password field errors - keeping backward compatibility with tests
        ('password', 'missing'): "密碼錯誤、請重新確認。",
        ('password', 'value_error.any_str.min_length'): "密碼錯誤、請重新確認。",
        ('password', 'type_error.str'): "密碼錯誤、請重新確認。",
        
        # Invite code field errors
        ('inviteCode', 'missing'): "請輸入邀請碼",
        ('inviteCode', 'value_error.any_str.min_length'): "邀請碼不能為空",
        ('inviteCode', 'type_error.str'): "邀請碼必須是文字格式",
        
        # Query parameter errors
        ('username', 'query_missing'): "帳號錯誤、請重新確認。",
        ('username', 'query_invalid'): "帳號錯誤、請重新確認。",
    }
    
    # Field-specific fallback messages
    FIELD_FALLBACKS = {
        'username': "帳號錯誤、請重新確認。",
        'password': "密碼錯誤、請重新確認。",
        'inviteCode': "邀請碼錯誤、請重新確認。",
    }
    
    # Generic fallback
    GENERIC_FALLBACK = "參數驗證失敗"
    
    @classmethod
    def get_error_message(cls, field: str, error_type: str, error_details: Dict[str, Any] = None) -> str:
        """
        Get user-friendly error message based on field and error type
        
        Args:
            field: The field name that failed validation
            error_type: The type of validation error
            error_details: Additional error details from Pydantic
            
        Returns:
            User-friendly error message
        """
        # Try exact match first
        key = (field, error_type)
        if key in cls.ERROR_MESSAGES:
            return cls.ERROR_MESSAGES[key]
        
        # Try field-specific fallback
        if field in cls.FIELD_FALLBACKS:
            return cls.FIELD_FALLBACKS[field]
        
        # Generic fallback
        return cls.GENERIC_FALLBACK
    
    @classmethod
    def get_primary_error_message(cls, errors: List[Dict[str, Any]]) -> str:
        """
        Get the primary error message from a list of validation errors
        
        Args:
            errors: List of validation errors from Pydantic
            
        Returns:
            Primary error message to show to user
        """
        if not errors:
            return cls.GENERIC_FALLBACK
        
        # Check for specific scenarios first
        custom_message = handle_specific_validation_scenarios(errors)
        if custom_message:
            return custom_message
        
        # Get the first error (most relevant)
        first_error = errors[0]
        field = first_error.get('loc', [])[-1] if first_error.get('loc') else 'unknown'
        error_type = first_error.get('type', 'unknown')
        
        return cls.get_error_message(field, error_type, first_error)


def create_validation_error_response(
    exc: RequestValidationError,
    include_debug_info: bool = None
) -> ResponseModel:
    """
    Create a standardized validation error response
    
    Args:
        exc: The RequestValidationError exception
        include_debug_info: Whether to include debug information (defaults to DEBUG mode)
        
    Returns:
        ResponseModel with appropriate error information
    """
    if include_debug_info is None:
        include_debug_info = settings.LOG_LEVEL == "DEBUG"
    
    # Get primary error message
    primary_message = ErrorMessageMapper.get_primary_error_message(exc.errors())
    
    # Prepare debug information if needed
    debug_errors = None
    if include_debug_info:
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
    
    return ResponseModel(
        success=False,
        message=primary_message,
        errors=debug_errors,
        error_code="VALIDATION_ERROR"
    )


def handle_specific_validation_scenarios(errors: List[Dict[str, Any]]) -> Optional[str]:
    """
    Handle specific validation scenarios that need custom logic
    
    Args:
        errors: List of validation errors
        
    Returns:
        Custom error message if specific scenario is detected, None otherwise
    """
    # Check for missing required fields in login/register
    missing_fields = []
    for error in errors:
        if error.get('type') == 'missing':
            field = error.get('loc', [])[-1] if error.get('loc') else None
            if field in ['username', 'password']:
                missing_fields.append(field)
    
    # Custom messages for specific combinations
    if 'username' in missing_fields and 'password' in missing_fields:
        return "請輸入帳號和密碼"
    
    return None
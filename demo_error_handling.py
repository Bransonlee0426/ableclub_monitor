#!/usr/bin/env python3
"""
Demo script to show the enhanced error handling capabilities
"""

from fastapi.exceptions import RequestValidationError
from core.error_handler import create_validation_error_response, ErrorMessageMapper
from core.config import settings

def demo_error_mapping():
    """
    Demo the error message mapping functionality
    """
    print("=== 錯誤訊息映射示範 ===\n")
    
    # Test different error scenarios
    test_cases = [
        ("username", "missing", "缺少用戶名"),
        ("username", "value_error.email", "無效的 email 格式"),
        ("password", "missing", "缺少密碼"),
        ("password", "value_error.any_str.min_length", "空密碼"),
        ("inviteCode", "missing", "缺少邀請碼"),
        ("unknown_field", "unknown_error", "未知錯誤"),
    ]
    
    for field, error_type, description in test_cases:
        message = ErrorMessageMapper.get_error_message(field, error_type)
        print(f"{description}:")
        print(f"  欄位: {field}")
        print(f"  錯誤類型: {error_type}")
        print(f"  訊息: {message}")
        print()

def demo_response_structure():
    """
    Demo the response structure in different modes
    """
    print("=== 回應結構示範 ===\n")
    
    # Mock validation error
    class MockValidationError:
        def errors(self):
            return [
                {
                    'loc': ['body', 'username'],
                    'type': 'missing',
                    'msg': 'field required',
                    'input': {'password': 'test123'}
                },
                {
                    'loc': ['body', 'password'],
                    'type': 'value_error.any_str.min_length',
                    'msg': 'ensure this value has at least 1 characters',
                    'input': ''
                }
            ]
    
    mock_exc = MockValidationError()
    
    # Test in production mode (no debug info)
    print("1. 產線模式 (LOG_LEVEL != DEBUG):")
    original_log_level = settings.LOG_LEVEL
    settings.LOG_LEVEL = "INFO"
    
    response = create_validation_error_response(mock_exc)
    print(f"  回應: {response.model_dump_json(indent=2, ensure_ascii=False)}")
    
    # Test in debug mode (with debug info)
    print("\n2. 開發模式 (LOG_LEVEL = DEBUG):")
    settings.LOG_LEVEL = "DEBUG"
    
    response = create_validation_error_response(mock_exc)
    print(f"  回應: {response.model_dump_json(indent=2, ensure_ascii=False)}")
    
    # Restore original setting
    settings.LOG_LEVEL = original_log_level

if __name__ == "__main__":
    demo_error_mapping()
    demo_response_structure()
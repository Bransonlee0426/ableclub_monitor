#!/usr/bin/env python3
"""
Test script to verify the enhanced error handling mechanism
"""

import asyncio
import json
from httpx import AsyncClient
from app.main import app

async def test_error_handling():
    """
    Test various error scenarios to verify the enhanced error handling
    """
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        
        print("=== 測試增強的錯誤處理機制 ===\n")
        
        # Test cases for different validation errors
        test_cases = [
            {
                "name": "缺少 username",
                "endpoint": "/api/v1/auth/login-or-register",
                "method": "POST",
                "payload": {"password": "password123"},
                "expected_message": "帳號錯誤、請重新確認。"
            },
            {
                "name": "缺少 password",
                "endpoint": "/api/v1/auth/login-or-register",
                "method": "POST",
                "payload": {"username": "user@test.com"},
                "expected_message": "密碼錯誤、請重新確認。"
            },
            {
                "name": "空的 username",
                "endpoint": "/api/v1/auth/login-or-register",
                "method": "POST",
                "payload": {"username": "", "password": "password123"},
                "expected_message": "帳號錯誤、請重新確認。"
            },
            {
                "name": "空的 password",
                "endpoint": "/api/v1/auth/login-or-register",
                "method": "POST",
                "payload": {"username": "user@test.com", "password": ""},
                "expected_message": "密碼錯誤、請重新確認。"
            },
            {
                "name": "無效的 email 格式",
                "endpoint": "/api/v1/auth/login-or-register",
                "method": "POST",
                "payload": {"username": "not-an-email", "password": "password123"},
                "expected_message": "帳號錯誤、請重新確認。"
            },
            {
                "name": "check-status 沒有 username 參數",
                "endpoint": "/api/v1/users/check-status",
                "method": "GET",
                "payload": None,
                "expected_message": "帳號錯誤、請重新確認。"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"{i}. 測試: {test_case['name']}")
            
            try:
                if test_case['method'] == 'POST':
                    response = await client.post(test_case['endpoint'], json=test_case['payload'])
                else:
                    response = await client.get(test_case['endpoint'])
                
                print(f"   狀態碼: {response.status_code}")
                
                if response.status_code == 400:
                    data = response.json()
                    print(f"   回應內容: {json.dumps(data, ensure_ascii=False, indent=6)}")
                    
                    # Check message
                    if data.get('message') == test_case['expected_message']:
                        print(f"   ✅ 訊息正確: {data.get('message')}")
                    else:
                        print(f"   ❌ 訊息錯誤")
                        print(f"      期望: {test_case['expected_message']}")
                        print(f"      實際: {data.get('message')}")
                    
                    # Check structure
                    if 'success' in data and 'message' in data:
                        print(f"   ✅ 回應結構正確")
                    else:
                        print(f"   ❌ 回應結構錯誤")
                    
                    # Check if debug info is included (should be in DEBUG mode)
                    if 'errors' in data and data['errors']:
                        print(f"   ℹ️  包含除錯資訊: {len(data['errors'])} 個錯誤")
                    
                else:
                    print(f"   ❌ 期望狀態碼 400，實際 {response.status_code}")
                    print(f"   回應: {response.text}")
                
            except Exception as e:
                print(f"   ❌ 測試失敗: {str(e)}")
            
            print()
        
        print("=== 測試完成 ===")

if __name__ == "__main__":
    asyncio.run(test_error_handling())
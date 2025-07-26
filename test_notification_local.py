#!/usr/bin/env python3
"""
本地測試通知功能腳本
Local testing script for notification functionality
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_notification_function():
    """Test the notification function locally"""
    try:
        print("🔍 開始測試通知功能...")
        
        # Import the notification function
        from app.jobs.notification_job import process_and_notify_users
        
        print("✅ 通知函數導入成功")
        
        # Execute the notification function
        result = await process_and_notify_users()
        
        print(f"📧 通知處理完成，結果: {result}")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 啟動本地通知功能測試...")
    asyncio.run(test_notification_function())
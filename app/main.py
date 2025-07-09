from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from notifications.sender import test_email_notification, NotificationSender

# Create FastAPI app instance
app = FastAPI(
    title="AbleClub Monitor API",
    description="API for monitoring and sending notifications for AbleClub courses.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Create notification sender instance
notification_sender = NotificationSender()

# Email notification configuration
EMAIL_CONFIG = {
    "channel": "email",
    "email_user": "bransonlee0426@gmail.com",
    "email_password": "ebvnpqhnwlkykrrh"
}

# Pydantic model for notification request
class EmailNotificationRequest(BaseModel):
    """Email 通知請求模型"""
    message: str = Field(..., description="要發送的 Email 訊息")
    to_email: Optional[str] = Field(default=None, description="自訂收件者 Email (可選，預設使用系統設定)")
    subject: Optional[str] = Field(default=None, description="Email 主旨 (可選，預設為 'AbleClub Monitor 通知')")

@app.get("/", 
         tags=["Root"], 
         summary="API 健康檢查",
         description="檢查 API 服務狀態")
def read_root():
    """
    Root endpoint to check API status.
    """
    return {"status": "ok", "message": "Welcome to the AbleClub Monitor API!"}

# Swagger URL: http://127.0.0.1:8000/docs#/Notifications/send_email_api_notifications_sendEmail_post
@app.post("/api/notifications/sendEmail", 
          tags=["Notifications"],
          summary="發送 Email 通知",
          description="發送 Email 通知到指定收件者",
          response_description="Email 發送結果")
def send_email_notification(request: EmailNotificationRequest):
    """
    **發送 Email 通知**
    
    使用系統配置的 Email 設定發送通知到指定收件者。
    
    **Swagger 測試 URL**: http://127.0.0.1:8000/docs#/Notifications/send_email_api_notifications_sendEmail_post
    
    **範例請求**:
    ```json
    {
      "message": "🎯 AbleClub 新課程通知\\n\\n課程：Python 進階班\\n時間：2024-01-20 19:00",
      "subject": "🚨 課程通知"
    }
    ```
    """
    try:
        # 使用配置發送 Email
        result = notification_sender.send_notification(
            message=request.message,
            channel=EMAIL_CONFIG["channel"],
            email_user=EMAIL_CONFIG["email_user"],
            email_password=EMAIL_CONFIG["email_password"],
            to_email=request.to_email,
            subject=request.subject
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return {
            "status": "success",
            "message": "Email 通知發送成功",
            "response": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email notification: {str(e)}")

# Swagger URL: http://127.0.0.1:8000/docs#/Notifications/test_email_api_notifications_test_email_get
@app.get("/api/notifications/test-email", 
         tags=["Notifications"],
         summary="測試 Email 通知",
         description="發送一個測試 Email 通知")
def test_email():
    """
    **測試 Email 通知功能**
    
    發送一個預定義的測試 Email，用於驗證 Email 通知系統是否正常運作。
    
    **Swagger 測試 URL**: http://127.0.0.1:8000/docs#/Notifications/test_email_api_notifications_test_email_get
    """
    try:
        result = test_email_notification()
        
        return {
            "status": "success",
            "message": "Email 通知測試完成",
            "test_results": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test email notification: {str(e)}")

# Swagger URL: http://127.0.0.1:8000/docs#/Notifications/get_supported_channels_api_notifications_channels_get
@app.get("/api/notifications/channels", 
         tags=["Notifications"],
         summary="查看支援的通知管道",
         description="取得所有支援的通知管道列表及說明")
def get_supported_channels():
    """
    **取得支援的通知管道列表**
    
    回傳系統支援的所有通知管道，包含各管道的說明和設定需求。
    
    **Swagger 測試 URL**: http://127.0.0.1:8000/docs#/Notifications/get_supported_channels_api_notifications_channels_get
    """
    return {
        "supported_channels": ["email", "telegram"],
        "channel_descriptions": {
            "email": "Email 通知 (已配置)",
            "telegram": "Telegram Bot 通知 (未來功能)"
        },
        "system_info": {
            "version": "1.0.0",
            "focus": "專注於 Email 和 Telegram 兩個實用的通知管道"
        }
    }

# Other endpoints for events, etc., will be added here.

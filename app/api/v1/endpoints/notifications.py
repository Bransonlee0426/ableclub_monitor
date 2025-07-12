from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from schemas.notification import (
    SendNotificationRequest, 
    NotificationResponse, 
    TestEmailResponse,
    NotificationChannel
)
from notifications.sender import NotificationSender, test_email_notification

router = APIRouter()


@router.post(
    "/send",
    response_model=NotificationResponse,
    summary="發送通知",
    description="發送通知到指定的管道 (Email 或 Telegram)。支援實際發送和模擬模式。",
    responses={
        200: {
            "description": "通知發送成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Email 通知發送成功 (模擬模式)",
                        "mode": "debug",
                        "channel": "email",
                        "details": {
                            "from": "sender@example.com",
                            "to": "receiver@example.com",
                            "subject": "AbleClub Monitor 通知"
                        }
                    }
                }
            }
        },
        400: {
            "description": "請求參數錯誤",
            "content": {
                "application/json": {
                    "example": {"detail": "不支援的通知管道"}
                }
            }
        },
        500: {
            "description": "通知發送失敗",
            "content": {
                "application/json": {
                    "example": {"detail": "Email 發送失敗: SMTP 連線錯誤"}
                }
            }
        }
    }
)
async def send_notification(request: SendNotificationRequest):
    """
    Send notification to specified channel.
    
    This endpoint allows sending notifications via email or telegram.
    It supports both production and debug modes based on configuration.
    """
    sender = NotificationSender()
    
    # Prepare kwargs for the notification sender
    kwargs = {}
    if request.channel == NotificationChannel.email:
        kwargs["subject"] = request.subject
        if request.to_email:
            kwargs["to_email"] = request.to_email
    
    # Send the notification
    result = sender.send_notification(
        message=request.message,
        channel=request.channel.value,
        **kwargs
    )
    
    # Handle errors
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    # Extract response data
    success = "error" not in result
    message = result.get("message", "通知發送成功")
    mode = result.get("mode")
    
    # Prepare details (exclude sensitive information)
    details = {k: v for k, v in result.items() if k not in ["message", "mode"]}
    
    return NotificationResponse(
        success=success,
        message=message,
        mode=mode,
        channel=request.channel.value,
        details=details if details else None
    )


@router.get(
    "/test-email",
    response_model=TestEmailResponse,
    summary="測試 Email 通知",
    description="發送測試 Email 通知，用於驗證 Email 通知功能是否正常運作。",
    responses={
        200: {
            "description": "測試通知發送成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Email 測試通知發送成功",
                        "mode": "debug",
                        "details": {
                            "from": "sender@example.com",
                            "to": "receiver@example.com",
                            "subject": "AbleClub Monitor - 測試通知"
                        }
                    }
                }
            }
        },
        500: {
            "description": "測試通知發送失敗",
            "content": {
                "application/json": {
                    "example": {"detail": "Email 發送失敗: SMTP 連線錯誤"}
                }
            }
        }
    }
)
async def test_email():
    """
    Send a test email notification.
    
    This endpoint sends a predefined test message to verify that
    the email notification system is working correctly.
    """
    try:
        result = test_email_notification()
        
        # Handle the case where result might have an error
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        # Extract response data
        success = "error" not in result
        message = result.get("message", "Email 測試通知發送成功")
        mode = result.get("mode")
        
        # Prepare details (exclude sensitive information)
        details = {k: v for k, v in result.items() if k not in ["message", "mode"]}
        
        return TestEmailResponse(
            success=success,
            message=message,
            mode=mode,
            details=details if details else None
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"測試通知發送失敗: {str(e)}"
        )


@router.get(
    "/channels",
    summary="取得支援的通知管道",
    description="取得目前系統支援的所有通知管道列表。",
    responses={
        200: {
            "description": "支援的通知管道列表",
            "content": {
                "application/json": {
                    "example": {
                        "channels": ["email", "telegram"],
                        "default": "email"
                    }
                }
            }
        }
    }
)
async def get_supported_channels():
    """
    Get list of supported notification channels.
    
    Returns all notification channels that are currently supported
    by the notification system.
    """
    sender = NotificationSender()
    return {
        "channels": sender.supported_channels,
        "default": "email"
    }
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from enum import Enum


class NotificationChannel(str, Enum):
    """支援的通知管道列舉"""
    email = "email"
    telegram = "telegram"


class SendNotificationRequest(BaseModel):
    """發送通知請求的資料模型"""
    message: str = Field(..., description="要發送的通知訊息", min_length=1, max_length=5000)
    channel: NotificationChannel = Field(default=NotificationChannel.email, description="通知管道")
    subject: Optional[str] = Field(default="AbleClub Monitor 通知", description="Email 主旨 (僅適用於 email 管道)")
    to_email: Optional[str] = Field(default=None, description="接收者 Email (可選，使用預設設定)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "測試通知訊息",
                "channel": "email",
                "subject": "AbleClub Monitor - 測試通知",
                "to_email": "user@example.com"
            }
        }
    )


class NotificationResponse(BaseModel):
    """通知發送回應的資料模型"""
    success: bool = Field(..., description="發送是否成功")
    message: str = Field(..., description="回應訊息")
    mode: Optional[str] = Field(default=None, description="發送模式 (debug/production)")
    channel: str = Field(..., description="使用的通知管道")
    details: Optional[Dict[str, Any]] = Field(default=None, description="詳細資訊")

    model_config = ConfigDict(
        json_schema_extra={
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
    )


class TestEmailResponse(BaseModel):
    """測試 Email 通知回應的資料模型"""
    success: bool = Field(..., description="測試是否成功")
    message: str = Field(..., description="測試結果訊息")
    mode: Optional[str] = Field(default=None, description="發送模式")
    details: Optional[Dict[str, Any]] = Field(default=None, description="發送詳細資訊")

    model_config = ConfigDict(
        json_schema_extra={
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
    )
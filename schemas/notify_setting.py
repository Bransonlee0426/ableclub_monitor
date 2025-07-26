from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
import re


class NotifySettingBase(BaseModel):
    """通知設定的基礎資料模型"""
    notify_type: str = Field(..., description="通知類型")
    email_address: Optional[str] = Field(default=None, description="Email 地址")
    keywords: List[str] = Field(default=[], description="關鍵字列表")


class NotifySettingCreate(NotifySettingBase):
    """通知設定建立請求的資料模型"""

    @field_validator('notify_type')
    @classmethod
    def validate_notify_type(cls, v):
        """驗證 notify_type 不可為空字串"""
        if v == "":
            raise ValueError("請確實填寫通知類型")
        return v

    @model_validator(mode='after')
    def validate_email_when_email_type(self):
        """條件式驗證：當 notify_type 為 'email' 時，email_address 必須存在且格式正確"""
        if self.notify_type == "email":
            if not self.email_address or self.email_address.strip() == "":
                raise ValueError("Email 通知類型必須提供有效的 Email 地址")
            
            # 驗證 Email 格式
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, self.email_address):
                raise ValueError("Email 地址格式不正確")
        
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "notify_type": "email",
                "email_address": "user@example.com",
                "keywords": ["Python", "FastAPI"]
            }
        }
    )


class NotifySettingUpdate(BaseModel):
    """通知設定更新請求的資料模型"""
    notify_type: Optional[str] = Field(default=None, description="通知類型")
    email_address: Optional[str] = Field(default=None, description="Email 地址")
    is_active: Optional[bool] = Field(default=None, description="是否啟用")
    keywords: Optional[List[str]] = Field(default=None, description="關鍵字列表")

    @field_validator('notify_type')
    @classmethod
    def validate_notify_type(cls, v):
        """驗證 notify_type 不可為空字串"""
        if v is not None and v == "":
            raise ValueError("請確實填寫通知類型")
        return v

    @field_validator('email_address')
    @classmethod
    def validate_email_address(cls, v):
        """驗證 email_address 不可為空字串"""
        if v is not None and v == "":
            raise ValueError("Email 地址不可為空字串")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "notify_type": "telegram",
                "email_address": "newemail@example.com",
                "is_active": True,
                "keywords": ["Python", "FastAPI", "React"]
            }
        }
    )


class NotifySettingResponse(BaseModel):
    """通知設定回應的資料模型"""
    id: int = Field(..., description="通知設定 ID")
    user_id: int = Field(..., description="使用者 ID")
    notify_type: str = Field(..., description="通知類型")
    email_address: Optional[str] = Field(default=None, description="Email 地址")
    is_active: bool = Field(..., description="是否啟用")
    created_at: datetime = Field(..., description="建立時間")
    updated_at: datetime = Field(..., description="更新時間")
    keywords: List[str] = Field(default=[], description="使用者設定的關鍵字列表")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 1,
                "notify_type": "email",
                "email_address": "user@example.com",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "keywords": ["Python", "FastAPI"]
            }
        }
    )


class NotifySettingListResponse(BaseModel):
    """通知設定列表回應的資料模型"""
    items: List[NotifySettingResponse] = Field(..., description="通知設定列表")
    total: int = Field(..., description="總筆數")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": 1,
                        "user_id": 1,
                        "notify_type": "email",
                        "email_address": "user@example.com",
                        "is_active": True,
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00",
                        "keywords": ["Python", "FastAPI"]
                    }
                ],
                "total": 1
            }
        }
    )
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime


class InvitationCodeCreate(BaseModel):
    """邀請碼建立請求的資料模型"""
    code: str = Field(..., description="邀請碼", min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, description="邀請碼描述")
    expires_at: Optional[datetime] = Field(default=None, description="到期時間")

    @field_validator('expires_at', mode='before')
    @classmethod
    def validate_expires_at(cls, v):
        """Convert empty string to None for expires_at field"""
        if v == "" or v is None:
            return None
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "WELCOME2024",
                "description": "2024年歡迎新用戶邀請碼",
                "expires_at": "2024-12-31T23:59:59"
            }
        }
    )


class InvitationCodeUpdate(BaseModel):
    """邀請碼更新請求的資料模型"""
    description: Optional[str] = Field(default=None, description="邀請碼描述")
    is_active: Optional[bool] = Field(default=None, description="是否啟用")
    expires_at: Optional[datetime] = Field(default=None, description="到期時間")

    @field_validator('expires_at', mode='before')
    @classmethod
    def validate_expires_at(cls, v):
        """Convert empty string to None for expires_at field"""
        if v == "" or v is None:
            return None
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "description": "更新後的描述",
                "is_active": False,
                "expires_at": "2024-12-31T23:59:59"
            }
        }
    )


class InvitationCodeResponse(BaseModel):
    """邀請碼回應的資料模型"""
    id: int = Field(..., description="邀請碼 ID")
    code: str = Field(..., description="邀請碼")
    description: Optional[str] = Field(default=None, description="邀請碼描述")
    is_active: bool = Field(..., description="是否啟用")
    expires_at: Optional[datetime] = Field(default=None, description="到期時間")
    created_at: datetime = Field(..., description="建立時間")
    updated_at: datetime = Field(..., description="更新時間")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "code": "WELCOME2024",
                "description": "2024年歡迎新用戶邀請碼",
                "is_active": True,
                "expires_at": "2024-12-31T23:59:59",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
    )


class InvitationCodeListResponse(BaseModel):
    """邀請碼列表回應的資料模型"""
    items: List[InvitationCodeResponse] = Field(..., description="邀請碼列表")
    total: int = Field(..., description="總筆數")
    page: int = Field(..., description="當前頁數")
    size: int = Field(..., description="每頁筆數")
    pages: int = Field(..., description="總頁數")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": 1,
                        "code": "WELCOME2024",
                        "description": "2024年歡迎新用戶邀請碼",
                        "is_active": True,
                        "expires_at": "2024-12-31T23:59:59",
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00"
                    }
                ],
                "total": 1,
                "page": 1,
                "size": 20,
                "pages": 1
            }
        }
    )
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from core.datetime_utils import TaiwanDatetimeMixin, datetime_field


class UserUpdate(BaseModel):
    """使用者更新請求的資料模型"""
    is_active: bool = Field(..., description="是否啟用")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_active": False
            }
        }
    )


class UserPublic(BaseModel, TaiwanDatetimeMixin):
    """使用者公開資訊回應的資料模型 (不包含密碼)"""
    id: int = Field(..., description="使用者 ID")
    username: str = Field(..., description="使用者名稱 (Email)")
    invite_code_used: Optional[str] = Field(default=None, description="使用的邀請碼")
    is_active: bool = Field(..., description="是否啟用")
    created_at: datetime = datetime_field("建立時間")
    updated_at: datetime = datetime_field("更新時間")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "user@example.com",
                "invite_code_used": "WELCOME2024",
                "is_active": True,
                "created_at": "2024-01-01-00:00",
                "updated_at": "2024-01-01-00:00"
            }
        }
    )


class UserListResponse(BaseModel):
    """使用者列表回應的資料模型"""
    items: List[UserPublic] = Field(..., description="使用者列表")
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
                        "username": "user@example.com",
                        "invite_code_used": "WELCOME2024",
                        "is_active": True,
                        "created_at": "2024-01-01-00:00",
                        "updated_at": "2024-01-01-00:00"
                    }
                ],
                "total": 1,
                "page": 1,
                "size": 20,
                "pages": 1
            }
        }
    )
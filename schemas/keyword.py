from pydantic import BaseModel, Field, ConfigDict
from typing import List
from datetime import datetime
from core.datetime_utils import TaiwanDatetimeMixin, datetime_field


class KeywordResponse(BaseModel, TaiwanDatetimeMixin):
    """關鍵字回應的資料模型"""
    id: int = Field(..., description="關鍵字 ID")
    user_id: int = Field(..., description="使用者 ID")
    keyword: str = Field(..., description="關鍵字內容")
    created_at: datetime = datetime_field("建立時間")
    updated_at: datetime = datetime_field("更新時間")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 1,
                "keyword": "Python",
                "created_at": "2024-01-01-00:00",
                "updated_at": "2024-01-01-00:00"
            }
        }
    )


class KeywordListRequest(BaseModel):
    """關鍵字列表更新請求的資料模型 (for PUT operation)"""
    keywords: List[str] = Field(..., description="關鍵字列表")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "keywords": ["Python", "FastAPI", "React"]
            }
        }
    )


class KeywordListResponse(BaseModel):
    """關鍵字列表回應的資料模型"""
    keywords: List[str] = Field(..., description="關鍵字列表")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "keywords": ["Python", "FastAPI", "React"]
            }
        }
    ) 
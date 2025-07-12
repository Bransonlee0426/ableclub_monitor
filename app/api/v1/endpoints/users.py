
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from crud import user as crud_user
from database.session import get_db
from dependencies import get_current_active_user
from models.user import User
from schemas.user import UserPublic

router = APIRouter()

@router.get(
    "/check-status",
    summary="檢查使用者註冊狀態",
    description="根據使用者名稱 (Email) 查詢該使用者是否已註冊且帳號為啟用狀態。",
    responses={
        200: {
            "description": "查詢成功",
            "content": {
                "application/json": {
                    "examples": {
                        "registered": {"summary": "已註冊的使用者", "value": {"isRegistered": True}},
                        "unregistered": {"summary": "未註冊或未啟用的使用者", "value": {"isRegistered": False}}
                    }
                }
            }
        },
        400: {
            "description": "輸入的 Email 格式錯誤",
            "content": {
                "application/json": {
                    "example": {"success": False, "message": "帳號錯誤、請重新確認。"}
                }
            }
        }
    }
)
def check_user_status(
    username: str = Query(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
    db: Session = Depends(get_db)
):
    """
    Check if a user is registered and active based on the username (email).
    """
    user = crud_user.get_user_by_username(db, username=username)
    if user and user.is_active:
        return {"isRegistered": True}
    return {"isRegistered": False}


@router.get(
    "/me",
    response_model=UserPublic,
    summary="取得當前使用者資訊",
    description="取得當前已驗證使用者的個人資訊。需要提供有效的 JWT Token。",
    responses={
        200: {
            "description": "成功取得使用者資訊",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "user@example.com",
                        "invite_code_used": "WELCOME2024",
                        "is_active": True,
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00"
                    }
                }
            }
        },
        401: {
            "description": "未授權 - Token 無效或已過期",
            "content": {
                "application/json": {
                    "example": {"detail": "憑證無效或已過期"}
                }
            }
        },
        400: {
            "description": "使用者帳號已被停用",
            "content": {
                "application/json": {
                    "example": {"detail": "使用者帳號已被停用"}
                }
            }
        }
    }
)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> UserPublic:
    """
    Get the current authenticated user's information.
    
    This endpoint returns the personal information of the currently authenticated user.
    The user must provide a valid JWT token in the Authorization header.
    
    Args:
        current_user: The current authenticated user (injected by dependency)
        
    Returns:
        UserPublic: User information without sensitive data like password
    """
    return UserPublic.model_validate(current_user)

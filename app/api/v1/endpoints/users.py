
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from crud import user as crud_user
from database.session import get_db

router = APIRouter()

@router.get(
    "/check-status",
    tags=["Users"],
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

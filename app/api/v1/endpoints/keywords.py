from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from crud import keyword as crud_keyword
from dependencies import get_current_active_user
from models.user import User
from database.session import get_db
from schemas.response import SuccessResponse

router = APIRouter()


@router.get(
    "/",
    response_model=SuccessResponse[List[str]],
    status_code=status.HTTP_200_OK,
    summary="取得使用者關鍵字列表",
    description="取得當前使用者設定的所有關鍵字列表。",
    responses={
        200: {
            "description": "成功取得關鍵字列表",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "查詢成功",
                        "data": ["Python", "FastAPI", "React"],
                        "error_code": None,
                        "errors": None,
                        "timestamp": None
                    }
                }
            }
        },
        401: {
            "description": "未授權，需要有效的 JWT Token"
        }
    }
)
async def get_user_keywords(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> SuccessResponse[List[str]]:
    """
    Get the current user's keywords list.
    
    Returns a list of keyword strings for the authenticated user.
    If the user has no keywords, returns an empty list.
    """
    keywords = crud_keyword.get_by_user_id(db=db, user_id=current_user.id)
    keyword_list = [keyword.keyword for keyword in keywords]
    return SuccessResponse(data=keyword_list, message="查詢成功")


@router.put(
    "/",
    response_model=SuccessResponse[List[str]],
    status_code=status.HTTP_200_OK,
    summary="更新使用者關鍵字列表",
    description="完整替換當前使用者的關鍵字列表。這是一個冪等操作，會先刪除所有現有關鍵字，然後重新建立。",
    responses={
        200: {
            "description": "成功更新關鍵字列表",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "關鍵字更新成功",
                        "data": ["Python", "FastAPI"],
                        "error_code": None,
                        "errors": None,
                        "timestamp": None
                    }
                }
            }
        },
        401: {
            "description": "未授權，需要有效的 JWT Token"
        },
        422: {
            "description": "請求資料格式錯誤"
        }
    }
)
async def update_user_keywords(
    keywords: List[str],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> SuccessResponse[List[str]]:
    """
    Update the current user's keywords list using complete replacement.
    
    This endpoint uses the PUT method semantics - it completely replaces
    the user's existing keywords with the new list provided.
    
    Args:
        keywords: List of keyword strings to set for the user
        current_user: The authenticated user (from JWT token)
        db: Database session
        
    Returns:
        The updated list of keywords for the user
    """
    updated_keywords = crud_keyword.sync_for_user(
        db=db, 
        user_id=current_user.id, 
        keywords=keywords
    )
    keyword_list = [keyword.keyword for keyword in updated_keywords]
    return SuccessResponse(data=keyword_list, message="關鍵字更新成功") 
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
import math
from typing import Dict, Any

from schemas.invitation_code import (
    InvitationCodeCreate,
    InvitationCodeUpdate,
    InvitationCodeResponse
)
from schemas.user import (
    UserUpdate,
    UserPublic
)
from schemas.notify_setting import NotifySettingResponse
from schemas.response import SuccessResponse, ListResponse, ErrorCodes, EmptyResponse, create_list_response
from core.unified_error_handler import (
    ResourceNotFoundException,
    ResourceConflictException,
    BusinessLogicException
)
from crud import invitation_code as crud_invitation_code
from crud import user as crud_user
from crud import notify_setting as crud_notify_setting
from database.session import get_db
from dependencies import get_current_active_user
from models.user import User
from typing import Optional

router = APIRouter()


@router.post(
    "/invitation-codes",
    response_model=SuccessResponse[InvitationCodeResponse],
    status_code=status.HTTP_201_CREATED,
    summary="建立新的邀請碼",
    description="建立一個新的邀請碼。邀請碼必須是唯一的，由 API 呼叫者手動提供。",
    responses={
        201: {
            "description": "邀請碼建立成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "邀請碼建立成功",
                        "data": {
                            "id": 1,
                            "code": "WELCOME2024",
                            "description": "2024年歡迎新用戶邀請碼",
                            "is_active": True,
                            "expires_at": "2024-12-31-23:59",
                            "created_at": "2024-01-01-00:00",
                            "updated_at": "2024-01-01-00:00"
                        }
                    }
                }
            }
        },
        400: {
            "description": "請求參數錯誤",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "邀請碼為必填欄位",
                        "error_code": "VALIDATION_ERROR"
                    }
                }
            }
        },
        409: {
            "description": "邀請碼已存在",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "邀請碼已存在",
                        "error_code": "RESOURCE_ALREADY_EXISTS"
                    }
                }
            }
        }
    }
)
async def create_invitation_code(
    invitation_code: InvitationCodeCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new invitation code.
    
    The invitation code must be unique and is manually provided by the API caller.
    The system does not auto-generate invitation codes.
    """
    # Check if the code already exists
    existing_code = crud_invitation_code.get_invitation_code_by_code(db, invitation_code.code)
    if existing_code:
        raise ResourceConflictException("邀請碼已存在")
    
    # Create the new invitation code
    created_code = crud_invitation_code.create_invitation_code(db=db, invitation_code=invitation_code)
    return SuccessResponse(data=created_code, message="邀請碼建立成功")


@router.get(
    "/invitation-codes",
    response_model=SuccessResponse[Dict[str, Any]],
    summary="查詢邀請碼列表",
    description="取得所有邀請碼的列表，支援依啟用狀態篩選與分頁功能。",
    responses={
        200: {
            "description": "查詢成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "查詢成功",
                        "data": {
                            "items": [
                                {
                                    "id": 1,
                                    "code": "WELCOME2024",
                                    "description": "2024年歡迎新用戶邀請碼",
                                    "is_active": True,
                                    "expires_at": "2024-12-31-23:59",
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
                }
            }
        }
    }
)
async def get_invitation_codes(
    is_active: Optional[bool] = Query(default=None, description="篩選啟用狀態"),
    page: int = Query(default=1, ge=1, description="頁數"),
    size: int = Query(default=20, ge=1, le=100, description="每頁筆數"),
    db: Session = Depends(get_db)
):
    """
    Get invitation codes list with filtering and pagination.
    
    Supports filtering by active status and pagination with configurable page size.
    """
    # Get invitation codes with filtering and pagination
    invitation_codes, total = crud_invitation_code.get_invitation_codes(
        db=db,
        is_active=is_active,
        page=page,
        size=size
    )
    
    # Convert SQLAlchemy models to Pydantic models
    code_data = [InvitationCodeResponse.model_validate(code) for code in invitation_codes]
    
    return create_list_response(items=code_data, total=total, page=page, size=size)


@router.patch(
    "/invitation-codes/{code_id}",
    response_model=SuccessResponse[InvitationCodeResponse],
    summary="更新邀請碼資訊",
    description="局部更新一個已存在邀請碼的資訊。只會更新請求中提供的欄位。",
    responses={
        200: {
            "description": "更新成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "邀請碼更新成功",
                        "data": {
                            "id": 1,
                            "code": "WELCOME2024",
                            "description": "更新後的描述",
                            "is_active": False,
                            "expires_at": "2024-12-31-23:59",
                            "created_at": "2024-01-01-00:00",
                            "updated_at": "2024-01-15-00:00"
                        }
                    }
                }
            }
        },
        404: {
            "description": "邀請碼不存在",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "邀請碼不存在",
                        "error_code": "RESOURCE_NOT_FOUND"
                    }
                }
            }
        }
    }
)
async def update_invitation_code(
    code_id: int,
    invitation_code_update: InvitationCodeUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing invitation code.
    
    Only the fields provided in the request will be updated.
    The invitation code itself cannot be changed.
    """
    # Update the invitation code
    updated_code = crud_invitation_code.update_invitation_code(
        db=db,
        code_id=code_id,
        invitation_code_update=invitation_code_update
    )
    
    if not updated_code:
        raise ResourceNotFoundException("邀請碼不存在")
    
    return SuccessResponse(data=updated_code, message="邀請碼更新成功")


@router.delete(
    "/invitation-codes/{code_id}",
    response_model=SuccessResponse[None],
    status_code=status.HTTP_200_OK,
    summary="刪除邀請碼",
    description="軟刪除 (停用) 一個邀請碼。將 is_active 設為 false 而不是實際刪除資料。",
    responses={
        200: {
            "description": "刪除成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "邀請碼刪除成功"
                    }
                }
            }
        },
        404: {
            "description": "邀請碼不存在",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "邀請碼不存在",
                        "error_code": "RESOURCE_NOT_FOUND"
                    }
                }
            }
        }
    }
)
async def delete_invitation_code(
    code_id: int,
    db: Session = Depends(get_db)
):
    """
    Soft delete (deactivate) an invitation code.
    
    Sets the is_active field to false instead of actually deleting the record.
    This preserves the historical data while making the invitation code unusable.
    """
    # Soft delete the invitation code
    deleted_code = crud_invitation_code.soft_delete_invitation_code(db=db, code_id=code_id)
    
    if not deleted_code:
        raise ResourceNotFoundException("邀請碼不存在")
    
    return SuccessResponse(data=None, message="邀請碼刪除成功")


# --- User Management API Endpoints ---

@router.get(
    "/users",
    response_model=SuccessResponse[Dict[str, Any]],
    summary="查詢使用者列表",
    description="取得所有使用者的列表，支援依啟用狀態篩選與分頁功能。回應不包含密碼資訊。",
    responses={
        200: {
            "description": "查詢成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "查詢成功",
                        "data": {
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
                }
            }
        }
    }
)
async def get_users(
    is_active: Optional[bool] = Query(default=None, description="篩選啟用狀態"),
    page: int = Query(default=1, ge=1, description="頁數"),
    size: int = Query(default=20, ge=1, le=100, description="每頁筆數"),
    db: Session = Depends(get_db)
):
    """
    Get users list with filtering and pagination.
    
    Supports filtering by active status and pagination with configurable page size.
    Response excludes password_hash field for security.
    """
    # Get users with filtering and pagination
    users, total = crud_user.get_users(
        db=db,
        is_active=is_active,
        page=page,
        size=size
    )
    
    # Convert SQLAlchemy models to Pydantic models
    user_data = [UserPublic.model_validate(user) for user in users]
    
    return create_list_response(items=user_data, total=total, page=page, size=size)


@router.get(
    "/users/{user_id}",
    response_model=SuccessResponse[UserPublic],
    summary="查詢單一使用者資訊",
    description="取得某個特定使用者的詳細資訊。回應不包含密碼資訊。",
    responses={
        200: {
            "description": "查詢成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "取得使用者資訊成功",
                        "data": {
                            "id": 1,
                            "username": "user@example.com",
                            "invite_code_used": "WELCOME2024",
                            "is_active": True,
                            "created_at": "2024-01-01-00:00",
                            "updated_at": "2024-01-01-00:00"
                        }
                    }
                }
            }
        },
        404: {
            "description": "使用者不存在",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "使用者不存在",
                        "error_code": "RESOURCE_NOT_FOUND"
                    }
                }
            }
        }
    }
)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific user by ID.
    
    Returns user information excluding password_hash field for security.
    """
    # Get the user
    user = crud_user.get_user_by_id(db=db, user_id=user_id)
    
    if not user:
        raise ResourceNotFoundException("使用者不存在")
    
    return SuccessResponse(data=user, message="取得使用者資訊成功")


@router.patch(
    "/users/{user_id}",
    response_model=SuccessResponse[UserPublic],
    summary="更新使用者資訊",
    description="更新一個已存在使用者的啟用狀態，主要用於停權或復權。",
    responses={
        200: {
            "description": "更新成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "使用者資訊更新成功",
                        "data": {
                            "id": 1,
                            "username": "user@example.com",
                            "invite_code_used": "WELCOME2024",
                            "is_active": False,
                            "created_at": "2024-01-01-00:00",
                            "updated_at": "2024-01-15-00:00"
                        }
                    }
                }
            }
        },
        404: {
            "description": "使用者不存在",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "使用者不存在",
                        "error_code": "RESOURCE_NOT_FOUND"
                    }
                }
            }
        }
    }
)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing user's active status.
    
    Mainly used for activating or deactivating user accounts.
    Returns updated user information excluding password_hash field.
    """
    # Update the user
    updated_user = crud_user.update_user_active_status(
        db=db,
        user_id=user_id,
        is_active=user_update.is_active
    )
    
    if not updated_user:
        raise ResourceNotFoundException("使用者不存在")
    
    return SuccessResponse(data=updated_user, message="使用者資訊更新成功")


@router.delete(
    "/users/{user_id}",
    response_model=SuccessResponse[None],
    status_code=status.HTTP_200_OK,
    summary="刪除使用者",
    description="軟刪除 (停用) 一個使用者。將 is_active 設為 false 而不是實際刪除資料。",
    responses={
        200: {
            "description": "刪除成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "使用者刪除成功"
                    }
                }
            }
        },
        404: {
            "description": "使用者不存在",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "使用者不存在",
                        "error_code": "RESOURCE_NOT_FOUND"
                    }
                }
            }
        }
    }
)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Soft delete (deactivate) a user.
    
    Sets the is_active field to false instead of actually deleting the record.
    This preserves the historical data while making the user account unusable.
    """
    # Soft delete the user
    deleted_user = crud_user.soft_delete_user(db=db, user_id=user_id)
    
    if not deleted_user:
        raise ResourceNotFoundException("使用者不存在")
    
    return SuccessResponse(data=None, message="使用者刪除成功")


# --- NotifySetting Management API Endpoints ---

@router.get(
    "/notify-settings",
    response_model=SuccessResponse[Dict[str, Any]],
    summary="查詢所有使用者通知設定列表",
    description="取得所有使用者的通知設定列表，支援分頁功能。需要認證權限。",
    responses={
        200: {
            "description": "查詢成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "查詢成功",
                        "data": {
                            "items": [
                                {
                                    "id": 1,
                                    "user_id": 1,
                                    "notify_type": "email",
                                    "email_address": "user@example.com",
                                    "is_active": True,
                                    "created_at": "2024-01-01-00:00",
                                    "updated_at": "2024-01-01-00:00",
                                    "keywords": ["Python", "FastAPI"]
                                }
                            ],
                            "total": 1,
                            "page": 1,
                            "size": 100,
                            "pages": 1
                        }
                    }
                }
            }
        },
        401: {
            "description": "未授權存取",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "未授權存取",
                        "error_code": "UNAUTHORIZED"
                    }
                }
            }
        }
    }
)
async def get_all_notify_settings(
    skip: int = Query(default=0, ge=0, description="跳過筆數"),
    limit: int = Query(default=100, ge=1, le=1000, description="每頁筆數"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all users' notification settings with pagination.
    
    This endpoint is for admin use to view all notification settings across all users.
    Requires authentication to ensure only authorized users can access this data.
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return (max 1000)
        current_user: Current authenticated user (from JWT token)
        db: Database session
        
    Returns:
        Paginated list of all notification settings with metadata
    """
    # Get notification settings with pagination (already includes keywords)
    setting_data = crud_notify_setting.get_multi(db=db, skip=skip, limit=limit)
    
    # Calculate total pages for pagination metadata
    # Since we don't have a count function in get_multi, we'll use len for now
    total = len(setting_data)  # This is not accurate for pagination, but matches the current implementation
    pages = math.ceil(total / limit) if total > 0 else 1
    current_page = (skip // limit) + 1
    
    return SuccessResponse(
        data={
            "items": setting_data,
            "total": total,
            "page": current_page,
            "size": limit,
            "pages": pages
        },
        message="查詢成功"
    )
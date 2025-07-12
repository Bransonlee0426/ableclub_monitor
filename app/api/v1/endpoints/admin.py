from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import math

from schemas.invitation_code import (
    InvitationCodeCreate,
    InvitationCodeUpdate,
    InvitationCodeResponse,
    InvitationCodeListResponse
)
from schemas.user import (
    UserUpdate,
    UserPublic,
    UserListResponse
)
from crud import invitation_code as crud_invitation_code
from crud import user as crud_user
from database.session import get_db
from typing import Optional

router = APIRouter()


@router.post(
    "/invitation-codes",
    response_model=InvitationCodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="建立新的邀請碼",
    description="建立一個新的邀請碼。邀請碼必須是唯一的，由 API 呼叫者手動提供。",
    responses={
        201: {
            "description": "邀請碼建立成功",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "code": "WELCOME2024",
                        "description": "2024年歡迎新用戶邀請碼",
                        "is_active": True,
                        "expires_at": "2024-12-31T23:59:59Z",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                }
            }
        },
        400: {
            "description": "請求參數錯誤",
            "content": {
                "application/json": {
                    "example": {"detail": "邀請碼為必填欄位"}
                }
            }
        },
        409: {
            "description": "邀請碼已存在",
            "content": {
                "application/json": {
                    "example": {"detail": "邀請碼已存在"}
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
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="邀請碼已存在"
        )
    
    # Create the new invitation code
    return crud_invitation_code.create_invitation_code(db=db, invitation_code=invitation_code)


@router.get(
    "/invitation-codes",
    response_model=InvitationCodeListResponse,
    summary="查詢邀請碼列表",
    description="取得所有邀請碼的列表，支援依啟用狀態篩選與分頁功能。",
    responses={
        200: {
            "description": "查詢成功",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "id": 1,
                                "code": "WELCOME2024",
                                "description": "2024年歡迎新用戶邀請碼",
                                "is_active": True,
                                "expires_at": "2024-12-31T23:59:59Z",
                                "created_at": "2024-01-01T00:00:00Z",
                                "updated_at": "2024-01-01T00:00:00Z"
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
    
    # Calculate total pages
    pages = math.ceil(total / size) if total > 0 else 1
    
    return InvitationCodeListResponse(
        items=invitation_codes,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.patch(
    "/invitation-codes/{code_id}",
    response_model=InvitationCodeResponse,
    summary="更新邀請碼資訊",
    description="局部更新一個已存在邀請碼的資訊。只會更新請求中提供的欄位。",
    responses={
        200: {
            "description": "更新成功",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "code": "WELCOME2024",
                        "description": "更新後的描述",
                        "is_active": False,
                        "expires_at": "2024-12-31T23:59:59Z",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-15T00:00:00Z"
                    }
                }
            }
        },
        404: {
            "description": "邀請碼不存在",
            "content": {
                "application/json": {
                    "example": {"detail": "邀請碼不存在"}
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邀請碼不存在"
        )
    
    return updated_code


@router.delete(
    "/invitation-codes/{code_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="刪除邀請碼",
    description="軟刪除 (停用) 一個邀請碼。將 is_active 設為 false 而不是實際刪除資料。",
    responses={
        204: {
            "description": "刪除成功"
        },
        404: {
            "description": "邀請碼不存在",
            "content": {
                "application/json": {
                    "example": {"detail": "邀請碼不存在"}
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邀請碼不存在"
        )
    
    # Return 204 No Content (no response body)


# --- User Management API Endpoints ---

@router.get(
    "/users",
    response_model=UserListResponse,
    summary="查詢使用者列表",
    description="取得所有使用者的列表，支援依啟用狀態篩選與分頁功能。回應不包含密碼資訊。",
    responses={
        200: {
            "description": "查詢成功",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "id": 1,
                                "username": "user@example.com",
                                "invite_code_used": "WELCOME2024",
                                "is_active": True,
                                "created_at": "2024-01-01T00:00:00Z",
                                "updated_at": "2024-01-01T00:00:00Z"
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
    
    # Calculate total pages
    pages = math.ceil(total / size) if total > 0 else 1
    
    return UserListResponse(
        items=users,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get(
    "/users/{user_id}",
    response_model=UserPublic,
    summary="查詢單一使用者資訊",
    description="取得某個特定使用者的詳細資訊。回應不包含密碼資訊。",
    responses={
        200: {
            "description": "查詢成功",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "user@example.com",
                        "invite_code_used": "WELCOME2024",
                        "is_active": True,
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                }
            }
        },
        404: {
            "description": "使用者不存在",
            "content": {
                "application/json": {
                    "example": {"detail": "使用者不存在"}
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="使用者不存在"
        )
    
    return user


@router.patch(
    "/users/{user_id}",
    response_model=UserPublic,
    summary="更新使用者資訊",
    description="更新一個已存在使用者的啟用狀態，主要用於停權或復權。",
    responses={
        200: {
            "description": "更新成功",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "user@example.com",
                        "invite_code_used": "WELCOME2024",
                        "is_active": False,
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-15T00:00:00Z"
                    }
                }
            }
        },
        404: {
            "description": "使用者不存在",
            "content": {
                "application/json": {
                    "example": {"detail": "使用者不存在"}
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="使用者不存在"
        )
    
    return updated_user


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="刪除使用者",
    description="軟刪除 (停用) 一個使用者。將 is_active 設為 false 而不是實際刪除資料。",
    responses={
        204: {
            "description": "刪除成功"
        },
        404: {
            "description": "使用者不存在",
            "content": {
                "application/json": {
                    "example": {"detail": "使用者不存在"}
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="使用者不存在"
        )
    
    # Return 204 No Content (no response body)
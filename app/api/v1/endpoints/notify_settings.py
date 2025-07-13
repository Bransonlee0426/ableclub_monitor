from fastapi import APIRouter, Depends, HTTPException, status, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import ValidationError

from schemas.notify_setting import (
    NotifySettingCreate, 
    NotifySettingUpdate, 
    NotifySettingResponse, 
    NotifySettingListResponse
)
from crud import notify_setting as crud_notify_setting
from dependencies import get_current_active_user
from models.user import User
from database.session import get_db

router = APIRouter()


@router.post(
    "/",
    response_model=NotifySettingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="新增通知設定",
    description="為當前使用者新增一個通知設定。支援條件式驗證：當 notify_type 為 'email' 時，email_address 為必填欄位。",
    responses={
        201: {
            "description": "通知設定建立成功",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "user_id": 1,
                        "notify_type": "email",
                        "email_address": "user@example.com",
                        "is_active": True,
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00"
                    }
                }
            }
        },
        400: {
            "description": "驗證錯誤",
            "content": {
                "application/json": {
                    "examples": {
                        "empty_notify_type": {
                            "summary": "通知類型為空",
                            "value": {"detail": "請確實填寫通知類型"}
                        },
                        "missing_email": {
                            "summary": "Email 通知缺少地址",
                            "value": {"detail": "Email 通知類型必須提供有效的 Email 地址"}
                        }
                    }
                }
            }
        },
        409: {
            "description": "重複的通知設定",
            "content": {
                "application/json": {
                    "example": {"detail": "該通知類型的設定已存在"}
                }
            }
        }
    }
)
async def create_notify_setting(
    notify_setting_data: NotifySettingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> NotifySettingResponse:
    """
    Create a new notification setting for the current user.
    
    Validates that:
    - notify_type is not empty
    - If notify_type is 'email', email_address must be provided and valid
    - The user doesn't already have a setting for this notify_type
    """
    # Check if user already has a setting for this notify_type
    existing_setting = crud_notify_setting.get_notify_setting_by_user_and_type(
        db, current_user.id, notify_setting_data.notify_type
    )
    
    if existing_setting:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="該通知類型的設定已存在"
        )
    
    # Create the notification setting
    db_notify_setting = crud_notify_setting.create_notify_setting(
        db=db,
        user_id=current_user.id,
        notify_setting_data=notify_setting_data
    )
    
    return NotifySettingResponse.model_validate(db_notify_setting)


@router.get(
    "/",
    response_model=NotifySettingListResponse,
    summary="查詢當前使用者的所有通知設定",
    description="取得當前使用者的所有通知設定列表，按建立時間倒序排列。",
    responses={
        200: {
            "description": "查詢成功",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "id": 1,
                                "user_id": 1,
                                "notify_type": "email",
                                "email_address": "user@example.com",
                                "is_active": True,
                                "created_at": "2024-01-01T00:00:00",
                                "updated_at": "2024-01-01T00:00:00"
                            }
                        ],
                        "total": 1
                    }
                }
            }
        }
    }
)
async def get_user_notify_settings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> NotifySettingListResponse:
    """
    Get all notification settings for the current user.
    
    Returns a list of all notification settings ordered by creation date (newest first).
    """
    notify_settings, total = crud_notify_setting.get_user_notify_settings(
        db, current_user.id
    )
    
    return NotifySettingListResponse(
        items=[NotifySettingResponse.model_validate(setting) for setting in notify_settings],
        total=total
    )


@router.patch(
    "/{notify_setting_id}",
    response_model=NotifySettingResponse,
    summary="更新通知設定",
    description="更新指定的通知設定。支援部分更新，只更新提供的欄位。包含條件式驗證：如果最終狀態中 notify_type 為 'email'，則 email_address 不可為空。",
    responses={
        200: {
            "description": "更新成功",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "user_id": 1,
                        "notify_type": "telegram",
                        "email_address": None,
                        "is_active": True,
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T01:00:00"
                    }
                }
            }
        },
        400: {
            "description": "驗證錯誤",
            "content": {
                "application/json": {
                    "example": {"detail": "Email 通知類型必須提供有效的 Email 地址"}
                }
            }
        },
        404: {
            "description": "通知設定不存在",
            "content": {
                "application/json": {
                    "example": {"detail": "找不到指定的通知設定"}
                }
            }
        }
    }
)
async def update_notify_setting(
    notify_setting_id: int = Path(..., description="通知設定 ID"),
    update_data: NotifySettingUpdate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> NotifySettingResponse:
    """
    Update a notification setting.
    
    Validates that:
    - The notification setting exists and belongs to the current user
    - If final state has notify_type as 'email', email_address must not be empty
    """
    # Get current setting to validate final state
    current_setting = crud_notify_setting.get_notify_setting_by_id(
        db, notify_setting_id, current_user.id
    )
    
    if not current_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到指定的通知設定"
        )
    
    # Prepare final state for validation
    final_notify_type = update_data.notify_type if update_data.notify_type is not None else current_setting.notify_type
    final_email_address = update_data.email_address if update_data.email_address is not None else current_setting.email_address
    
    # Validate final state
    if not crud_notify_setting.validate_final_state(final_notify_type, final_email_address):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email 通知類型必須提供有效的 Email 地址"
        )
    
    # Update the setting
    updated_setting = crud_notify_setting.update_notify_setting(
        db=db,
        notify_setting_id=notify_setting_id,
        user_id=current_user.id,
        update_data=update_data
    )
    
    return NotifySettingResponse.model_validate(updated_setting)


@router.delete(
    "/{notify_setting_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="刪除通知設定",
    description="刪除指定的通知設定。只能刪除屬於當前使用者的設定。",
    responses={
        204: {
            "description": "刪除成功"
        },
        404: {
            "description": "通知設定不存在",
            "content": {
                "application/json": {
                    "example": {"detail": "找不到指定的通知設定"}
                }
            }
        }
    }
)
async def delete_notify_setting(
    notify_setting_id: int = Path(..., description="通知設定 ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a notification setting.
    
    The setting must exist and belong to the current user.
    """
    success = crud_notify_setting.delete_notify_setting(
        db=db,
        notify_setting_id=notify_setting_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到指定的通知設定"
        )
    
    return None  # 204 No Content
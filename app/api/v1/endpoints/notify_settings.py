from fastapi import APIRouter, Depends, status, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import ValidationError

from schemas.notify_setting import (
    NotifySettingCreate, 
    NotifySettingUpdate, 
    NotifySettingResponse, 
    NotifySettingListResponse
)
from schemas.response import SuccessResponse, ListResponse, ErrorCodes
from core.unified_error_handler import (
    ResourceNotFoundException,
    ResourceConflictException,
    BusinessLogicException
)
from crud import notify_setting as crud_notify_setting
from dependencies import get_current_active_user
from models.user import User
from database.session import get_db

router = APIRouter()


@router.post(
    "/",
    response_model=SuccessResponse[NotifySettingResponse],
    status_code=status.HTTP_201_CREATED,
    summary="新增通知設定",
    description="為當前使用者新增一個通知設定。支援條件式驗證：當 notify_type 為 'email' 時，email_address 為必填欄位。",
    responses={
        201: {
            "description": "通知設定建立成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "通知設定建立成功",
                        "data": {
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
            }
        },
        400: {
            "description": "驗證錯誤",
            "content": {
                "application/json": {
                    "examples": {
                        "empty_notify_type": {
                            "summary": "通知類型為空",
                            "value": {
                                "success": False,
                                "message": "請確實填寫通知類型",
                                "error_code": "VALIDATION_ERROR"
                            }
                        },
                        "missing_email": {
                            "summary": "Email 通知缺少地址",
                            "value": {
                                "success": False,
                                "message": "Email 通知類型必須提供有效的 Email 地址",
                                "error_code": "VALIDATION_ERROR"
                            }
                        }
                    }
                }
            }
        },
        409: {
            "description": "重複的通知設定",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "該通知類型的設定已存在",
                        "error_code": "RESOURCE_ALREADY_EXISTS"
                    }
                }
            }
        }
    }
)
async def create_notify_setting(
    notify_setting_data: NotifySettingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
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
        raise ResourceConflictException("該通知類型的設定已存在")
    
    # Create the notification setting
    db_notify_setting = crud_notify_setting.create_notify_setting(
        db=db,
        user_id=current_user.id,
        notify_setting_data=notify_setting_data
    )
    
    setting_response = NotifySettingResponse.model_validate(db_notify_setting)
    
    # Return 201 response with proper format
    response_data = SuccessResponse(data=setting_response, message="通知設定建立成功")
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=response_data.model_dump(exclude_none=True)
    )


@router.get(
    "/",
    response_model=SuccessResponse[NotifySettingListResponse],
    summary="查詢當前使用者的所有通知設定",
    description="取得當前使用者的所有通知設定列表，按建立時間倒序排列。",
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
    }
)
async def get_user_notify_settings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all notification settings for the current user.
    
    Returns a list of all notification settings ordered by creation date (newest first).
    """
    notify_settings, total = crud_notify_setting.get_user_notify_settings(
        db, current_user.id
    )
    
    list_response = NotifySettingListResponse(
        items=[NotifySettingResponse.model_validate(setting) for setting in notify_settings],
        total=total
    )
    
    return SuccessResponse(data=list_response, message="查詢成功")


@router.patch(
    "/{notify_setting_id}",
    response_model=SuccessResponse[NotifySettingResponse],
    summary="更新通知設定",
    description="更新指定的通知設定。支援部分更新，只更新提供的欄位。包含條件式驗證：如果最終狀態中 notify_type 為 'email'，則 email_address 不可為空。",
    responses={
        200: {
            "description": "更新成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "通知設定更新成功",
                        "data": {
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
            }
        },
        400: {
            "description": "驗證錯誤",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Email 通知類型必須提供有效的 Email 地址",
                        "error_code": "VALIDATION_ERROR"
                    }
                }
            }
        },
        404: {
            "description": "通知設定不存在",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "找不到指定的通知設定",
                        "error_code": "RESOURCE_NOT_FOUND"
                    }
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
):
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
        raise ResourceNotFoundException("找不到指定的通知設定")
    
    # Prepare final state for validation
    final_notify_type = update_data.notify_type if update_data.notify_type is not None else current_setting.notify_type
    final_email_address = update_data.email_address if update_data.email_address is not None else current_setting.email_address
    
    # Validate final state
    if not crud_notify_setting.validate_final_state(final_notify_type, final_email_address):
        raise BusinessLogicException("Email 通知類型必須提供有效的 Email 地址", ErrorCodes.VALIDATION_ERROR, 400)
    
    # Update the setting
    updated_setting = crud_notify_setting.update_notify_setting(
        db=db,
        notify_setting_id=notify_setting_id,
        user_id=current_user.id,
        update_data=update_data
    )
    
    setting_response = NotifySettingResponse.model_validate(updated_setting)
    return SuccessResponse(data=setting_response, message="通知設定更新成功")


@router.delete(
    "/{notify_setting_id}",
    response_model=SuccessResponse[None],
    status_code=status.HTTP_200_OK,
    summary="刪除通知設定",
    description="刪除指定的通知設定。只能刪除屬於當前使用者的設定。",
    responses={
        200: {
            "description": "刪除成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "通知設定刪除成功"
                    }
                }
            }
        },
        404: {
            "description": "通知設定不存在",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "找不到指定的通知設定",
                        "error_code": "RESOURCE_NOT_FOUND"
                    }
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
        raise ResourceNotFoundException("找不到指定的通知設定")
    
    return SuccessResponse(data=None, message="通知設定刪除成功")
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from schemas.notify_setting import (
    NotifySettingCreate, 
    NotifySettingUpdate, 
    NotifySettingResponse
)
from schemas.response import SuccessResponse, ErrorCodes
from core.unified_error_handler import BusinessLogicException
from crud import notify_setting as crud_notify_setting
from dependencies import get_current_active_user
from models.user import User
from models.notify_setting import NotifySetting
from database.session import get_db

router = APIRouter()



@router.get(
    "/",
    response_model=SuccessResponse[NotifySettingResponse],
    summary="查詢當前使用者的通知設定",
    description="取得當前使用者的通知設定，採用 Singleton Resource 設計模式，每個使用者僅有一組通知設定。",
    responses={
        200: {
            "description": "查詢成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "查詢成功",
                        "data": {
                            "id": 1,
                            "user_id": 1,
                            "notify_type": "email",
                            "email_address": "user@example.com",
                            "is_active": True,
                            "created_at": "2024-01-01T00:00:00",
                            "updated_at": "2024-01-01T00:00:00",
                            "keywords": ["Python", "FastAPI"]
                        }
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
                        "message": "找不到通知設定",
                        "error_code": "RESOURCE_NOT_FOUND"
                    }
                }
            }
        }
    }
)
async def read_my_settings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get notification settings for the current user.
    
    Uses Singleton Resource pattern where each user has exactly one notification setting.
    Raises 404 if no settings exist for the current user.
    """
    # Extract user_id as integer (current_user.id contains the actual integer value)
    user_id: int = int(current_user.id)  # type: ignore
    
    notify_setting = crud_notify_setting.get_by_owner(db, owner_id=user_id)
    
    if not notify_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到通知設定"
        )
    
    # Get user's keywords from the eagerly loaded relationship
    try:
        # Use the pre-loaded keywords from the user relationship
        keywords_list = [keyword.keyword for keyword in notify_setting.user.keywords] if notify_setting.user and notify_setting.user.keywords else []
    except Exception:
        # If accessing pre-loaded keywords fails, use empty list to avoid breaking the main operation
        keywords_list = []
    
    # Create response with keywords
    setting_dict = {
        "id": notify_setting.id,
        "user_id": notify_setting.user_id,
        "notify_type": notify_setting.notify_type,
        "email_address": notify_setting.email_address,
        "is_active": notify_setting.is_active,
        "created_at": notify_setting.created_at,
        "updated_at": notify_setting.updated_at,
        "keywords": keywords_list
    }
    
    setting_response = NotifySettingResponse.model_validate(setting_dict)
    return SuccessResponse(data=setting_response, message="查詢成功")


@router.post(
    "/",
    response_model=SuccessResponse[NotifySettingResponse],
    status_code=status.HTTP_201_CREATED,
    summary="建立當前使用者的通知設定",
    description="為當前使用者建立通知設定，支援關鍵字設定。採用 Singleton Resource 設計，每個使用者只能有一組設定。支援條件式驗證：當 notify_type 為 'email' 時，email_address 為必填欄位。",
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
                            "updated_at": "2024-01-01T00:00:00",
                            "keywords": ["Python", "FastAPI"]
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
            "description": "通知設定已存在",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Notify setting already exists for this user.",
                        "error_code": "RESOURCE_ALREADY_EXISTS"
                    }
                }
            }
        }
    }
)
async def create_my_setting(
    notify_setting_data: NotifySettingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new notification setting for the current user.
    
    Uses Singleton Resource pattern - only one setting per user is allowed.
    Validates that:
    - notify_type is not empty
    - If notify_type is 'email', email_address must be provided and valid
    - The user doesn't already have a setting
    """
    # Extract user_id as integer (current_user.id contains the actual integer value)
    user_id: int = int(current_user.id)  # type: ignore
    
    # Check if user already has a setting (Singleton Resource pattern)
    existing_setting = crud_notify_setting.get_by_owner(db, owner_id=user_id)
    
    if existing_setting:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Notify setting already exists for this user."
        )
    
    # Create the notification setting (with keywords if provided)
    db_notify_setting = crud_notify_setting.create_with_owner(
        db=db,
        owner_id=user_id,
        obj_in=notify_setting_data
    )
    
    # Get user's keywords from the eagerly loaded relationship
    try:
        # Use the pre-loaded keywords from the user relationship
        keywords_list = [keyword.keyword for keyword in db_notify_setting.user.keywords] if db_notify_setting.user and db_notify_setting.user.keywords else []
    except Exception:
        # If accessing pre-loaded keywords fails, use empty list to avoid breaking the main operation
        keywords_list = []
    
    # Create response with keywords
    setting_dict = {
        "id": db_notify_setting.id,
        "user_id": db_notify_setting.user_id,
        "notify_type": db_notify_setting.notify_type,
        "email_address": db_notify_setting.email_address,
        "is_active": db_notify_setting.is_active,
        "created_at": db_notify_setting.created_at,
        "updated_at": db_notify_setting.updated_at,
        "keywords": keywords_list
    }
    
    setting_response = NotifySettingResponse.model_validate(setting_dict)
    
    # Return 201 response with SuccessResponse (same as GET endpoint)
    return SuccessResponse(data=setting_response, message="通知設定建立成功")


@router.put(
    "/",
    response_model=SuccessResponse[NotifySettingResponse],
    summary="更新當前使用者的通知設定",
    description="更新當前使用者的通知設定，支援關鍵字更新。支援部分更新，只更新提供的欄位。包含條件式驗證：如果最終狀態中 notify_type 為 'email'，則 email_address 不可為空。可更新關鍵字列表，提供空陣列將清空所有關鍵字。",
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
                            "updated_at": "2024-01-01T01:00:00",
                            "keywords": ["React", "Vue"]
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
                        "message": "找不到通知設定",
                        "error_code": "RESOURCE_NOT_FOUND"
                    }
                }
            }
        }
    }
)
async def update_my_setting(
    update_data: NotifySettingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update the notification setting for the current user.
    
    Uses Singleton Resource pattern - updates the single setting for this user.
    Validates that:
    - The notification setting exists for the current user
    - If final state has notify_type as 'email', email_address must not be empty
    """
    # Extract user_id as integer (current_user.id contains the actual integer value)
    user_id: int = int(current_user.id)  # type: ignore
    
    # Get current setting to validate it exists and for final state validation
    current_setting = crud_notify_setting.get_by_owner(db, owner_id=user_id)
    
    if not current_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到通知設定"
        )
    
    # Prepare final state for validation
    final_notify_type = update_data.notify_type if update_data.notify_type is not None else str(current_setting.notify_type)
    final_email_address = update_data.email_address if update_data.email_address is not None else (str(current_setting.email_address) if current_setting.email_address else None)
    
    # Validate final state
    if not crud_notify_setting.validate_final_state(final_notify_type, final_email_address):
        raise BusinessLogicException("Email 通知類型必須提供有效的 Email 地址", ErrorCodes.VALIDATION_ERROR, 400)
    
    # Update the setting
    updated_setting = crud_notify_setting.update(
        db=db,
        db_obj=current_setting,
        obj_in=update_data
    )
    
    # Get updated setting with eagerly loaded relationships
    updated_setting_with_relations = crud_notify_setting.get_by_owner(db, owner_id=user_id)
    
    # Get user's keywords from the eagerly loaded relationship
    try:
        # Use the pre-loaded keywords from the user relationship
        keywords_list = [keyword.keyword for keyword in updated_setting_with_relations.user.keywords] if updated_setting_with_relations.user and updated_setting_with_relations.user.keywords else []
    except Exception:
        # If accessing pre-loaded keywords fails, use empty list to avoid breaking the main operation
        keywords_list = []
    
    # Create response with keywords using the updated setting with relations
    setting_dict = {
        "id": updated_setting_with_relations.id,
        "user_id": updated_setting_with_relations.user_id,
        "notify_type": updated_setting_with_relations.notify_type,
        "email_address": updated_setting_with_relations.email_address,
        "is_active": updated_setting_with_relations.is_active,
        "created_at": updated_setting_with_relations.created_at,
        "updated_at": updated_setting_with_relations.updated_at,
        "keywords": keywords_list
    }
    
    setting_response = NotifySettingResponse.model_validate(setting_dict)
    return SuccessResponse(data=setting_response, message="通知設定更新成功")


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="刪除當前使用者的通知設定",
    description="刪除當前使用者的通知設定。採用 Singleton Resource 設計，刪除該使用者的唯一通知設定。",
    responses={
        204: {
            "description": "刪除成功"
        },
        404: {
            "description": "通知設定不存在",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "找不到通知設定",
                        "error_code": "RESOURCE_NOT_FOUND"
                    }
                }
            }
        }
    }
)
async def delete_my_setting(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete the notification setting for the current user.
    
    Uses Singleton Resource pattern - deletes the single setting for this user.
    Returns 204 No Content on successful deletion.
    """
    # Extract user_id as integer (current_user.id contains the actual integer value)
    user_id: int = int(current_user.id)  # type: ignore
    
    # Check if setting exists
    current_setting = crud_notify_setting.get_by_owner(db, owner_id=user_id)
    
    if not current_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到通知設定"
        )
    
    # Delete the setting
    crud_notify_setting.remove_by_owner(db=db, owner_id=user_id)
    
    # Return 204 No Content (FastAPI will handle the empty response)
    return None
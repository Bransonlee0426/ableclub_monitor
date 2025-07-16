"""
Development-only authentication endpoints for easier testing.
WARNING: This should NEVER be used in production!
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import timedelta

from core.security import create_access_token
from crud import user as crud_user
from database.session import get_db
from schemas.auth import Token
from schemas.response import SuccessResponse, TokenResponse, ErrorCodes
from core.unified_error_handler import (
    BusinessLogicException,
    ResourceNotFoundException
)
from core.config import settings

router = APIRouter()

# Enable in development - check if we're using default secret key (indicates dev environment)
DEV_MODE = settings.SECRET_KEY == "a_very_secret_key_that_should_be_changed"

@router.post(
    "/dev-login",
    response_model=SuccessResponse[TokenResponse],
    summary="🚧 開發用快速登入 (僅開發環境)",
    description="⚠️ 僅供開發測試使用！產線環境必須關閉此端點。無需密碼即可取得 30 天有效期的 token。",
    tags=["🚧 Development Only"]
)
async def dev_quick_login(
    username: str = "bransonlee0426@gmail.com",
    db: Session = Depends(get_db)
):
    """
    Development-only quick login that bypasses password check.
    
    WARNING: This endpoint should NEVER be enabled in production!
    """
    if not DEV_MODE:
        raise BusinessLogicException("此端點僅在開發環境可用", ErrorCodes.DEV_ENVIRONMENT_ONLY, 404)
    
    # Check if user exists and is active
    user = crud_user.get_user_by_username(db, username=username)
    if not user:
        raise ResourceNotFoundException(f"使用者 {username} 不存在")
    
    if not user.is_active:
        raise BusinessLogicException("使用者帳號已被停用", ErrorCodes.ACCOUNT_DISABLED, 400)
    
    # Create long-lived token (30 days)
    expires_delta = timedelta(days=30)
    access_token = create_access_token(subject=user.username, expires_delta=expires_delta)
    
    token_data = TokenResponse(access_token=access_token, token_type="bearer")
    
    return SuccessResponse(
        data=token_data,
        message="🚧 開發模式登入成功 (有效期: 30天)"
    )


@router.get(
    "/dev-token",
    response_model=SuccessResponse[dict],
    summary="🚧 取得當前開發 token 資訊 (僅開發環境)",
    description="⚠️ 僅供開發測試使用！顯示預設使用者的長期 token。",
    tags=["🚧 Development Only"]
)
async def get_dev_token():
    """
    Get a pre-generated development token for quick testing.
    """
    if not DEV_MODE:
        raise BusinessLogicException("此端點僅在開發環境可用", ErrorCodes.DEV_ENVIRONMENT_ONLY, 404)
    
    username = "bransonlee0426@gmail.com"
    expires_delta = timedelta(days=30)
    token = create_access_token(subject=username, expires_delta=expires_delta)
    
    token_data = {
        "dev_user": username,
        "token": token,
        "expires_in_days": 30,
        "usage": {
            "swagger_auth": token,
            "curl_header": f"Authorization: Bearer {token}"
        }
    }
    
    return SuccessResponse(
        data=token_data,
        message="🚧 開發 token 資訊取得成功"
    )
from fastapi import APIRouter, Depends, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from schemas.auth import LoginOrRegisterRequest, Token
from schemas.response import SuccessResponse, AuthResponse, TokenResponse, ErrorCodes
from core.unified_error_handler import (
    AuthenticationException, 
    BusinessLogicException, 
    ResourceNotFoundException
)
from crud import user as crud_user
from crud import invitation_code as crud_invitation_code
from core import security
from database.session import get_db

router = APIRouter()

@router.post(
    "/login-or-register", 
    response_model=SuccessResponse[TokenResponse],
    summary="使用者登入或註冊",
    description="此端點整合了使用者登入和註冊功能。系統會自動偵測使用者是否存在，並執行相應的操作。",
    responses={
        200: {
            "description": "使用者成功登入",
            "content": {
                "application/json": {
                    "example": {
                        "success": True, 
                        "message": "登入成功", 
                        "data": {"access_token": "jwt.token.here", "token_type": "bearer"}
                    }
                }
            }
        },
        201: {
            "description": "新使用者成功註冊",
            "content": {
                "application/json": {
                    "example": {
                        "success": True, 
                        "message": "註冊成功", 
                        "data": {"access_token": "jwt.token.here", "token_type": "bearer"}
                    }
                }
            }
        },
        400: {
            "description": "邀請碼無效",
            "content": {
                "application/json": {
                    "example": {
                        "success": False, 
                        "message": "邀請碼無效。", 
                        "error_code": "INVALID_INVITATION_CODE"
                    }
                }
            }
        },
        401: {
            "description": "驗證失敗 (密碼錯誤或帳號停用)",
            "content": {
                "application/json": {
                    "example": {
                        "success": False, 
                        "message": "密碼錯誤、請重新確認。", 
                        "error_code": "INVALID_CREDENTIALS"
                    }
                }
            }
        },
        402: {
            "description": "新使用者缺少邀請碼",
            "content": {
                "application/json": {
                    "example": {
                        "success": False, 
                        "message": "您尚未註冊，請輸入邀請碼", 
                        "error_code": "REGISTRATION_REQUIRED"
                    }
                }
            }
        }
    }
)
async def login_or_register(
    request: LoginOrRegisterRequest, 
    db: Session = Depends(get_db)
):
    """
    Handles user login and registration.
    - If the user exists, it attempts to log them in.
    - If the user does not exist, it attempts to register them using an invite code.
    """
    user = crud_user.get_user_by_username(db, username=request.username)

    # --- Login Path ---
    if user:
        if not user.is_active:
            # To prevent leaking user status, return the same error as a wrong password.
            raise AuthenticationException("密碼錯誤、請重新確認。")

        if not security.verify_password(request.password, user.password_hash):
            raise AuthenticationException("密碼錯誤、請重新確認。")

        # Generate access token for the existing user.
        access_token = security.create_access_token(subject=user.username)
        token_data = TokenResponse(access_token=access_token, token_type="bearer")
        return SuccessResponse(data=token_data, message="登入成功")

    # --- Registration Path ---
    else:
        if not request.inviteCode:
            raise BusinessLogicException("您尚未註冊，請輸入邀請碼", ErrorCodes.REGISTRATION_REQUIRED, 402)

        invitation_code = crud_invitation_code.get_valid_code(db, code=request.inviteCode)
        if not invitation_code or not invitation_code.is_active:
            raise BusinessLogicException("邀請碼無效。", ErrorCodes.INVALID_INVITATION_CODE, 400)

        # Create a new user.
        new_user = crud_user.create_user(
            db=db, 
            username=request.username, 
            password=request.password,
            invite_code=request.inviteCode
        )
        
        # Note: In a real application, you would deactivate or decrement the invitation code here.

        # Generate access token for the new user.
        access_token = security.create_access_token(subject=new_user.username)
        token_data = TokenResponse(access_token=access_token, token_type="bearer")
        
        # Return a 201 Created response for successful registration.
        response_data = SuccessResponse(data=token_data, message="註冊成功")
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=response_data.model_dump(exclude_none=True)
        )
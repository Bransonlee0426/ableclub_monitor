from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from schemas.auth import LoginOrRegisterRequest, ResponseModel, Token
from crud import user as crud_user
from crud import invitation_code as crud_invitation_code
from core import security
from database.session import get_db

router = APIRouter()

@router.post(
    "/login-or-register", 
    response_model=ResponseModel,
    summary="使用者登入或註冊",
    description="此端點整合了使用者登入和註冊功能。系統會自動偵測使用者是否存在，並執行相應的操作。",
    responses={
        200: {
            "description": "使用者成功登入",
            "content": {
                "application/json": {
                    "example": {"success": True, "message": "登入成功", "token": {"access_token": "jwt.token.here", "token_type": "bearer"}}
                }
            }
        },
        201: {
            "description": "新使用者成功註冊",
            "content": {
                "application/json": {
                    "example": {"success": True, "message": "註冊成功", "token": {"access_token": "jwt.token.here", "token_type": "bearer"}}
                }
            }
        },
        400: {
            "description": "邀請碼無效",
            "content": {
                "application/json": {
                    "example": {"detail": "邀請碼無效。"}
                }
            }
        },
        401: {
            "description": "驗證失敗 (密碼錯誤或帳號停用)",
            "content": {
                "application/json": {
                    "example": {"detail": "密碼錯誤、請重新確認。"}
                }
            }
        },
        402: {
            "description": "新使用者缺少邀請碼",
            "content": {
                "application/json": {
                    "example": {"detail": "您尚未註冊，請輸入邀請碼"}
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
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="密碼錯誤、請重新確認。")

        if not security.verify_password(request.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="密碼錯誤、請重新確認。")

        # Generate access token for the existing user.
        access_token = security.create_access_token(subject=user.username)
        return ResponseModel(
            success=True, 
            message="登入成功", 
            token=Token(access_token=access_token, token_type="bearer")
        )

    # --- Registration Path ---
    else:
        if not request.inviteCode:
            raise HTTPException(status_code=402, detail="您尚未註冊，請輸入邀請碼")

        invitation_code = crud_invitation_code.get_valid_code(db, code=request.inviteCode)
        if not invitation_code or not invitation_code.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邀請碼無效。")

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
        
        # Return a 201 Created response for successful registration.
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=ResponseModel(
                success=True, 
                message="註冊成功", 
                token=Token(access_token=access_token, token_type="bearer")
            ).model_dump(exclude_none=True)
        )
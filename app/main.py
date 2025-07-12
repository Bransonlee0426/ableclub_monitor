from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api.v1.api import api_router
from schemas.auth import ResponseModel

# Create FastAPI app instance
app = FastAPI(
    title="AbleClub Monitor API",
    description="API for monitoring and sending notifications for AbleClub courses.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom exception handler for Pydantic validation errors.
    This handler intercepts FastAPI's default 422 Unprocessable Entity response
    and returns a custom 400 Bad Request response in our standard format.
    """
    # Here, we can customize the error message based on the validation error details.
    # For now, we'll use a generic message that matches the test cases.
    error_messages = {
        "username": "帳號錯誤、請重新確認。",
        "password": "密碼錯誤、請重新確認。",
    }
    
    # Find the first field with an error to determine the message
    error_field = exc.errors()[0]['loc'][-1]
    message = error_messages.get(error_field, "參數驗證失敗")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ResponseModel(success=False, message=message).model_dump(exclude_none=True),
    )

@app.get("/", 
         tags=["Root"], 
         summary="API 健康檢查",
         description="檢查 API 服務狀態")
def read_root():
    """
    Root endpoint to check API status.
    """
    return {"status": "ok", "message": "Welcome to the AbleClub Monitor API!"}

# Include the main API router
# All routes from app/api/v1/api.py will be included under the /api/v1 prefix
app.include_router(api_router, prefix="/api/v1")

# The old notification endpoints are now removed from here
# and will be re-implemented under the new router structure.

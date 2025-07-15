from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from schemas.auth import ResponseModel
from core.config import settings

# Define server configurations for different environments
servers = [
    {
        "url": "http://127.0.0.1:8000",
        "description": "🔧 Local Development Server"
    },
    {
        "url": "https://ableclub-monitor-dev-205163530380.asia-east1.run.app",
        "description": "🚧 Development Environment (GCP Cloud Run)"
    },
    {
        "url": "https://ableclub-monitor-205163530380.asia-east1.run.app",
        "description": "🌐 Production Environment (GCP Cloud Run)"
    }
]

# Create FastAPI app instance with multiple server configurations
app = FastAPI(
    title="AbleClub Monitor API",
    description="API for monitoring and sending notifications for AbleClub courses.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    servers=servers
)

# Configure CORS settings based on environment
if getattr(settings, 'ENABLE_CORS', False):
    # Development environment: allow all origins for Swagger UI testing
    allowed_origins = ["*"] if settings.LOG_LEVEL == "DEBUG" else [
        "https://ableclub-monitor-205163530380.asia-east1.run.app",  # Production
        "https://ableclub-monitor-dev-205163530380.asia-east1.run.app",  # Development
        "http://127.0.0.1:8000",  # Local development
        "http://localhost:8000",  # Alternative local
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
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

# Database initialization
from database.init import init_database, get_database_info

@app.on_event("startup")
async def startup_event():
    """
    Initialize database on application startup
    """
    try:
        init_database()
    except Exception as e:
        print(f"Database initialization failed: {e}")
        # Don't fail the startup, just log the error

@app.get("/api/v1/system/database-info", 
         tags=["System"], 
         summary="取得資料庫資訊",
         description="檢查資料庫狀態和表格存在情況")
def database_info():
    """
    Get database information and table status
    """
    return get_database_info()

@app.post("/api/v1/system/init-database", 
          tags=["System"], 
          summary="初始化資料庫",
          description="手動初始化資料庫表格")
def manual_database_init():
    """
    Manually initialize database tables
    """
    from database.init import init_database
    success = init_database()
    return {
        "success": success,
        "message": "資料庫初始化完成" if success else "資料庫初始化失敗"
    }

# Include the main API router
# All routes from app/api/v1/api.py will be included under the /api/v1 prefix
app.include_router(api_router, prefix="/api/v1")

# The old notification endpoints are now removed from here
# and will be re-implemented under the new router structure.

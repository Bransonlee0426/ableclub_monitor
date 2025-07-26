from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
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
    description="🚀 AbleClub Monitor API - 開發版",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_version="3.0.2",
    servers=servers,
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "defaultModelsExpandDepth": 1,
        "defaultModelExpandDepth": 1,
        "displayOperationId": False,
        "filter": True
    }
)

# Configure CORS settings based on environment
if getattr(settings, 'ENABLE_CORS', False):
    # Development environment: allow all origins for Swagger UI testing
    allowed_origins = ["*"] if settings.LOG_LEVEL == "DEBUG" else [
        "https://ableclub-monitor-205163530380.asia-east1.run.app",  # Production
        "https://ableclub-monitor-dev-205163530380.asia-east1.run.app",  # Development
        "https://ableclub-monitor-prod.web.app",  # Firebase frontend (production)
        "https://ableclub-monitor-prod.firebaseapp.com",  # Firebase frontend (legacy)
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
else:
    # Always enable basic CORS for API functionality
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

# Import unified error handler
from core.unified_error_handler import UnifiedErrorHandler, BusinessLogicException
from sqlalchemy.exc import SQLAlchemyError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Unified validation exception handler
    """
    return await UnifiedErrorHandler.validation_exception_handler(request, exc)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Unified HTTP exception handler
    """
    return await UnifiedErrorHandler.http_exception_handler(request, exc)

@app.exception_handler(BusinessLogicException)
async def business_logic_exception_handler(request: Request, exc: BusinessLogicException):
    """
    Handle custom business logic exceptions
    """
    return UnifiedErrorHandler.create_error_response(
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handle database errors
    """
    return await UnifiedErrorHandler.sqlalchemy_exception_handler(request, exc)

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions
    """
    return await UnifiedErrorHandler.general_exception_handler(request, exc)

@app.get("/", 
         tags=["Root"], 
         summary="API 健康檢查",
         description="檢查 API 服務狀態")
def read_root():
    """
    Root endpoint to check API status.
    """
    return {
        "status": "ok", 
        "message": "Welcome to the AbleClub Monitor API!",
        "version": "1.0.0",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/health", 
         tags=["Health"], 
         summary="簡易健康檢查",
         description="簡易健康檢查端點，用於 Cloud Run 健康監測")
def health_check():
    """
    Simple health check endpoint for Cloud Run.
    Returns 200 OK to indicate service is ready.
    """
    try:
        # Simple database connectivity check
        from database.session import get_db
        db = next(get_db())
        db.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "service": "ableclub-monitor"
        }
    except Exception as e:
        # Still return healthy to prevent restart loops
        return {
            "status": "healthy",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "service": "ableclub-monitor",
            "note": "startup_phase"
        }



# Database initialization
from database.init import init_database, get_database_info

@app.on_event("startup")
async def startup_event():
    """
    Initialize database and start scheduler on application startup
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize database (with timeout to prevent hanging)
        logger.info("正在初始化資料庫...")
        init_database()
        logger.info("資料庫初始化完成")
        
        logger.info(f"應用程式啟動完成，健康檢查端點：/health")
        
        # Start job scheduler if enabled (with delay for Cloud Run)
        if settings.SCHEDULER_ENABLED:
            logger.info("排程器將在 30 秒後背景啟動")
            # Schedule the scheduler to start after 30 seconds for faster deployment
            import asyncio
            asyncio.create_task(delayed_scheduler_start())
        else:
            logger.info("任務排程器已在設定中停用")
            
    except Exception as e:
        logger.error(f"啟動初始化失敗: {e}")
        # Don't fail the startup, just log the error - continue serving requests

async def delayed_scheduler_start():
    """
    Start the scheduler after a delay to allow container to fully start
    """
    import logging
    import asyncio
    
    logger = logging.getLogger(__name__)
    
    try:
        # Wait 30 seconds before starting scheduler
        logger.info("等待 30 秒後啟動排程器...")
        await asyncio.sleep(30)  # 30 seconds
        
        logger.info("正在啟動任務排程器...")
        from scheduler.job_scheduler import scheduler_manager
        await scheduler_manager.start_scheduler()
        logger.info("任務排程器延遲啟動完成")
        
    except Exception as e:
        logger.error(f"延遲啟動排程器失敗: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Gracefully shutdown scheduler on application shutdown
    """
    try:
        if settings.SCHEDULER_ENABLED:
            from scheduler.job_scheduler import scheduler_manager
            await scheduler_manager.shutdown_scheduler()
    except Exception as e:
        print(f"Error during shutdown: {e}")

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

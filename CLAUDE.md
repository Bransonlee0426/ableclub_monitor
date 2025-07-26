# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Testing
```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_auth_api.py

# Run tests in verbose mode
pytest -v
```

### Code Quality
```bash
# Check syntax
python -m py_compile app/main.py

# Update requirements after adding new packages
pip freeze > requirements.txt
```

### Application Tasks
```bash
# Run web scraping tasks
python -m scraper.tasks

# Test API health
curl http://127.0.0.1:8000/

# Test email notifications
curl -X GET "http://127.0.0.1:8000/api/v1/notifications/test-email"

# Check job scheduler status
curl -X GET "http://127.0.0.1:8000/api/v1/health/scheduler"

# View job execution status
curl -X GET "http://127.0.0.1:8000/api/v1/jobs/scraper/status"

# Stop scheduled job (if needed)
curl -X POST "http://127.0.0.1:8000/api/v1/jobs/scraper/stop"
```

## Architecture Overview

This is a FastAPI-based web scraping and monitoring application for AbleClub Taiwan with authentication, personalized notification system, keyword filtering, and automated job scheduling features.

### Core Structure
- **app/main.py**: FastAPI application entry point with custom exception handling and job scheduler integration
- **app/api/v1/**: API versioning structure with modular endpoints
  - **endpoints/auth.py**: Authentication endpoints (login, token validation)
  - **endpoints/users.py**: User management endpoints
  - **endpoints/admin.py**: Admin user management endpoints
  - **endpoints/notify_settings.py**: User notification preference management
  - **endpoints/keywords.py**: User keyword management endpoints
  - **endpoints/notifications.py**: Notification testing endpoints
  - **endpoints/jobs.py**: Job scheduling and monitoring endpoints
  - **endpoints/scraped_events.py**: Event data management endpoints
  - **endpoints/dev_auth.py**: Development environment authentication
- **core/config.py**: Centralized configuration using Pydantic settings
- **core/security.py**: JWT token handling and password hashing utilities
- **core/datetime_utils.py**: Taiwan timezone datetime formatting utilities

### Job Scheduling System
- **scheduler/**: Job scheduling and management
  - **job_scheduler.py**: APScheduler configuration and management
  - **job_manager.py**: Job execution logic with retry and error handling
- **app/jobs/**: Scheduled job implementations
  - **notification_job.py**: Complete notification processing job with keyword matching
- **models/job_execution_history.py**: Database model for tracking job executions
- **notifications/job_notifications.py**: Email notification system for job failures

### Data Layer
- **models/**: SQLAlchemy ORM models for database entities
  - **user.py**: User authentication model
  - **invitation_code.py**: Invitation code system
  - **event.py**: Event tracking model (scraped events)
  - **notify_setting.py**: User notification preferences model
  - **keyword.py**: User keyword filtering model
  - **job_execution_history.py**: Job execution tracking model
- **schemas/**: Pydantic schemas for API request/response validation with Taiwan timezone formatting
- **crud/**: Database operation utilities following repository pattern
- **database/session.py**: SQLAlchemy database session configuration

### Business Logic
- **scraper/tasks.py**: Web scraping functionality for AbleClub website using Playwright
- **notifications/sender.py**: Multi-channel notification system (Email + Telegram)

### Key Configuration
- Uses SQLite database (configurable via DATABASE_URL for local, PostgreSQL for production)
- JWT authentication with configurable expiration
- Email notifications via SMTP (Gmail support) + Telegram Bot
- Environment variables managed through .env file
- **Job scheduler enabled in production** (SCHEDULER_ENABLED=true)
- **Taiwan timezone datetime formatting** across all API responses (YYYY-MM-DD-HH:mm format)
- **Environment-aware API calls** (BASE_API_URL for notification job)

### API Structure
All API endpoints are versioned under `/api/v1/`:
- Authentication routes: `/api/v1/auth/`
- User management: `/api/v1/users/`
- Admin management: `/api/v1/admin/`
- Notification settings: `/api/v1/notify-settings/`
- Keyword management: `/api/v1/keywords/`
- Job management: `/api/v1/jobs/`
- Event management: `/api/v1/scraped-events/`
- Health checks: `/api/v1/health/`
- Main health check: `/` (root level)

### Job Scheduling Features
- **Automated scraping**: Runs corporate events scraper every hour using Playwright
- **Automated notifications**: Processes user settings and sends personalized notifications
- **Error handling**: Automatic retry (up to 3 attempts) with exponential backoff
- **Failure management**: Pauses job after 3 consecutive failures, auto-resumes after 6 hours
- **History tracking**: Complete execution history with success/failure tracking
- **Data cleanup**: Automatically removes execution records older than 3 months
- **Manual control**: API endpoints to stop jobs and view status
- **Keyword matching**: Case-insensitive keyword filtering for personalized notifications

### Testing Framework
- Uses pytest with async support
- Coverage reporting configured for app directory
- Test files follow `test_*.py` pattern in tests/ directory
- Custom validation error handling returns 400 status codes with Chinese error messages

### Authentication System
- JWT-based authentication with access tokens
- Password hashing using bcrypt
- Custom response format with success/message structure
- Invitation code system for user registration

### Job Scheduler Configuration

#### Enable Scheduler
To enable the job scheduler, set the following environment variables:

```bash
# .env file
SCHEDULER_ENABLED=true
SCHEDULER_TIMEZONE=Asia/Taipei
SCRAPER_JOB_INTERVAL_HOURS=1
JOB_MAX_INSTANCES=1
JOB_RETRY_MAX=3
```

#### Job Scheduler Behavior
- **Startup**: Scheduler starts automatically when application starts (if enabled)
- **First execution**: Runs immediately on startup, then every hour
- **Retry logic**: Up to 3 retries with increasing wait times (1min, 2min, 3min)
- **Failure handling**: Pauses job after 3 consecutive failures
- **Auto-recovery**: Resumes automatically after 6 hours
- **Data cleanup**: Removes execution records older than 3 months before each run

#### Production Deployment
For production deployment with auto-restart capabilities, use one of these service managers:

**Systemd Service:**
```bash
sudo systemctl enable ableclub-monitor.service
sudo systemctl start ableclub-monitor.service
```

**Docker Compose:**
```bash
docker-compose up -d  # Includes restart: unless-stopped
```

---

## ⚠️ Important Development Guidelines

### Environment-Aware Development
When developing new features, **ALWAYS** consider both local and production environments:

1. **Use Environment Variables**: Never hardcode URLs, file paths, or environment-specific values
   - ❌ Bad: `http://localhost:8000/api/v1/endpoint`
   - ✅ Good: `f"{BASE_API_URL}/api/v1/endpoint"` where `BASE_API_URL` is from environment

2. **Configuration Examples**:
   ```python
   # Get base API URL from environment
   BASE_API_URL = os.getenv("BASE_API_URL", "http://127.0.0.1:8000")
   
   # Database URL for different environments
   DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
   ```

3. **Common Environment Variables to Externalize**:
   - API URLs (`BASE_API_URL`, `EXTERNAL_API_URL`)
   - Database connections (`DATABASE_URL`)
   - File paths (`UPLOAD_PATH`, `LOG_PATH`)
   - Service endpoints (`NOTIFICATION_SERVICE_URL`)
   - Feature flags (`FEATURE_ENABLED`)

4. **Testing in Both Environments**:
   - Test locally with local configurations
   - Verify production deployment works with production configurations
   - Use different `.env` files for each environment

**Remember**: What works in local development may fail in production if environment-specific values are hardcoded!

---

## Detailed Project Structure

```
ableclub_monitor/
├── app/                           # 主要應用程式
│   ├── main.py                   # FastAPI 應用程式進入點
│   └── api/v1/                   # API 版本控制
│       ├── api.py               # API 路由統整
│       └── endpoints/           # 具體 API 端點實作
│           ├── auth.py         # 認證相關端點
│           ├── users.py        # 使用者管理端點
│           ├── admin.py        # 管理員功能端點
│           ├── admin_updated.py # 更新的管理員功能
│           ├── dev_auth.py     # 開發環境認證端點
│           ├── notifications.py # 通知相關端點
│           ├── notify_settings.py # 通知設定管理端點
│           └── keywords.py     # 關鍵字管理端點
├── core/                         # 核心配置與工具
│   ├── config.py               # 環境變數與設定管理
│   ├── security.py             # JWT 與密碼安全工具
│   ├── error_handler.py        # 錯誤處理機制
│   └── unified_error_handler.py # 統一錯誤處理器
├── database/                     # 資料庫相關
│   ├── init.py                 # 資料庫初始化
│   └── session.py              # SQLAlchemy 連線設定
├── models/                       # SQLAlchemy 資料模型
│   ├── user.py                 # 使用者資料模型
│   ├── event.py                # 事件資料模型
│   ├── invitation_code.py      # 邀請碼資料模型
│   ├── notify_setting.py       # 通知設定資料模型
│   ├── keyword.py              # 關鍵字資料模型
│   └── job_execution_history.py # 任務執行歷史模型
├── schemas/                      # Pydantic 資料驗證 (台灣時區格式化)
│   ├── auth.py                 # 認證相關資料結構
│   ├── user.py                 # 使用者相關資料結構
│   ├── invitation_code.py      # 邀請碼資料結構
│   ├── notification.py         # 通知相關資料結構
│   ├── notify_setting.py       # 通知設定資料結構
│   ├── keyword.py              # 關鍵字相關資料結構
│   ├── scraped_event.py        # 爬取事件資料結構
│   ├── job_execution_history.py # 任務執行歷史資料結構
│   └── response.py             # 統一回應格式
├── crud/                         # 資料庫操作層
│   ├── user.py                 # 使用者 CRUD 操作
│   ├── invitation_code.py      # 邀請碼 CRUD 操作
│   ├── notify_setting.py       # 通知設定 CRUD 操作
│   ├── keyword.py              # 關鍵字 CRUD 操作
│   ├── event.py                # 事件 CRUD 操作
│   └── crud_job_execution_history.py # 任務執行歷史 CRUD 操作
├── scheduler/                    # 排程系統
│   ├── job_scheduler.py        # APScheduler 管理
│   └── job_manager.py          # 任務執行邏輯
├── scraper/                      # 網頁抓取功能
│   └── tasks.py               # 爬蟲任務實作 (Playwright)
├── notifications/                # 通知系統
│   ├── sender.py              # 多管道通知發送器
│   └── job_notifications.py   # 任務失敗通知
├── tests/                        # 測試套件
│   ├── conftest.py            # pytest 配置
│   ├── test_main.py           # 主程式測試
│   ├── test_auth_api.py       # 認證 API 測試
│   ├── test_user_admin_api.py # 使用者管理 API 測試
│   ├── test_invitation_code_api.py # 邀請碼 API 測試
│   ├── test_notify_settings_api.py # 通知設定 API 測試
│   ├── test_keyword_api.py    # 關鍵字 API 測試
│   └── test_security.py       # 安全模組測試
├── logs/                         # 日誌檔案目錄
├── deploy/                       # 部署相關檔案
│   ├── deploy-dev.sh          # 開發環境部署腳本
│   ├── deploy-prod.sh         # 生產環境部署腳本
│   ├── env/                   # 環境配置檔案
│   │   ├── dev.env           # 開發環境配置
│   │   └── prod.env          # 生產環境配置
│   └── README.md             # 部署說明文件
├── requirements.txt              # Python 依賴套件
├── pytest.ini                   # pytest 配置檔案
├── Dockerfile                    # Docker 容器設定
├── docker-compose.yml           # Docker 編排設定
├── test_error_handling.py       # 錯誤處理測試
├── dependencies.py              # 依賴注入配置
├── CLAUDE.md                    # Claude Code 專案指引
├── Gemini.md                    # Gemini 相關文件
└── README.md                    # 專案說明文件
```

## Detailed Architecture Design

### Overall Architecture
This project uses a **Layered Architecture**:
```
API Layer (FastAPI) → Business Logic Layer (Scraper/Notifications) → Data Access Layer (CRUD) → Data Model Layer (SQLAlchemy)
```

### Core Module Descriptions
| Module | Function | Technology |
|---|---|---|
| **API Layer** | RESTful API endpoints, version controlled | FastAPI + Uvicorn |
| **Authentication System** | JWT login, invitation code registration, dev env auth | JWT + Bcrypt |
| **Admin System** | User management, invitation code management | FastAPI + SQLAlchemy |
| **Notification Settings** | Personalized notification preferences | FastAPI + CRUD |
| **Keyword Management** | Personalized keyword filtering, idempotent ops | FastAPI + CRUD |
| **Data Layer** | ORM models, CRUD operations | SQLAlchemy + SQLite/PostgreSQL |
| **Error Handling** | Unified error handling, exception management | FastAPI Exception Handler |
| **Scraper System** | AbleClub website monitoring | Playwright + Selenium |
| **Notification System** | Email + Telegram multi-channel | SMTP + Bot API |
| **Testing System** | Unit tests, coverage reports | pytest + asyncio |

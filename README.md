# AbleClub Monitor

一個用於監控和抓取 AbleClub Taiwan 網站資訊的專案，包含完整的認證系統、通知功能和 Web API。

## 🚀 開發環境啟動指南

### 📋 首次設定

```bash
# 1. 建立虛擬環境（首次使用）
python3 -m venv .venv

# 2. 建立環境變數檔案
# 複製範本檔案，並根據您的本機環境進行設定
cp .env.example .env

# 3. 編輯 .env 檔案，設定必要的環境變數
# 例如：資料庫路徑、Email 帳號等
```

### ⚡ 開發環境啟動流程

```bash
# 1. 激活虛擬環境
source .venv/bin/activate

# 2. 安裝/更新依賴套件
pip install -r requirements.txt

# 3. 啟動 FastAPI 開發服務器
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 4. 關閉 FastAPI 開發服務器
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 --workers 1 --no-reload

```



### 🔍 驗證啟動狀態

```bash
# 檢查 API 是否正常運行
curl http://127.0.0.1:8000/

# 預期回應：{"status":"ok","message":"Welcome to the AbleClub Monitor API!"}

# 查看 API 文件
# 瀏覽器開啟：http://127.0.0.1:8000/docs
```

### 🔧 常用開發指令

```bash
# 更新 requirements.txt（安裝新套件後）
pip freeze > requirements.txt

# 執行測試
pytest

# 執行測試並查看覆蓋率
pytest --cov=app
```

## 📁 專案結構

```
ableclub_monitor/
├── app/              # 主要應用程式 (FastAPI)
├── core/             # 核心配置與工具
├── database/         # 資料庫相關
├── models/           # SQLAlchemy 資料模型
├── schemas/          # Pydantic 資料驗證
├── crud/             # 資料庫操作層
├── scraper/          # 網頁抓取功能
├── notifications/    # 通知系統
├── tests/            # 測試套件
├── deploy/           # 部署相關腳本 (詳細說明請見內部文件)
├── requirements.txt  # Python 依賴套件
├── Dockerfile        # Docker 容器設定
└── README.md         # 專案說明文件
```

## 🏗️ 架構設計

此專案採用 **分層架構 (Layered Architecture)** 設計，實現了關注點分離，提高了程式碼的可維護性與可擴展性。

```
API 層 (FastAPI) → 業務邏輯層 (爬蟲/通知) → 資料存取層 (CRUD) → 資料模型層 (SQLAlchemy)
```

### 核心模組

| 模組 | 功能 | 技術 |
|------|------|------|
| **API 層** | RESTful API 端點，版本控制 | FastAPI + Uvicorn |
| **認證系統** | JWT 登入、邀請碼註冊、開發環境認證 | JWT + Bcrypt |
| **管理系統** | 使用者管理、邀請碼管理、系統管理 | FastAPI + SQLAlchemy |
| **通知設定** | 個人化通知偏好管理 | FastAPI + CRUD |
| **關鍵字管理** | 個人化關鍵字過濾、冪等操作 | FastAPI + CRUD |
| **資料層** | ORM 模型、CRUD 操作 | SQLAlchemy + SQLite/PostgreSQL |
| **錯誤處理** | 統一錯誤處理機制、異常管理 | FastAPI Exception Handler |
| **爬蟲系統** | AbleClub 網站監控 | Playwright + Selenium |
| **通知系統** | Email + Telegram 多管道 | SMTP + Bot API |
| **測試系統** | 單元測試、覆蓋率報告 | pytest + asyncio |

### 設計原則

- **關注點分離**: 各模組職責明確分工
- **依賴注入**: 使用 FastAPI 的依賴注入系統
- **配置管理**: 集中式環境變數管理
- **錯誤處理**: 統一的 API 錯誤回應格式
- **測試驅動**: 完整的單元測試覆蓋

## 🔧 功能使用指南

### API 服務

```bash
# 啟動 API 服務器（開發模式）
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# API 服務會在以下位址運行：
# - 主要 API: http://127.0.0.1:8000
# - API 文件: http://127.0.0.1:8000/docs
# - 替代文件: http://127.0.0.1:8000/redoc
```

### 認證 API

```bash
# 使用者註冊（需要邀請碼）
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login-or-register" \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password123", "inviteCode": "VALIDCODE"}'

# 使用者登入
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login-or-register" \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password123"}'

# 檢查使用者狀態
curl -X GET "http://127.0.0.1:8000/api/v1/users/check-status?username=user@example.com"

# 開發環境登入（僅限開發）
curl -X POST "http://127.0.0.1:8000/api/v1/dev/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "dev@example.com"}'
```

### 管理員 API

```bash
# 取得所有使用者列表（需管理員權限）
curl -X GET "http://127.0.0.1:8000/api/v1/admin/users" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 建立邀請碼（需管理員權限）
curl -X POST "http://127.0.0.1:8000/api/v1/admin/invitation-codes" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code": "NEWCODE", "expiry_days": 7}'
```

### 通知設定 API（Singleton Resource 設計）

這組 API 圍繞當前登入的使用者 (/me)，採納了「單例資源」設計模式。前端不需要關心 id，只需透過不同的 HTTP 方法操作 `/api/v1/me/notify-settings/` 這個唯一的路徑即可。

| HTTP 方法 | 路徑 | 功能 | 狀態碼 |
|-----------|------|------|--------|
| `GET` | `/api/v1/me/notify-settings/` | 查詢當前使用者的通知設定 | 200 OK / 404 Not Found |
| `POST` | `/api/v1/me/notify-settings/` | 建立當前使用者的通知設定 | 201 Created / 409 Conflict |
| `PUT` | `/api/v1/me/notify-settings/` | 更新當前使用者的通知設定 | 200 OK / 404 Not Found |
| `DELETE` | `/api/v1/me/notify-settings/` | 刪除當前使用者的通知設定 | 204 No Content / 404 Not Found |

```bash
# 建立通知設定（初次設定）
curl -X POST "http://127.0.0.1:8000/api/v1/me/notify-settings/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notify_type": "email",
    "email_address": "user@example.com",
    "keywords": ["Python", "FastAPI"]
  }'

# 查詢通知設定
curl -X GET "http://127.0.0.1:8000/api/v1/me/notify-settings/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 更新通知設定
curl -X PUT "http://127.0.0.1:8000/api/v1/me/notify-settings/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notify_type": "telegram",
    "email_address": null,
    "keywords": ["React", "Vue"]
  }'

# 刪除通知設定
curl -X DELETE "http://127.0.0.1:8000/api/v1/me/notify-settings/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**通知設定 API 特色**：
- 🔄 **Singleton Resource 模式**：每個使用者只能有一組通知設定
- ⚡ **簡化的路徑設計**：無需處理複雜的 ID 參數
- 🔗 **內建關鍵字整合**：設定中自動包含使用者的關鍵字列表
- 🛡️ **完整的錯誤處理**：支援 404, 409, 400 等標準 HTTP 狀態碼
- 📧 **條件式驗證**：Email 類型通知必須提供有效的 Email 地址

### 關鍵字管理 API

關鍵字管理功能讓使用者設定個人化的關鍵字列表，用於過濾和篩選通知內容。

```bash
# 取得個人關鍵字列表
curl -X GET "http://127.0.0.1:8000/api/v1/me/keywords/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 回應範例：["Python", "FastAPI", "React"]

# 更新關鍵字列表（完整替換）
curl -X PUT "http://127.0.0.1:8000/api/v1/me/keywords/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '["Python", "FastAPI", "Vue.js"]'

# 回應範例：["Python", "FastAPI", "Vue.js"]

# 清空所有關鍵字
curl -X PUT "http://127.0.0.1:8000/api/v1/me/keywords/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[]'

# 回應範例：[]
```

**關鍵字 API 特色**：
- 🔄 **完整替換語義**：PUT 操作會先刪除所有現有關鍵字，再設定新的列表
- ⚡ **冪等性設計**：重複執行相同請求不會產生副作用
- 🗃️ **簡潔格式**：直接使用字串陣列，無需複雜的 JSON 結構
- 🔗 **自動整合**：關鍵字會自動顯示在通知設定回應中
- 🚫 **支援清空**：傳送空陣列可清除所有關鍵字

### 通知功能

```bash
# 取得支援的通知管道
curl -X GET "http://127.0.0.1:8000/api/v1/notifications/channels"

# 測試 Email 通知
curl -X GET "http://127.0.0.1:8000/api/v1/notifications/test-email"

# 發送自訂通知
curl -X POST "http://127.0.0.1:8000/api/v1/notifications/send" \
  -H "Content-Type: application/json" \
  -d '{"message": "測試訊息", "channel": "email", "subject": "測試主旨"}'
```

### 網頁抓取功能

```bash
# 確保虛擬環境已激活
source .venv/bin/activate

# 執行抓取任務
python -m scraper.tasks
```

## 🌐 環境變數設定

在 `.env` 檔案中設定以下變數：

```bash
# 資料庫連線 (選擇其中一種)
# 本地開發 - SQLite
DATABASE_URL="sqlite:///./ableclub_monitor.db"

# 生產環境/雲端部署 - PostgreSQL (Neon)
# DATABASE_URL="postgresql://user:password@host:port/database?sslmode=require"

# JWT 認證設定
SECRET_KEY="your_very_secret_key_here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email 通知設定
EMAIL_DEBUG_MODE=false
EMAIL_USER="your_gmail@gmail.com"
EMAIL_PASSWORD="your_16_digit_app_password"
DEFAULT_NOTIFICATION_EMAIL="recipient@example.com"

# Telegram 通知設定
TELEGRAM_BOT_TOKEN="your_bot_token"
TELEGRAM_CHAT_ID="your_chat_id"
```

## 🧪 測試標準作業程序

本專案採用 Test-Driven Development (TDD) 方法，並使用 `pytest` 作為測試框架。

### 執行測試

```bash
# 確保虛擬環境已激活
source .venv/bin/activate

# 執行所有測試
pytest

# 執行特定測試檔案
pytest tests/test_auth_api.py

# 執行測試並顯示覆蓋率
pytest --cov=app

# 執行測試並顯示詳細資訊
pytest -v
```

### 測試覆蓋率

目前測試覆蓋率：**98%**

- 認證 API：100% 覆蓋
- 使用者管理：100% 覆蓋
- 核心功能：94% 覆蓋

## 📊 技術棧

- **後端框架**: FastAPI, Uvicorn
- **資料庫**: SQLAlchemy, SQLite (開發), PostgreSQL (生產)
- **網頁爬蟲**: Playwright, BeautifulSoup4
- **安全與認證**: Passlib (Bcrypt), Python-JOSE (JWT)
- **測試框架**: pytest, pytest-asyncio, HTTPX
- **容器化**: Docker

## 🐳 Docker 運行

```bash
# 建立 Docker 映像檔
docker build -t ableclub-monitor .

# 使用 Docker Compose 啟動
docker-compose up -d

# 查看容器狀態
docker-compose ps

# 停止服務
docker-compose down
```

---

**專案特色**：
- ✅ 完整的 JWT 認證系統
- ✅ 邀請碼註冊機制
- ✅ 多管道通知系統
- ✅ 個人化關鍵字管理
- ✅ 穩定的網頁爬蟲
- ✅ 高測試覆蓋率
- ✅ 完整的 API 文檔
- ✅ Docker 容器化支援

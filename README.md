# AbleClub Monitor

一個用於監控和抓取 AbleClub Taiwan 網站資訊的專案，包含完整的認證系統、通知功能和 Web API。

## 🚀 開發環境啟動指南

### 📋 首次設定

```bash
# 1. 建立虛擬環境（首次使用）
python3 -m venv .venv

# 2. 建立環境變數檔案
cp .env.example .env

# 3. 編輯 .env 檔案，設定必要的環境變數
# DATABASE_URL="sqlite:///./ableclub_monitor.db"
# EMAIL_USER="your_email@gmail.com"
# EMAIL_PASSWORD="your_app_password"
```

### ⚡ 開發環境啟動流程

每次開始開發時，請依序執行以下步驟：

```bash
# 1. 激活虛擬環境
source .venv/bin/activate

# 2. 安裝/更新依賴套件
pip install -r requirements.txt

# 3. 啟動 FastAPI 開發服務器
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 🔍 驗證啟動狀態

```bash
# 檢查 API 是否正常運行
curl http://127.0.0.1:8000/

# 預期回應：{"status":"ok","message":"Welcome to the AbleClub Monitor API!"}

# 查看 API 文件
# 瀏覽器開啟：http://127.0.0.1:8000/docs
```

### 🛑 開發環境結束流程

開發結束時，請執行以下步驟：

```bash
# 1. 停止 FastAPI 服務器
# 在運行 uvicorn 的終端按 Ctrl+C

# 2. 確認所有背景進程已停止
pkill -f uvicorn

# 3. 停用虛擬環境
deactivate
```

### 🔧 常用開發指令

```bash
# 檢查虛擬環境狀態
echo $VIRTUAL_ENV

# 查看已安裝的套件
pip list

# 更新 requirements.txt（安裝新套件後）
pip freeze > requirements.txt

# 檢查程式碼語法
python -m py_compile app/main.py

# 執行特定模組
python -m scraper.tasks

# 執行測試
pytest

# 執行特定測試檔案
pytest tests/test_auth_api.py

# 執行測試並顯示詳細資訊
pytest -v
```

### ⚠️ 重要提醒

- **開發前必做**：激活虛擬環境 `source .venv/bin/activate`
- **終端機指示**：激活後會顯示 `(.venv)` 前綴
- **環境變數**：確保 `.env` 檔案已正確設定
- **新套件安裝**：記得更新 `requirements.txt`
- **服務器狀態**：開發時保持 uvicorn 服務器運行

## 📁 專案結構

```
ableclub_monitor/
├── app/                           # 主要應用程式
│   ├── main.py                   # FastAPI 應用程式進入點
│   └── api/v1/                   # API 版本控制
│       ├── api.py               # API 路由統整
│       └── endpoints/           # 具體 API 端點實作
│           ├── auth.py         # 認證相關端點
│           ├── users.py        # 使用者管理端點
│           └── notifications.py # 通知相關端點
├── core/                         # 核心配置與工具
│   ├── config.py               # 環境變數與設定管理
│   └── security.py             # JWT 與密碼安全工具
├── database/                     # 資料庫相關
│   └── session.py              # SQLAlchemy 連線設定
├── models/                       # SQLAlchemy 資料模型
│   ├── user.py                 # 使用者資料模型
│   ├── event.py                # 事件資料模型
│   └── invitation_code.py      # 邀請碼資料模型
├── schemas/                      # Pydantic 資料驗證
│   ├── auth.py                 # 認證相關資料結構
│   └── notification.py         # 通知相關資料結構
├── crud/                         # 資料庫操作層
│   ├── user.py                 # 使用者 CRUD 操作
│   └── invitation_code.py      # 邀請碼 CRUD 操作
├── scraper/                      # 網頁抓取功能
│   └── tasks.py               # 爬蟲任務實作 (Playwright)
├── notifications/                # 通知系統
│   └── sender.py              # 多管道通知發送器
├── tests/                        # 測試套件
│   ├── conftest.py            # pytest 配置
│   ├── test_main.py           # 主程式測試
│   └── test_auth_api.py       # 認證 API 測試
├── logs/                         # 日誌檔案目錄
├── requirements.txt              # Python 依賴套件
├── pytest.ini                   # pytest 配置檔案
├── Dockerfile                    # Docker 容器設定
├── docker-compose.yml           # Docker 編排設定
├── CLAUDE.md                    # Claude Code 專案指引
└── README.md                    # 專案說明文件
```

## 🏗️ 架構設計

### 整體架構

此專案採用 **分層架構 (Layered Architecture)** 設計：

```
API 層 (FastAPI) → 業務邏輯層 (爬蟲/通知) → 資料存取層 (CRUD) → 資料模型層 (SQLAlchemy)
```

### 核心模組說明

| 模組 | 功能 | 技術 |
|------|------|------|
| **API 層** | RESTful API 端點，版本控制 | FastAPI + Uvicorn |
| **認證系統** | JWT 登入、邀請碼註冊 | JWT + Bcrypt |
| **資料層** | ORM 模型、CRUD 操作 | SQLAlchemy + SQLite |
| **爬蟲系統** | AbleClub 網站監控 | Playwright |
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
```

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
# 資料庫連線
DATABASE_URL="sqlite:///./ableclub_monitor.db"

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

### 後端框架
- **FastAPI**: 現代、高效能的 Python Web 框架
- **Uvicorn**: ASGI 伺服器，支援非同步處理

### 資料庫
- **SQLAlchemy**: Python ORM 框架
- **SQLite**: 開發環境預設資料庫 (可設定為 PostgreSQL/MySQL)

### 網頁爬蟲
- **Playwright**: 現代瀏覽器自動化工具
- **BeautifulSoup4**: HTML 解析備用方案

### 安全與認證
- **Passlib + Bcrypt**: 密碼雜湊
- **Python-JOSE**: JWT 令牌處理
- **Pydantic**: 資料驗證與序列化

### 通知系統
- **SMTP**: Email 發送 (支援 Gmail、Outlook 等)
- **Requests**: Telegram Bot API 整合

### 測試框架
- **pytest**: 主要測試框架
- **pytest-asyncio**: 非同步測試支援
- **pytest-mock**: Mock 功能
- **pytest-cov**: 覆蓋率報告
- **HTTPX**: 非同步 HTTP 客戶端測試

### 開發工具
- **Docker**: 容器化部署
- **python-dotenv**: 環境變數管理

## ⚠️ 開發注意事項

1. **虛擬環境**：每次開發前都要激活虛擬環境
2. **環境變數**：確保 `.env` 檔案正確設定
3. **依賴管理**：新增套件後要更新 `requirements.txt`
4. **測試覆蓋**：修改程式碼後要執行測試確保功能正常
5. **API 文檔**：新增 API 端點時要添加完整的文檔說明
6. **安全考量**：不要在程式碼中硬編碼敏感資訊
7. **程式碼風格**：遵循 Python PEP 8 編碼風格

## 🐳 Docker 部署

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
- ✅ 穩定的網頁爬蟲
- ✅ 高測試覆蓋率 (98%)
- ✅ 完整的 API 文檔
- ✅ Docker 容器化支援
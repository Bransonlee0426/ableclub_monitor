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
│   └── keyword.py              # 關鍵字資料模型
├── schemas/                      # Pydantic 資料驗證
│   ├── auth.py                 # 認證相關資料結構
│   ├── user.py                 # 使用者相關資料結構
│   ├── invitation_code.py      # 邀請碼資料結構
│   ├── notification.py         # 通知相關資料結構
│   ├── notify_setting.py       # 通知設定資料結構
│   ├── keyword.py              # 關鍵字相關資料結構
│   └── response.py             # 統一回應格式
├── crud/                         # 資料庫操作層
│   ├── user.py                 # 使用者 CRUD 操作
│   ├── invitation_code.py      # 邀請碼 CRUD 操作
│   ├── notify_setting.py       # 通知設定 CRUD 操作
│   └── keyword.py              # 關鍵字 CRUD 操作
├── scraper/                      # 網頁抓取功能
│   └── tasks.py               # 爬蟲任務實作 (Playwright)
├── notifications/                # 通知系統
│   └── sender.py              # 多管道通知發送器
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

### 通知設定 API

```bash
# 取得個人通知設定
curl -X GET "http://127.0.0.1:8000/api/v1/me/notify-settings" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 更新通知設定
curl -X PUT "http://127.0.0.1:8000/api/v1/me/notify-settings" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email_notifications": true, "telegram_notifications": false}'
```

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

### 後端框架
- **FastAPI**: 現代、高效能的 Python Web 框架
- **Uvicorn**: ASGI 伺服器，支援非同步處理

### 資料庫
- **SQLAlchemy**: Python ORM 框架
- **SQLite**: 開發環境預設資料庫
- **PostgreSQL**: 生產環境建議資料庫 (支援 Neon、AWS RDS 等)
- **psycopg2-binary**: PostgreSQL 資料庫驅動

### 網頁爬蟲
- **Playwright**: 現代瀏覽器自動化工具
- **Selenium**: 傳統瀏覽器自動化備選方案
- **BeautifulSoup4**: HTML 解析備用方案

### 安全與認證
- **Passlib + Bcrypt**: 密碼雜湊
- **Python-JOSE**: JWT 令牌處理
- **Pydantic**: 資料驗證與序列化

### 設定管理
- **Pydantic-Settings**: 設定管理和環境變數驗證
- **python-dotenv**: 環境變數載入

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

## ☁️ GCP Cloud Run 部署

本專案採用 **環境分離架構**，提供開發環境和生產環境的完全獨立部署。

### 🏗️ 部署架構

```
deploy/
├── deploy-dev.sh       # 開發環境部署腳本
├── deploy-prod.sh      # 生產環境部署腳本
├── env/
│   ├── dev.env        # 開發環境配置
│   └── prod.env       # 生產環境配置
└── README.md          # 詳細部署說明
```

### 🔄 環境差異

| 項目 | 開發環境 | 生產環境 |
|------|----------|----------|
| 專案ID | ableclub-monitor-dev | ableclub-monitor |
| 資料庫 | SQLite | PostgreSQL (Neon) |
| 記憶體 | 512Mi | 1Gi |
| CPU | 1 | 2 |
| 並發數 | 20 | 80 |
| 實例範圍 | 0-5 | 1-10 |
| Token 期限 | 30分鐘 | 24小時 |
| 日誌級別 | DEBUG | INFO |

### 前置準備

1. **安裝 Google Cloud CLI**：
   ```bash
   # macOS
   brew install --cask google-cloud-sdk
   
   # 登入 GCP
   gcloud auth login
   
   # 啟用必要的 API
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

### 🚀 快速部署

#### 開發環境部署
```bash
cd deploy
./deploy-dev.sh
```

#### 生產環境部署
```bash
cd deploy
./deploy-prod.sh
```

### 📋 部署特色

- 🔒 **自動生成安全的 SECRET_KEY**
- 🔍 **環境檢查**：自動檢測 gcloud CLI 和 Docker
- 🏗️ **自動建置 Docker 映像檔**
- ☁️ **上傳到 GCP Container Registry**
- 🚀 **部署到 Cloud Run（台灣區域）**
- ⚙️ **自動設定所有環境變數**
- 🌐 **允許未經驗證的存取**
- 🛡️ **錯誤處理和自動清理**
- ⚠️ **生產環境部署確認機制**

### 📊 部署後驗證

```bash
# 查看服務狀態
gcloud run services list --region=asia-east1

# 測試 API（開發環境）
curl https://ableclub-monitor-dev-asia-east1.a.run.app/

# 測試 API（生產環境）
curl https://ableclub-monitor-asia-east1.a.run.app/

# 查看日誌
gcloud run services logs tail ableclub-monitor --region=asia-east1
```

### 🔧 自訂配置

如需修改部署參數，請編輯對應的環境配置檔案：
- 開發環境：`deploy/env/dev.env`
- 生產環境：`deploy/env/prod.env`

詳細的部署說明請參考：[deploy/README.md](deploy/README.md)

---

**專案特色**：
- ✅ 完整的 JWT 認證系統
- ✅ 邀請碼註冊機制  
- ✅ 多管道通知系統
- ✅ 個人化關鍵字管理
- ✅ 穩定的網頁爬蟲
- ✅ 高測試覆蓋率 (98%)
- ✅ 完整的 API 文檔
- ✅ Docker 容器化支援
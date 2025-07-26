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

| 模組 | 功能 |
|------|------|
| **API 層** | 提供 RESTful API 端點，並進行版本控制。 |
| **認證系統** | 實現 JWT 登入、邀請碼註冊。 |
| **資料層** | 使用 SQLAlchemy ORM 進行資料庫操作。 |
| **爬蟲系統** | 監控 AbleClub 網站的更新。 |
| **通知系統** | 支援 Email 和 Telegram 等多管道通知。 |
| **測試系統** | 使用 pytest 進行完整的單元與整合測試。 |

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

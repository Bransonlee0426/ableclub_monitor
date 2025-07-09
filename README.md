# AbleClub Monitor

一個用於監控和抓取 AbleClub Taiwan 網站資訊的專案，包含 Email 通知功能。

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
├── app/                      # 主要應用程式
│   ├── __init__.py
│   └── main.py              # FastAPI 應用程式進入點
├── core/                    # 核心配置
│   ├── __init__.py
│   └── config.py           # 環境變數與設定管理
├── database/               # 資料庫相關
│   ├── __init__.py
│   └── session.py          # 資料庫連線設定
├── models/                 # 資料模型
│   ├── __init__.py
│   └── event.py           # 事件資料模型
├── notifications/          # 通知系統
│   ├── __init__.py
│   └── sender.py           # 通知發送邏輯
├── scraper/               # 網頁抓取功能
│   ├── __init__.py
│   └── tasks.py           # 抓取任務實作
├── .env.example           # 環境變數範例檔案
├── .env                   # 環境變數檔案（需自行建立）
├── requirements.txt       # Python 依賴套件
├── docker-compose.yml     # Docker 容器編排
├── Dockerfile            # Docker 映像檔設定
└── README.md             # 專案說明
```

## 🔧 功能使用指南

### API 服務

```bash
# 啟動 API 服務器（開發模式）
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# API 服務會在以下位址運行：
# - 主要 API: http://127.0.0.1:8000
# - API 文件: http://127.0.0.1:8000/docs
```

### 網頁抓取功能

```bash
# 確保虛擬環境已激活
source .venv/bin/activate

# 執行抓取任務
python -m scraper.tasks
```

### Email 通知功能測試

```bash
# 測試 API 健康狀態
curl http://127.0.0.1:8000/

# 測試 Email 通知
curl -X GET "http://127.0.0.1:8000/api/notifications/test-email"

# 發送自訂 Email 通知
curl -X POST "http://127.0.0.1:8000/api/notifications/sendEmail" \
  -H "Content-Type: application/json" \
  -d '{"message": "測試訊息", "subject": "測試主旨"}'
```

## 🌐 Email 通知設定

### 環境變數設定

在 `.env` 檔案中設定以下變數：

```bash
# 資料庫連線
DATABASE_URL="sqlite:///./ableclub_monitor.db"

# Email 通知設定
EMAIL_USER="your_gmail@gmail.com"
EMAIL_PASSWORD="your_16_digit_app_password"
DEFAULT_NOTIFICATION_EMAIL="recipient@example.com"
EMAIL_DEBUG_MODE=false
```

## ⚠️ 開發注意事項

1. **虛擬環境**：每次開發前都要激活虛擬環境
2. **環境變數**：確保 `.env` 檔案正確設定
3. **依賴管理**：新增套件後要更新 `requirements.txt`
4. **服務器狀態**：開發時保持 FastAPI 服務器運行
5. **代碼提交**：提交前確保代碼能在虛擬環境中正常運行

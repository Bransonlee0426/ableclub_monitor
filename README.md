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

## 🧪 測試標準作業程序 (SOP)

本專案採用 Test-Driven Development (TDD) 方法，並使用 `pytest` 作為測試框架。遵循此 SOP 能確保程式碼品質與功能的正確性。

### 1. 執行完整測試

在進行任何程式碼修改前後，都應執行完整的單元測試。

```bash
# 確保虛擬環境已激活
source .venv/bin/activate

# 執行 pytest
pytest
```

### 2. 解讀測試結果

`pytest` 的輸出會包含以下幾個關鍵部分：

- **測試進度**：`[  6%] [ 13%] ... [100%]` 顯示測試執行進度。
- **測試結果**：每個測試後面會標示 `PASSED` (通過), `FAILED` (失敗), 或 `SKIPPED` (跳過)。
- **失敗詳情 (`FAILURES`)**：這是最重要的部分。它會詳細列出每個失敗測試的：
    - **失敗點**：用 `>` 標示出在哪一行程式碼發生錯誤。
    - **錯誤類型**：例如 `AssertionError` (斷言失敗) 或 `AttributeError` (屬性錯誤)。
    - **錯誤訊息**：提供詳細的錯誤原因，例如 `assert 200 == 401`。
- **警告摘要 (`warnings summary`)**：列出程式碼中使用了過時語法或存在潛在問題的地方。警告不會導致測試失敗，但建議修復。
- **總結 (`short test summary info`)**：在結尾提供一個簡潔的統計，例如 `1 failed, 14 passed, 8 warnings`。

### 3. 測試修復流程

當測試出現 `FAILED` 或 `warnings` 時，請依照以下流程進行修復：

#### 第一階段：修復 `FAILED` 的測試

1.  **優先處理 `AttributeError` 或 `ImportError`**：
    *   **原因**：這類錯誤通常表示測試中的 Mock 路徑不正確，或是模組的 import 結構有問題。它們會導致大量測試無法正常執行。
    *   **解法**：仔細檢查 `mocker.patch("path.to.your.function")` 的路徑是否與被測試模組中實際 import 和使用的名稱一致。例如，如果 `auth.py` 中是 `from crud import user as crud_user`，那麼 Mock 路徑就應該是 `...auth.crud_user.some_function`。

2.  **處理 `AssertionError`**：
    *   **原因**：這表示 API 的實際行為與測試案例的預期結果不符。
    *   **解法**：
        1.  **檢查 API 邏輯**：回到對應的端點函式 (例如 `app/api/v1/endpoints/auth.py`)，檢查業務邏輯是否正確實作。是否在正確的條件下回傳了正確的狀態碼和回應內容？
        2.  **檢查測試斷言**：確認測試案例中的預期結果 (`assert response.status_code == ...` 和 `assert response.json() == ...`) 是否寫錯了。有時候是 API 的行為正確，但測試的預期是錯誤的。

3.  **反覆測試**：每修復一個問題，就重新執行一次 `pytest`，確保修復沒有引入新的問題，並逐步減少失敗的測試數量。

#### 第二階段：處理 `warnings`

當所有測試都 `PASSED` 後，開始處理警告。

1.  **識別警告來源**：仔細閱讀警告訊息，它會指出是哪個檔案、哪一行程式碼、以及是什麼原因（例如使用了被棄用的函式或參數）。
2.  **修復專案內的警告**：
    *   **SQLAlchemy `declarative_base`**：將 `from sqlalchemy.ext.declarative import declarative_base` 改為 `from sqlalchemy.orm import declarative_base`。
    *   **Pydantic `regex`**：在 `Query` 或 `Field` 中，將 `regex=` 參數改為 `pattern=`。
    *   **Pydantic `.dict()`**：將 Pydantic 模型的 `.dict()` 方法改為 `.model_dump()`。
3.  **忽略第三方套件的警告**：如果警告來源於 `.venv/lib/site-packages/` 下的檔案，這表示它是第三方套件內部的問題。我們無法也不應該修改它，可以安全地忽略，等待套件作者在未來版本中修復。

### 4. 最終驗證

當 `pytest` 的最終結果顯示 **`... passed ...`** 且沒有任何可以由我們修復的警告時，代表測試流程已完成，程式碼已達到可交付狀態。

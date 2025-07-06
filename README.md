# AbleClub Monitor

一個用於監控和抓取 AbleClub Taiwan 網站資訊的專案。

## 開發環境設定

### 虛擬環境管理

本專案使用 Python 虛擬環境來管理依賴套件。

#### 首次設定（如果還沒有虛擬環境）
```bash
# 建立虛擬環境
python3 -m venv .venv
```

#### 開始開發時
```bash
# 激活虛擬環境
source .venv/bin/activate

# 安裝依賴套件
pip install -r requirements.txt
```

#### 結束開發時
```bash
# 停用虛擬環境
deactivate
```

#### 重要提醒
- **開始開發前**：務必先激活虛擬環境 `source .venv/bin/activate`
- **安裝新套件後**：記得更新 `requirements.txt`
  ```bash
  pip freeze > requirements.txt
  ```
- **終端機提示符**：激活虛擬環境後，終端機會顯示 `(.venv)` 前綴
- **檢查虛擬環境**：可用 `echo $VIRTUAL_ENV` 確認是否已激活

## 專案結構

```
ableclub_monitor/
├── app/                 # 主要應用程式
├── core/               # 核心配置
├── database/           # 資料庫相關
├── models/             # 資料模型
├── notifications/      # 通知系統
├── scraper/            # 網頁抓取功能
├── requirements.txt    # Python 依賴套件
└── README.md          # 專案說明
```

## 使用方式

### 執行網頁抓取
```bash
# 確保虛擬環境已激活
source .venv/bin/activate

# 執行抓取任務
python scraper/tasks.py
```

## 開發注意事項

1. **虛擬環境**：每次開發前都要激活虛擬環境
2. **依賴管理**：新增套件後要更新 requirements.txt
3. **代碼提交**：提交前確保代碼能在虛擬環境中正常運行

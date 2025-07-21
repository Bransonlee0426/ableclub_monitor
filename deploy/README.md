# 內部部署指南 (Internal Deployment Guide)

**警告：此文件包含敏感的基礎架構資訊，已被加入 `.gitignore`，嚴禁提交至版本控制系統。**

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
└── README.md          # 詳細部署說明 (本文件)
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

# 部署架構說明

這個目錄包含了 AbleClub Monitor 的完整部署架構，實現了開發環境和生產環境的完全分離。

## 📁 目錄結構

```
deploy/
├── README.md           # 部署說明文檔
├── deploy-dev.sh       # 開發環境部署腳本
├── deploy-prod.sh      # 生產環境部署腳本
├── env/
│   ├── dev.env        # 開發環境配置
│   └── prod.env       # 生產環境配置
└── config/            # 未來擴展的配置檔案
```

## 🏗️ 環境架構

### 開發環境 (Development)
- **專案ID**: `ableclub-monitor-dev`
- **資料庫**: SQLite (本地檔案)
- **資源**: 512Mi RAM, 1 CPU
- **並發**: 20
- **實例**: 0-5 個
- **特色**: Debug 模式、CORS 啟用、Email Debug

### 生產環境 (Production)
- **專案ID**: `ableclub-monitor`
- **資料庫**: PostgreSQL (Neon)
- **資源**: 1Gi RAM, 2 CPU
- **並發**: 80
- **實例**: 1-10 個
- **特色**: 高可用性、24小時 Token、安全配置

## 🚀 部署指令

### 開發環境部署
```bash
# 在專案根目錄執行
cd deploy
./deploy-dev.sh
```

### 生產環境部署
```bash
# 在專案根目錄執行
cd deploy
./deploy-prod.sh
```

## ⚙️ 配置說明

### 環境變數檔案
- `env/dev.env`: 開發環境的所有配置參數
- `env/prod.env`: 生產環境的所有配置參數

### 主要差異

| 項目 | 開發環境 | 生產環境 |
|------|----------|----------|
| 專案ID | ableclub-monitor-dev | ableclub-monitor |
| 資料庫 | SQLite | PostgreSQL |
| 記憶體 | 512Mi | 1Gi |
| CPU | 1 | 2 |
| 並發數 | 20 | 80 |
| 實例範圍 | 0-5 | 1-10 |
| Token 期限 | 30分鐘 | 24小時 |
| 日誌級別 | DEBUG | INFO |
| CORS | 啟用 | 停用 |
| Email Debug | 啟用 | 停用 |

## 🔒 安全考量

### 開發環境
- 使用較短的 Token 有效期
- 啟用 Debug 模式便於開發
- 較低的資源限制

### 生產環境
- 部署前需要確認提示
- 檢查 GCP 登入狀態
- 驗證資料庫連線格式
- 較長的 Token 有效期
- 嚴格的資源配置

## 📊 監控指令

### 查看服務狀態
```bash
# 開發環境
gcloud run services describe ableclub-monitor-dev --region=asia-east1

# 生產環境
gcloud run services describe ableclub-monitor --region=asia-east1
```

### 查看服務日誌
```bash
# 開發環境
gcloud run services logs tail ableclub-monitor-dev --region=asia-east1

# 生產環境
gcloud run services logs tail ableclub-monitor --region=asia-east1
```

### 列出所有服務
```bash
gcloud run services list --region=asia-east1
```

## 🔄 更新部署

只需重新執行對應的部署腳本即可：

```bash
# 更新開發環境
./deploy-dev.sh

# 更新生產環境
./deploy-prod.sh
```

## ⚠️ 注意事項

1. **環境隔離**: 開發和生產環境完全獨立，不會互相影響
2. **配置管理**: 所有環境差異都在配置檔案中明確定義
3. **安全性**: 生產環境部署有額外的確認步驟
4. **可擴展性**: 未來可以輕鬆添加更多環境（如測試環境）

## 🆘 故障排除

### 常見問題

1. **部署失敗**: 檢查 GCP 登入狀態和專案權限
2. **映像檔建置失敗**: 確認 Docker 運行正常
3. **環境變數錯誤**: 檢查對應的 `.env` 檔案
4. **資料庫連線失敗**: 驗證資料庫連線字串

### 重置環境
```bash
# 刪除服務（小心使用）
gcloud run services delete ableclub-monitor-dev --region=asia-east1
gcloud run services delete ableclub-monitor --region=asia-east1
```
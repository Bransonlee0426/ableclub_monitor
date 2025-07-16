#!/bin/bash

# AbleClub Monitor 生產環境部署腳本
# Production Environment Deployment Script

set -e  # 遇到錯誤就停止執行

# 載入生產環境配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/env/prod.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "錯誤: 找不到生產環境配置檔案 $ENV_FILE"
    exit 1
fi

# 載入環境變數
source "$ENV_FILE"

# 顯示當前配置
echo "=========================================="
echo "  AbleClub Monitor 生產環境部署"
echo "=========================================="
echo "專案ID: $PROJECT_ID"
echo "應用名稱: $APP_NAME"
echo "區域: $REGION"
echo "資料庫: PostgreSQL (Neon)"
echo "資源: $MEMORY RAM, $CPU CPU"
echo "並發: $CONCURRENCY"
echo "實例範圍: $MIN_INSTANCES - $MAX_INSTANCES"
echo "=========================================="

# 確認生產環境部署
confirm_production_deploy() {
    echo ""
    echo "⚠️  警告: 即將部署到生產環境"
    echo "這將影響正在運行的服務，請確認："
    echo "1. 所有測試都已通過"
    echo "2. 程式碼已經過審查"
    echo "3. 資料庫備份已完成"
    echo ""
    
    # 檢查是否在 CI/CD 環境中（GitHub Actions）
    if [ "$CI" = "true" ] || [ -n "$GITHUB_ACTIONS" ]; then
        echo "🤖 在 CI/CD 環境中執行，自動確認部署"
        return 0
    fi
    
    # 在本地環境中要求用戶確認
    read -p "確定要繼續生產環境部署嗎？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "部署已取消"
        exit 0
    fi
}

# 生成 SECRET_KEY 函數
generate_secret_key() {
    echo "生成生產環境 SECRET_KEY..."
    if command -v openssl &> /dev/null; then
        SECRET_KEY=$(openssl rand -hex 32)
        echo "已生成高強度 SECRET_KEY (64 字符)"
    else
        SECRET_KEY=$(head -c 32 /dev/urandom | base64 | tr -d "=+/" | cut -c1-64)
        echo "已生成 SECRET_KEY (使用 /dev/urandom)"
    fi
}

# 檢查必要的環境變數
check_env_vars() {
    echo "檢查生產環境變數..."
    
    if [ -z "$SECRET_KEY" ]; then
        generate_secret_key
    fi
    
    if [ -z "$PROJECT_ID" ]; then
        echo "錯誤: PROJECT_ID 未設定！"
        exit 1
    fi
    
    if [ -z "$DATABASE_URL" ]; then
        echo "錯誤: DATABASE_URL 未設定！"
        exit 1
    fi
    
    # 驗證資料庫連線字串格式
    if [[ ! $DATABASE_URL =~ ^postgresql:// ]]; then
        echo "錯誤: 生產環境必須使用 PostgreSQL 資料庫"
        exit 1
    fi
    
    echo "生產環境變數檢查完成"
}

# 檢查 gcloud CLI
check_gcloud() {
    echo "檢查 gcloud CLI..."
    if ! command -v gcloud &> /dev/null; then
        echo "錯誤: gcloud CLI 未安裝"
        echo "請先安裝 Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    # 檢查是否已登入
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        echo "錯誤: 請先登入 GCP"
        echo "執行: gcloud auth login"
        exit 1
    fi
    
    echo "gcloud CLI 已安裝並已登入"
}

# 檢查 Docker
check_docker() {
    echo "檢查 Docker..."
    if ! command -v docker &> /dev/null; then
        echo "錯誤: Docker 未安裝"
        echo "請先安裝 Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    echo "Docker 已安裝"
}

# 建置前檢查
pre_build_check() {
    echo "執行建置前檢查..."
    
    # 檢查是否在專案根目錄
    if [ ! -f "../Dockerfile" ]; then
        echo "錯誤: 請在專案根目錄執行此腳本"
        exit 1
    fi
    
    # 檢查必要檔案
    if [ ! -f "../requirements.txt" ]; then
        echo "錯誤: 找不到 requirements.txt"
        exit 1
    fi
    
    if [ ! -f "../app/main.py" ]; then
        echo "錯誤: 找不到 app/main.py"
        exit 1
    fi
    
    echo "建置前檢查完成"
}

# 主要部署函數
deploy_to_cloud_run() {
    echo "步驟 1: 設定 GCP 專案"
    gcloud config set project $PROJECT_ID
    
    echo "步驟 2: 啟用必要的 API"
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    
    echo "步驟 3: 建置並上傳 Docker 映像檔"
    IMAGE_URI="gcr.io/${PROJECT_ID}/${APP_NAME}"
    
    # 切換到專案根目錄進行建置
    cd ..
    gcloud builds submit --tag $IMAGE_URI --project $PROJECT_ID .
    cd deploy
    
    if [ $? -ne 0 ]; then
        echo "錯誤: Docker 映像檔建置失敗"
        exit 1
    fi
    
    echo "步驟 4: 部署到 Cloud Run（生產環境）"
    gcloud run deploy $APP_NAME \
      --image $IMAGE_URI \
      --platform managed \
      --region $REGION \
      --allow-unauthenticated \
      --set-env-vars="DATABASE_URL=$DATABASE_URL,SECRET_KEY=$SECRET_KEY,ALGORITHM=$ALGORITHM,EMAIL_USER=$EMAIL_USER,EMAIL_PASSWORD=$EMAIL_PASSWORD,DEFAULT_NOTIFICATION_EMAIL=$DEFAULT_NOTIFICATION_EMAIL,EMAIL_DEBUG_MODE=$EMAIL_DEBUG_MODE,LOG_LEVEL=$LOG_LEVEL,ENABLE_CORS=$ENABLE_CORS,ACCESS_TOKEN_EXPIRE_MINUTES=$ACCESS_TOKEN_EXPIRE_MINUTES" \
      --memory $MEMORY \
      --cpu $CPU \
      --concurrency $CONCURRENCY \
      --timeout $TIMEOUT \
      --max-instances $MAX_INSTANCES \
      --min-instances $MIN_INSTANCES \
      --cpu-throttling \
      --project $PROJECT_ID
    
    if [ $? -ne 0 ]; then
        echo "錯誤: Cloud Run 部署失敗"
        exit 1
    fi
    
    echo "=========================================="
    echo "  生產環境部署完成！"
    echo "=========================================="
    echo "服務 URL: https://$APP_NAME-$REGION.a.run.app"
    echo "API 文檔: https://$APP_NAME-$REGION.a.run.app/docs"
    echo ""
    echo "生產環境特色："
    echo "- ✅ 使用 PostgreSQL 資料庫"
    echo "- ✅ 高可用性配置"
    echo "- ✅ INFO 日誌級別"
    echo "- ✅ 生產級資源配置"
    echo "- ✅ 24小時 Token 有效期"
    echo ""
    echo "監控指令："
    echo "查看日誌: gcloud run services logs tail $APP_NAME --region=$REGION"
    echo "查看狀態: gcloud run services describe $APP_NAME --region=$REGION"
}

# 清理函數
cleanup() {
    echo "清理暫存檔案..."
    # 關閉 set -e 避免清理階段的錯誤中斷腳本
    set +e
    docker system prune -f 2>/dev/null
    # 確保清理函數總是成功退出
    exit 0
}

# 主要執行流程
main() {
    trap cleanup EXIT
    
    echo "開始生產環境部署流程..."
    
    # 確認生產環境部署
    confirm_production_deploy
    
    # 執行所有檢查
    check_env_vars
    check_gcloud
    check_docker
    pre_build_check
    
    # 執行部署
    deploy_to_cloud_run
    
    echo "生產環境部署流程完成！"
}

# 執行主函數
main "$@"
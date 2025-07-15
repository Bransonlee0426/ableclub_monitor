#!/bin/bash

# AbleClub Monitor 開發環境部署腳本
# Development Environment Deployment Script

set -e  # 遇到錯誤就停止執行

# 載入開發環境配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/env/dev.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "錯誤: 找不到開發環境配置檔案 $ENV_FILE"
    exit 1
fi

# 載入環境變數
source "$ENV_FILE"

# 顯示當前配置
echo "=========================================="
echo "  AbleClub Monitor 開發環境部署"
echo "=========================================="
echo "專案ID: $PROJECT_ID"
echo "應用名稱: $APP_NAME"
echo "區域: $REGION"
echo "資料庫: 使用 SQLite（開發環境）"
echo "資源: $MEMORY RAM, $CPU CPU"
echo "=========================================="

# 生成 SECRET_KEY 函數
generate_secret_key() {
    echo "生成開發環境 SECRET_KEY..."
    if command -v openssl &> /dev/null; then
        SECRET_KEY=$(openssl rand -hex 32)
        echo "已生成 SECRET_KEY (64 字符)"
    else
        SECRET_KEY=$(head -c 32 /dev/urandom | base64 | tr -d "=+/" | cut -c1-64)
        echo "已生成 SECRET_KEY (使用 /dev/urandom)"
    fi
}

# 檢查必要的環境變數
check_env_vars() {
    echo "檢查開發環境變數..."
    
    if [ -z "$SECRET_KEY" ]; then
        generate_secret_key
    fi
    
    if [ -z "$PROJECT_ID" ]; then
        echo "錯誤: PROJECT_ID 未設定！"
        exit 1
    fi
    
    echo "開發環境變數檢查完成"
}

# 檢查 gcloud CLI
check_gcloud() {
    echo "檢查 gcloud CLI..."
    if ! command -v gcloud &> /dev/null; then
        echo "錯誤: gcloud CLI 未安裝"
        echo "請先安裝 Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    echo "gcloud CLI 已安裝"
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
    
    echo "步驟 4: 部署到 Cloud Run（開發環境）"
    gcloud run deploy $APP_NAME \
      --image $IMAGE_URI \
      --platform managed \
      --region $REGION \
      --allow-unauthenticated \
      --set-env-vars="DATABASE_URL=$DATABASE_URL,SECRET_KEY=$SECRET_KEY,ALGORITHM=$ALGORITHM,EMAIL_USER=$EMAIL_USER,EMAIL_PASSWORD=$EMAIL_PASSWORD,DEFAULT_NOTIFICATION_EMAIL=$DEFAULT_NOTIFICATION_EMAIL,EMAIL_DEBUG_MODE=$EMAIL_DEBUG_MODE,LOG_LEVEL=$LOG_LEVEL,ENABLE_CORS=$ENABLE_CORS" \
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
    echo "  開發環境部署完成！"
    echo "=========================================="
    echo "服務 URL: https://$APP_NAME-$REGION.a.run.app"
    echo "API 文檔: https://$APP_NAME-$REGION.a.run.app/docs"
    echo ""
    echo "開發環境特色："
    echo "- ✅ 使用 SQLite 資料庫"
    echo "- ✅ 啟用 CORS 支援"
    echo "- ✅ DEBUG 日誌級別"
    echo "- ✅ Email Debug 模式"
    echo "- ✅ 較低的資源配置"
}

# 清理函數
cleanup() {
    echo "清理暫存檔案..."
    docker system prune -f 2>/dev/null || true
}

# 主要執行流程
main() {
    trap cleanup EXIT
    
    echo "開始開發環境部署流程..."
    
    # 執行所有檢查
    check_env_vars
    check_gcloud
    check_docker
    
    # 執行部署
    deploy_to_cloud_run
    
    echo "開發環境部署流程完成！"
}

# 執行主函數
main "$@"
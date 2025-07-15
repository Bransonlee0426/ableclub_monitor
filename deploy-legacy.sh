#!/bin/bash

# AbleClub Monitor 部署指令腳本
# 此腳本包含所有部署到 GCP Cloud Run 的必要指令

# 設定變數 (請根據您的專案修改)
PROJECT_ID="ableclub-monitor"
APP_NAME="ableclub-monitor"
REGION="asia-east1"
IMAGE_URI="gcr.io/${PROJECT_ID}/${APP_NAME}"

# 環境變數設定 (請修改為您的實際值)
DATABASE_URL="${DATABASE_URL:-postgresql://neondb_owner:npg_RQj3U7zuHoOS@ep-soft-forest-a1htqaql-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require}"
SECRET_KEY="${SECRET_KEY:-}"
ALGORITHM="${ALGORITHM:-HS256}"
EMAIL_USER="${EMAIL_USER:-bransonlee0426@gmail.com}"
EMAIL_PASSWORD="${EMAIL_PASSWORD:-ebvnpqhnwlkykrrh}"
DEFAULT_NOTIFICATION_EMAIL="${DEFAULT_NOTIFICATION_EMAIL:-xebiva9350@axcradio.com}"

# 生成 SECRET_KEY 函數
generate_secret_key() {
    echo "生成 SECRET_KEY..."
    # 使用 openssl 生成隨機的 64 位十六進制字串
    if command -v openssl &> /dev/null; then
        SECRET_KEY=$(openssl rand -hex 32)
        echo "已生成 SECRET_KEY (64 字符)"
    else
        # 如果沒有 openssl，使用 /dev/urandom
        SECRET_KEY=$(head -c 32 /dev/urandom | base64 | tr -d "=+/" | cut -c1-64)
        echo "已生成 SECRET_KEY (使用 /dev/urandom)"
    fi
}

# 檢查必要的環境變數
check_env_vars() {
    echo "檢查環境變數..."
    
    # 如果 SECRET_KEY 未設定，自動生成
    if [ -z "$SECRET_KEY" ]; then
        generate_secret_key
    fi
    
    if [ -z "$DATABASE_URL" ]; then
        echo "錯誤: DATABASE_URL 未設定！"
        exit 1
    fi
    
    echo "環境變數檢查完成"
}

# 檢查 gcloud CLI 是否已安裝
check_gcloud() {
    echo "檢查 gcloud CLI..."
    if ! command -v gcloud &> /dev/null; then
        echo "錯誤: gcloud CLI 未安裝"
        echo "請先安裝 Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    echo "gcloud CLI 已安裝"
}

# 檢查 Docker 是否已安裝
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
    echo "=========================================="
    echo "  AbleClub Monitor 部署到 GCP Cloud Run"
    echo "=========================================="
    
    echo "步驟 1: 設定 GCP 專案"
    gcloud config set project $PROJECT_ID
    
    echo "步驟 2: 啟用必要的 API"
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    
    echo "步驟 3: 建置並上傳 Docker 映像檔到 Container Registry"
    echo "這個步驟會讀取 Dockerfile 並建置映像檔，然後上傳到 GCP Container Registry"
    gcloud builds submit --tag $IMAGE_URI
    
    if [ $? -ne 0 ]; then
        echo "錯誤: Docker 映像檔建置失敗"
        exit 1
    fi
    
    echo "步驟 4: 部署服務到 Cloud Run"
    echo "部署 FastAPI 應用程式，並設定所有必要的環境變數"
    gcloud run deploy $APP_NAME \
      --image $IMAGE_URI \
      --platform managed \
      --region $REGION \
      --allow-unauthenticated \
      --set-env-vars="DATABASE_URL=$DATABASE_URL,SECRET_KEY=$SECRET_KEY,ALGORITHM=$ALGORITHM,EMAIL_USER=$EMAIL_USER,EMAIL_PASSWORD=$EMAIL_PASSWORD,DEFAULT_NOTIFICATION_EMAIL=$DEFAULT_NOTIFICATION_EMAIL" \
      --memory 1Gi \
      --cpu 2 \
      --concurrency 80 \
      --timeout 900 \
      --max-instances 10 \
      --min-instances 0 \
      --cpu-throttling
    
    if [ $? -ne 0 ]; then
        echo "錯誤: Cloud Run 部署失敗"
        exit 1
    fi
    
    echo "=========================================="
    echo "  部署完成！"
    echo "=========================================="
    echo "您的應用程式現在已部署到 Cloud Run"
    echo "URL: https://$APP_NAME-$REGION.a.run.app"
    echo ""
    echo "注意事項："
    echo "1. 請確保您已經安裝並設定了 gcloud CLI"
    echo "2. 請將 PROJECT_ID 和 SECRET_KEY 替換為您的實際值"
    echo "3. 如需更新環境變數，請修改此腳本並重新執行"
    echo "4. 如需查看服務狀態，請使用: gcloud run services list"
}

# 清理函數
cleanup() {
    echo "清理暫存檔案..."
    # 清理 Docker 相關的暫存檔案
    docker system prune -f 2>/dev/null || true
}

# 主要執行流程
main() {
    # 設定錯誤處理
    set -e
    trap cleanup EXIT
    
    echo "開始部署流程..."
    
    # 執行所有檢查
    check_env_vars
    check_gcloud
    check_docker
    
    # 執行部署
    deploy_to_cloud_run
    
    echo "部署流程完成！"
}

# 執行主函數
main "$@"
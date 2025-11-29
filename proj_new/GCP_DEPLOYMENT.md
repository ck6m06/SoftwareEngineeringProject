# GCP 部署指南

本指南說明如何將專案部署到 Google Cloud Platform (GCP)。

## 📋 目錄

1. [架構概覽](#架構概覽)
2. [準備工作](#準備工作)
3. [部署選項](#部署選項)
4. [詳細部署步驟](#詳細部署步驟)
5. [環境變數配置](#環境變數配置)
6. [安全性建議](#安全性建議)
7. [監控與維護](#監控與維護)

---

## 架構概覽

### 推薦架構 (生產環境)

```
┌─────────────────────────────────────────────────────┐
│                   Cloud Load Balancer                │
│                   (HTTPS/SSL Termination)            │
└──────────────────┬────────────────┬─────────────────┘
                   │                │
         ┌─────────▼────────┐  ┌───▼──────────────┐
         │   Cloud Storage   │  │   Cloud Run      │
         │   + Cloud CDN     │  │   (Backend API)  │
         │   (Frontend)      │  └───┬──────────────┘
         └───────────────────┘      │
                                    │
         ┌──────────────────────────┼──────────────────┐
         │                          │                  │
    ┌────▼────┐         ┌──────────▼─────┐   ┌───────▼────────┐
    │Cloud SQL│         │  Memorystore   │   │ Cloud Storage  │
    │ (MySQL) │         │    (Redis)     │   │   (Images)     │
    └─────────┘         └────────────────┘   └────────────────┘
         │
    ┌────▼─────────┐
    │ Secret Manager│
    │  (Secrets)    │
    └───────────────┘
```

### 替代架構 (使用 GCE + Docker Compose)

如果使用 `docker-compose-gcp.yml`，架構如下：

```
┌─────────────────────────────────────────────────────┐
│                   Cloud Load Balancer                │
│                   (HTTPS/SSL Termination)            │
└──────────────────┬─────────────────────────────────┘
                   │
         ┌─────────▼────────────┐
         │  Compute Engine VM   │
         │  (運行 Docker Compose)│
         │                      │
         │  ┌──────────────┐   │
         │  │   Frontend   │   │
         │  ├──────────────┤   │
         │  │   Backend    │   │
         │  ├──────────────┤   │
         │  │Celery Worker │   │
         │  ├──────────────┤   │
         │  │    MySQL     │───┼───► Cloud SQL (可選)
         │  ├──────────────┤   │
         │  │    Redis     │───┼───► Memorystore (可選)
         │  ├──────────────┤   │
         │  │    MinIO     │───┼───► Cloud Storage (可選)
         │  └──────────────┘   │
         └──────────────────────┘
```

---

## 準備工作

### 1. GCP 專案設定

```bash
# 設定專案 ID
export PROJECT_ID=your-project-id
export REGION=asia-east1

# 登入 GCP
gcloud auth login

# 設定預設專案
gcloud config set project $PROJECT_ID

# 啟用必要的 API
gcloud services enable \
  compute.googleapis.com \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  storage.googleapis.com \
  secretmanager.googleapis.com \
  cloudresourcemanager.googleapis.com
```

### 2. 安裝必要工具

- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

---

## 部署選項

### 選項 A: Cloud Run + 託管服務 (推薦)

**優點:**
- 自動擴展
- 按使用量付費
- 無需管理基礎設施
- 高可用性

**適合:**
- 流量波動大的應用
- 團隊規模小
- 希望降低運維成本

### 選項 B: Compute Engine + Docker Compose

**優點:**
- 完全控制
- 可使用 docker-compose-gcp.yml
- 適合測試環境

**適合:**
- 需要完全控制環境
- 有專職運維團隊
- 流量相對穩定

### 選項 C: Google Kubernetes Engine (GKE)

**優點:**
- 高度可擴展
- 適合微服務架構
- 企業級功能

**適合:**
- 大型應用
- 需要複雜的部署策略
- 多環境管理

---

## 詳細部署步驟

### 選項 A: Cloud Run + 託管服務

#### 1. 建立 Cloud SQL (MySQL)

```bash
# 建立 Cloud SQL 實例
gcloud sql instances create pet-adoption-db \
  --database-version=MYSQL_8_0 \
  --tier=db-f1-micro \
  --region=$REGION \
  --root-password=YOUR_STRONG_PASSWORD \
  --storage-type=SSD \
  --storage-size=10GB

# 建立資料庫
gcloud sql databases create pet_adoption \
  --instance=pet-adoption-db

# 建立資料庫使用者
gcloud sql users create dbuser \
  --instance=pet-adoption-db \
  --password=YOUR_DB_PASSWORD
```

#### 2. 建立 Memorystore (Redis)

```bash
# 建立 Redis 實例
gcloud redis instances create pet-adoption-redis \
  --size=1 \
  --region=$REGION \
  --redis-version=redis_7_0
```

#### 3. 建立 Cloud Storage Bucket

```bash
# 建立 Bucket
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://pet-adoption-images

# 設定 CORS
cat > cors.json <<EOF
[
  {
    "origin": ["https://your-domain.com"],
    "method": ["GET", "POST", "PUT", "DELETE"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
EOF

gsutil cors set cors.json gs://pet-adoption-images

# 設定公開讀取 (如需要)
gsutil iam ch allUsers:objectViewer gs://pet-adoption-images
```

#### 4. 設定 Secret Manager

```bash
# 建立 secrets
echo -n "your-secret-key" | gcloud secrets create SECRET_KEY --data-file=-
echo -n "your-jwt-secret" | gcloud secrets create JWT_SECRET_KEY --data-file=-
echo -n "your-db-password" | gcloud secrets create DB_PASSWORD --data-file=-
echo -n "your-smtp-password" | gcloud secrets create SMTP_PASSWORD --data-file=-

# 授予 Cloud Run 存取權限
gcloud secrets add-iam-policy-binding SECRET_KEY \
  --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

#### 5. 部署後端到 Cloud Run

```bash
# 建立 Dockerfile.cloudrun (如需要)
cd backend

# 使用 Cloud Build 建構映像
gcloud builds submit --tag gcr.io/$PROJECT_ID/pet-adoption-backend

# 部署到 Cloud Run
gcloud run deploy pet-adoption-backend \
  --image gcr.io/$PROJECT_ID/pet-adoption-backend \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="FLASK_ENV=production" \
  --set-secrets="SECRET_KEY=SECRET_KEY:latest,JWT_SECRET_KEY=JWT_SECRET_KEY:latest" \
  --add-cloudsql-instances=$PROJECT_ID:$REGION:pet-adoption-db \
  --memory=512Mi \
  --cpu=1 \
  --max-instances=10 \
  --min-instances=1
```

#### 6. 部署 Celery Worker

```bash
# Celery Worker 需要常駐，建議使用 Compute Engine 或 GKE
# 或使用 Cloud Tasks 替代 Celery
```

#### 7. 部署前端

```bash
cd frontend

# 建構前端
npm run build

# 上傳到 Cloud Storage
gsutil -m cp -r dist/* gs://your-frontend-bucket/

# 設定 Cloud CDN (可選)
# 或使用 Firebase Hosting
firebase deploy --only hosting
```

---

### 選項 B: Compute Engine + Docker Compose

#### 1. 建立 VM 實例

```bash
# 建立 VM
gcloud compute instances create pet-adoption-vm \
  --zone=asia-east1-a \
  --machine-type=n1-standard-2 \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-ssd \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --tags=http-server,https-server

# 允許 HTTP/HTTPS 流量
gcloud compute firewall-rules create allow-http \
  --allow=tcp:80 \
  --target-tags=http-server

gcloud compute firewall-rules create allow-https \
  --allow=tcp:443 \
  --target-tags=https-server
```

#### 2. SSH 到 VM 並安裝 Docker

```bash
# SSH 連線
gcloud compute ssh pet-adoption-vm --zone=asia-east1-a

# 安裝 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安裝 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 將當前使用者加入 docker 群組
sudo usermod -aG docker $USER
```

#### 3. 部署應用

```bash
# 複製專案到 VM
git clone https://github.com/your-repo/pet-adoption.git
cd pet-adoption/proj_new

# 建立 .env.gcp 檔案
cp .env.gcp.example .env.gcp
nano .env.gcp  # 填入實際配置

# 啟動服務
docker-compose --env-file .env.gcp -f docker-compose-gcp.yml up -d

# 檢查狀態
docker-compose -f docker-compose-gcp.yml ps

# 查看日誌
docker-compose -f docker-compose-gcp.yml logs -f
```

#### 4. 設定 Cloud SQL Proxy (如使用 Cloud SQL)

```bash
# 下載 Cloud SQL Proxy
wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
chmod +x cloud_sql_proxy

# 啟動 proxy
./cloud_sql_proxy -instances=$PROJECT_ID:$REGION:pet-adoption-db=tcp:3306 &

# 更新 DATABASE_URL 為 localhost:3306
```

---

## 環境變數配置

### 必要環境變數

參考 `.env.gcp.example` 檔案設定以下必要變數：

1. **資料庫連線**: `DATABASE_URL`
2. **Redis 連線**: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
3. **應用密鑰**: `SECRET_KEY`, `JWT_SECRET_KEY`
4. **CORS 設定**: `CORS_ORIGINS`
5. **SMTP 設定**: `SMTP_*` 變數
6. **物件儲存**: MinIO 或 Cloud Storage 相關變數

### 使用 Secret Manager

```bash
# 在應用中讀取 secrets
from google.cloud import secretmanager

def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

---

## 安全性建議

### 1. 網路安全

- 使用 VPC 隔離資源
- 設定防火牆規則限制流量
- 啟用 Cloud Armor (DDoS 防護)

```bash
# 建立 VPC
gcloud compute networks create pet-adoption-vpc --subnet-mode=custom

# 建立子網路
gcloud compute networks subnets create pet-adoption-subnet \
  --network=pet-adoption-vpc \
  --region=$REGION \
  --range=10.0.0.0/24
```

### 2. 身份與存取管理 (IAM)

- 使用服務帳戶
- 遵循最小權限原則
- 定期輪換密鑰

```bash
# 建立服務帳戶
gcloud iam service-accounts create pet-adoption-sa \
  --display-name="Pet Adoption Service Account"

# 授予必要權限
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:pet-adoption-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"
```

### 3. 資料保護

- 啟用資料庫加密
- 定期備份
- 設定保留政策

```bash
# 啟用自動備份
gcloud sql instances patch pet-adoption-db \
  --backup-start-time=03:00

# 建立手動備份
gcloud sql backups create --instance=pet-adoption-db
```

### 4. HTTPS/SSL

```bash
# 使用 Cloud Load Balancer 配置 SSL
# 或使用 Let's Encrypt

# 安裝 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 申請憑證
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

---

## 監控與維護

### 1. 設定 Cloud Monitoring

```bash
# 安裝 Cloud Monitoring Agent (在 VM 上)
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
sudo bash add-google-cloud-ops-agent-repo.sh --also-install
```

### 2. 設定告警

```python
# 在 GCP Console 設定告警政策:
# - CPU 使用率 > 80%
# - 記憶體使用率 > 90%
# - 磁碟使用率 > 85%
# - HTTP 5xx 錯誤率 > 5%
```

### 3. 日誌管理

```bash
# 查看 Cloud Run 日誌
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# 設定日誌 sink (匯出到 BigQuery)
gcloud logging sinks create pet-adoption-logs \
  bigquery.googleapis.com/projects/$PROJECT_ID/datasets/logs
```

### 4. 效能優化

- 啟用 Cloud CDN 快取靜態資源
- 使用 Cloud SQL Read Replicas (讀寫分離)
- 配置 Redis 快取策略
- 優化資料庫索引

### 5. 成本優化

```bash
# 設定預算告警
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Pet Adoption Budget" \
  --budget-amount=100USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90
```

---

## 維護腳本

### 自動部署腳本

建立 `deploy.sh`:

```bash
#!/bin/bash
set -e

PROJECT_ID="your-project-id"
REGION="asia-east1"

echo "🚀 開始部署..."

# 建構 Backend
echo "📦 建構後端映像..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/pet-adoption-backend backend/

# 部署 Backend
echo "🚢 部署後端到 Cloud Run..."
gcloud run deploy pet-adoption-backend \
  --image gcr.io/$PROJECT_ID/pet-adoption-backend \
  --region $REGION

# 建構並部署 Frontend
echo "🎨 建構前端..."
cd frontend && npm run build
echo "📤 上傳到 Cloud Storage..."
gsutil -m rsync -r -d dist/ gs://your-frontend-bucket/

echo "✅ 部署完成！"
```

### 備份腳本

建立 `backup.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)

# 備份資料庫
gcloud sql backups create --instance=pet-adoption-db

# 備份檔案
gsutil -m cp -r gs://pet-adoption-images gs://pet-adoption-backups/$DATE/

echo "✅ 備份完成: $DATE"
```

---

## 疑難排解

### 常見問題

1. **連線 Cloud SQL 失敗**
   - 檢查 Cloud SQL Proxy 是否運行
   - 確認 IAM 權限正確
   - 檢查 VPC 網路配置

2. **Redis 連線錯誤**
   - 確認 Memorystore 實例在同一 VPC
   - 檢查防火牆規則

3. **檔案上傳失敗**
   - 檢查 Cloud Storage bucket 權限
   - 確認 CORS 設定正確

4. **記憶體不足**
   - 增加 Cloud Run 記憶體配額
   - 優化 Celery worker 數量

---

## 參考資源

- [GCP 官方文件](https://cloud.google.com/docs)
- [Cloud Run 最佳實踐](https://cloud.google.com/run/docs/best-practices)
- [Cloud SQL 效能調校](https://cloud.google.com/sql/docs/mysql/best-practices)
- [Docker Compose 生產部署](https://docs.docker.com/compose/production/)

---

## 聯絡與支援

如有問題，請聯繫開發團隊或提交 Issue。

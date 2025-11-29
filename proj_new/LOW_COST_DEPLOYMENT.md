# 低成本 GCP 部署方案

本指南提供經濟實惠的 GCP 部署方案，適合小型專案或測試環境。

## 💰 成本優化策略

### 配置特點
- ✅ **使用容器內服務** - 不使用 Cloud SQL、Memorystore 等託管服務
- ✅ **單一 VM 部署** - 所有服務運行在一台虛擬機上
- ✅ **最小資源配置** - 降低 CPU 和記憶體使用
- ✅ **簡化健康檢查** - 減少資源消耗
- ✅ **低並發設定** - Celery worker 只使用 2 個並發

### 預估月成本（以台灣地區為例）

```
Compute Engine (e2-small)     ~$15-20/月
磁碟 (50GB SSD)               ~$8/月
流量 (1TB)                    ~$12/月
備份 (選填)                   ~$5/月
--------------------------------
總計                          ~$40-50/月
```

---

## 🚀 快速部署步驟

### 1. 建立最低規格的 VM

```bash
# 設定變數
export PROJECT_ID=your-project-id
export REGION=asia-east1
export ZONE=asia-east1-a

# 建立 e2-small 實例（最便宜的選項）
gcloud compute instances create pet-adoption-vm \
  --project=$PROJECT_ID \
  --zone=$ZONE \
  --machine-type=e2-small \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-standard \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --tags=http-server,https-server \
  --metadata=startup-script='#!/bin/bash
    apt-get update
    apt-get install -y docker.io docker-compose git
    systemctl start docker
    systemctl enable docker
  '

# 允許 HTTP/HTTPS 流量
gcloud compute firewall-rules create allow-http-https \
  --allow=tcp:80,tcp:443 \
  --target-tags=http-server,https-server \
  --source-ranges=0.0.0.0/0
```

### 2. 配置靜態 IP（可選，節省成本可跳過）

```bash
# 保留靜態 IP（會增加成本約 $3/月）
gcloud compute addresses create pet-adoption-ip --region=$REGION

# 取得 IP
gcloud compute addresses describe pet-adoption-ip --region=$REGION --format="get(address)"

# 附加到 VM
gcloud compute instances delete-access-config pet-adoption-vm \
  --access-config-name="external-nat" --zone=$ZONE

gcloud compute instances add-access-config pet-adoption-vm \
  --access-config-name="external-nat" \
  --address=STATIC_IP \
  --zone=$ZONE
```

### 3. SSH 連線到 VM 並部署

```bash
# SSH 連線
gcloud compute ssh pet-adoption-vm --zone=$ZONE

# 安裝 Docker 和 Docker Compose（如果啟動腳本未完成）
sudo apt-get update
sudo apt-get install -y docker.io git
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo usermod -aG docker $USER

# 登出並重新登入以套用 Docker 群組
exit
gcloud compute ssh pet-adoption-vm --zone=$ZONE

# Clone 專案
git clone https://github.com/your-username/your-repo.git
cd your-repo/proj_new

# 建立環境變數檔案
cat > .env.gcp <<EOF
# 資料庫配置
MYSQL_ROOT_PASSWORD=$(openssl rand -base64 32)
MYSQL_DATABASE=pet_adoption
MYSQL_USER=petuser
MYSQL_PASSWORD=$(openssl rand -base64 24)

# MinIO 配置
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=$(openssl rand -base64 24)
MINIO_SERVER_URL=http://YOUR_VM_IP:9000
MINIO_EXTERNAL_ENDPOINT=YOUR_VM_IP:9000

# 應用程式密鑰
SECRET_KEY=$(openssl rand -base64 32)
JWT_SECRET_KEY=$(openssl rand -base64 32)

# CORS 設定
CORS_ORIGINS=http://YOUR_VM_IP,http://YOUR_DOMAIN

# SMTP 設定 (使用 Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@your-domain.com

# 前端 API URL
VITE_API_BASE_URL=http://YOUR_VM_IP:5000/api
EOF

# 替換 YOUR_VM_IP 為實際 IP
VM_IP=$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google")
sed -i "s/YOUR_VM_IP/$VM_IP/g" .env.gcp

# 啟動服務
docker-compose --env-file .env.gcp -f docker-compose-gcp.yml up -d

# 查看狀態
docker-compose -f docker-compose-gcp.yml ps

# 查看日誌
docker-compose -f docker-compose-gcp.yml logs -f
```

### 4. 初始化資料庫

```bash
# 執行資料庫遷移
docker-compose -f docker-compose-gcp.yml exec backend flask db upgrade

# 建立測試帳號（選填）
docker-compose -f docker-compose-gcp.yml exec backend python create_test_accounts.py

# 設定 MinIO bucket 權限
docker-compose -f docker-compose-gcp.yml exec backend python scripts/set_minio_policy.py
```

---

## 🔧 進階配置

### 使用 Nginx 作為反向代理（推薦）

建立 `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:5000;
    }

    upstream frontend {
        server frontend:80;
    }

    server {
        listen 80;
        server_name _;

        # 前端
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # 後端 API
        location /api {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # MinIO (可選)
        location /minio {
            proxy_pass http://minio:9000;
            proxy_set_header Host $host;
        }
    }
}
```

在 `docker-compose-gcp.yml` 添加 Nginx 服務：

```yaml
  nginx:
    image: nginx:alpine
    container_name: pet-adoption-nginx
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
      - frontend
    networks:
      - pet-adoption-network
```

### 設定 Let's Encrypt SSL（免費 HTTPS）

```bash
# 安裝 Certbot
sudo apt-get install -y certbot

# 停止 Docker 服務（暫時）
docker-compose -f docker-compose-gcp.yml down

# 申請憑證
sudo certbot certonly --standalone -d your-domain.com

# 更新 nginx.conf 支援 HTTPS
# 重新啟動服務
docker-compose -f docker-compose-gcp.yml up -d
```

---

## 📊 監控與維護

### 1. 基本監控腳本

建立 `monitor.sh`:

```bash
#!/bin/bash

echo "=== 系統資源使用 ==="
free -h
echo ""
df -h
echo ""

echo "=== Docker 容器狀態 ==="
docker-compose -f docker-compose-gcp.yml ps
echo ""

echo "=== 容器資源使用 ==="
docker stats --no-stream
```

### 2. 自動備份腳本

建立 `backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR=/home/$USER/backups
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 備份資料庫
docker-compose -f docker-compose-gcp.yml exec -T mysql \
  mysqldump -u root -p$MYSQL_ROOT_PASSWORD pet_adoption > $BACKUP_DIR/db_$DATE.sql

# 備份 MinIO 資料
docker-compose -f docker-compose-gcp.yml exec -T minio \
  tar czf - /data > $BACKUP_DIR/minio_$DATE.tar.gz

# 刪除 7 天前的備份
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "備份完成: $DATE"
```

設定 Cron 定時備份：

```bash
# 每天凌晨 3 點備份
crontab -e
# 添加: 0 3 * * * /home/your-user/backup.sh >> /home/your-user/backup.log 2>&1
```

### 3. 自動重啟腳本（當容器異常時）

建立 `health-check.sh`:

```bash
#!/bin/bash
cd /path/to/proj_new

# 檢查後端健康
if ! docker-compose -f docker-compose-gcp.yml exec -T backend curl -f http://localhost:5000/api/health; then
    echo "Backend unhealthy, restarting..."
    docker-compose -f docker-compose-gcp.yml restart backend
fi

# 檢查其他服務...
```

---

## 💡 成本優化技巧

### 1. 使用搶占式 VM（最多省 80%）

```bash
# 建立搶占式實例（可能會被中斷）
gcloud compute instances create pet-adoption-vm \
  --preemptible \
  --machine-type=e2-small \
  ...其他參數
```

**注意**：搶占式 VM 可能隨時被 Google 收回，適合開發/測試環境。

### 2. 排程開關機

```bash
# 建立關機排程（非營業時間關機）
gcloud compute instances stop pet-adoption-vm --zone=$ZONE

# 建立開機排程
gcloud compute instances start pet-adoption-vm --zone=$ZONE
```

使用 Cloud Scheduler 自動化：

```bash
# 每天晚上 11 點關機
gcloud scheduler jobs create http shutdown-vm \
  --schedule="0 23 * * *" \
  --uri="https://compute.googleapis.com/compute/v1/projects/$PROJECT_ID/zones/$ZONE/instances/pet-adoption-vm/stop" \
  --http-method=POST \
  --oauth-service-account-email=your-sa@$PROJECT_ID.iam.gserviceaccount.com

# 每天早上 8 點開機
gcloud scheduler jobs create http startup-vm \
  --schedule="0 8 * * *" \
  --uri="https://compute.googleapis.com/compute/v1/projects/$PROJECT_ID/zones/$ZONE/instances/pet-adoption-vm/start" \
  --http-method=POST \
  --oauth-service-account-email=your-sa@$PROJECT_ID.iam.gserviceaccount.com
```

### 3. 使用標準磁碟而非 SSD

```bash
# 標準硬碟比 SSD 便宜 50-60%
--boot-disk-type=pd-standard  # 而不是 pd-ssd
```

### 4. 善用免費額度

GCP 提供：
- 每月 1 個 e2-micro 實例免費（美國地區）
- 30GB 標準磁碟免費
- 1GB 網路輸出免費

選擇美國地區可以使用免費額度：

```bash
--zone=us-central1-a
--machine-type=e2-micro
```

---

## 🔍 疑難排解

### 問題 1: 記憶體不足

```bash
# 檢查記憶體使用
docker stats

# 解決方案：增加 swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 問題 2: 磁碟空間不足

```bash
# 清理 Docker
docker system prune -a --volumes

# 清理舊的備份
find /home/$USER/backups -mtime +7 -delete
```

### 問題 3: 容器無法啟動

```bash
# 查看詳細日誌
docker-compose -f docker-compose-gcp.yml logs backend

# 重建容器
docker-compose -f docker-compose-gcp.yml up -d --force-recreate backend
```

---

## 📈 升級路徑

當流量增長時，可以這樣升級：

1. **階段 1**: 使用更大的 VM (e2-small → e2-medium)
2. **階段 2**: 將資料庫遷移到 Cloud SQL
3. **階段 3**: 使用 Cloud Load Balancer + 多個 VM
4. **階段 4**: 遷移到 Cloud Run 或 GKE

---

## ⚠️ 注意事項

1. **資料備份**：定期備份資料庫和檔案
2. **安全性**：定期更新系統和 Docker 映像
3. **監控**：設定告警通知異常情況
4. **SSL 憑證**：Let's Encrypt 憑證每 90 天需更新

---

## 📞 支援

如有問題，請查看日誌：

```bash
docker-compose -f docker-compose-gcp.yml logs -f --tail=100
```

或聯繫開發團隊。

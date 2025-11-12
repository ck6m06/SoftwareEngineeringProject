# Docker 部署指南

## 快速開始

### 1. 環境準備

確保已安裝:
- Docker Desktop (Windows/Mac) 或 Docker Engine (Linux)
- Docker Compose v2.0+

### 2. 環境變數設置

\\\ash
# 複製環境變數範例文件
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 編輯 backend/.env 設置以下必要變數
# SECRET_KEY=your-secret-key-here
# JWT_SECRET_KEY=your-jwt-secret-key-here
\\\

### 3. 啟動服務

\\\ash
# 啟動所有服務 (首次啟動會建構映像)
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f

# 查看特定服務日誌
docker-compose logs -f frontend
docker-compose logs -f backend
\\\

### 4. 初始化資料庫

\\\ash
# 進入後端容器
docker-compose exec backend bash

# 執行資料庫遷移
flask db upgrade

# 退出容器
exit
\\\

### 5. 訪問服務

- 前端應用: http://localhost:5173
- 後端 API: http://localhost:5000
- API 文檔: http://localhost:5000/api/docs
- MinIO 控制台: http://localhost:9001

## 開發模式

### 前端開發

前端使用 Vite 開發伺服器,支援熱重載 (HMR):

\\\ash
# 前端代碼變更會自動重載
# 直接編輯 frontend/src/ 下的文件即可

# 如果需要重啟前端容器
docker-compose restart frontend
\\\

### 後端開發

\\\ash
# 後端代碼變更需要重啟
docker-compose restart backend

# 或使用 Flask 開發模式 (自動重載)
# 在 docker-compose.yml 中設置 FLASK_ENV=development
\\\

### 安裝新的依賴

**前端**:
\\\ash
# 進入前端容器
docker-compose exec frontend sh

# 安裝套件
npm install package-name

# 退出
exit

# 重建容器以保存變更
docker-compose build frontend
\\\

**後端**:
\\\ash
# 進入後端容器
docker-compose exec backend bash

# 安裝套件
pip install package-name

# 更新 requirements.txt
pip freeze > requirements.txt

# 退出
exit

# 重建容器
docker-compose build backend
\\\

## 常用指令

\\\ash
# 停止所有服務
docker-compose down

# 停止並刪除所有數據 (包括資料庫)
docker-compose down -v

# 重建特定服務
docker-compose build frontend
docker-compose build backend

# 重啟特定服務
docker-compose restart frontend

# 查看容器資源使用
docker stats

# 進入容器 shell
docker-compose exec frontend sh      # Alpine Linux 使用 sh
docker-compose exec backend bash     # Debian/Ubuntu 使用 bash

# 查看容器網路
docker network inspect proj_new_pet-adoption-network
\\\

## 資料庫管理

\\\ash
# 進入 MySQL 容器
docker-compose exec mysql mysql -u petuser -p pet_adoption

# 備份資料庫
docker-compose exec mysql mysqldump -u petuser -p pet_adoption > backup.sql

# 還原資料庫
docker-compose exec -T mysql mysql -u petuser -p pet_adoption < backup.sql
\\\

## 故障排除

### 前端無法連接到後端

1. 檢查 CORS 設置:
   \\\
   CORS_ORIGINS="http://localhost:5173"
   \\\

2. 檢查 Vite 代理配置 (vite.config.ts):
   \\\	ypescript
   proxy: {
     '/api': {
       target: 'http://backend:5000',
       changeOrigin: true,
     },
   }
   \\\

### 容器無法啟動

\\\ash
# 查看詳細錯誤
docker-compose logs service-name

# 檢查端口衝突
netstat -ano | findstr "5173"  # Windows
lsof -i :5173                   # Linux/Mac

# 清理並重啟
docker-compose down
docker-compose up -d --build
\\\

### 前端熱重載不工作

在 docker-compose.yml 中確保有:
\\\yaml
volumes:
  - ./frontend:/app
  - /app/node_modules
stdin_open: true
tty: true
\\\

### 資料庫連接失敗

\\\ash
# 等待 MySQL 完全啟動
docker-compose logs mysql

# 檢查健康狀態
docker-compose ps

# 重啟資料庫
docker-compose restart mysql
\\\

## 生產部署

\\\ash
# 使用生產配置
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 或修改 docker-compose.yml 中的 target
# target: production
\\\

## 性能優化

### 減少映像大小

1. 使用 .dockerignore 排除不必要的文件
2. 使用多階段建構
3. 清理 npm/pip 快取

### 加快建構速度

\\\ash
# 使用 BuildKit
DOCKER_BUILDKIT=1 docker-compose build

# 平行建構
docker-compose build --parallel
\\\

## 清理

\\\ash
# 清理未使用的映像
docker image prune -a

# 清理所有未使用的資源
docker system prune -a --volumes

# 清理建構快取
docker builder prune
\\\

---

**最後更新**: 2025-10-26  
**維護者**: Development Team

# 資料遷移腳本 - 從 Docker volumes 遷移到本地目錄
# 使用方法: .\migrate-data.ps1

Write-Host "=== Docker 資料遷移工具 ===" -ForegroundColor Green
Write-Host ""

# 檢查 Docker 是否運行
$dockerRunning = docker info 2>$null
if (-not $dockerRunning) {
    Write-Host "錯誤: Docker 未運行，請先啟動 Docker Desktop" -ForegroundColor Red
    exit 1
}

# 創建本地資料目錄
Write-Host "1. 創建本地資料目錄..." -ForegroundColor Yellow
New-Item -Path "docker-data/mysql" -ItemType Directory -Force | Out-Null
New-Item -Path "docker-data/redis" -ItemType Directory -Force | Out-Null
New-Item -Path "docker-data/minio" -ItemType Directory -Force | Out-Null
Write-Host "   ✓ 目錄已創建" -ForegroundColor Green

# 備份 MySQL 資料
Write-Host ""
Write-Host "2. 備份 MySQL 資料..." -ForegroundColor Yellow
docker run --rm -v proj_new_mysql-data:/source -v ${PWD}/docker-data/mysql:/dest alpine sh -c "cp -av /source/. /dest/"
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ MySQL 資料已備份" -ForegroundColor Green
} else {
    Write-Host "   ⚠ MySQL volume 不存在或為空" -ForegroundColor Yellow
}

# 備份 Redis 資料
Write-Host ""
Write-Host "3. 備份 Redis 資料..." -ForegroundColor Yellow
docker run --rm -v proj_new_redis-data:/source -v ${PWD}/docker-data/redis:/dest alpine sh -c "cp -av /source/. /dest/"
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Redis 資料已備份" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Redis volume 不存在或為空" -ForegroundColor Yellow
}

# 備份 MinIO 資料
Write-Host ""
Write-Host "4. 備份 MinIO 資料..." -ForegroundColor Yellow
docker run --rm -v proj_new_minio-data:/source -v ${PWD}/docker-data/minio:/dest alpine sh -c "cp -av /source/. /dest/"
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ MinIO 資料已備份" -ForegroundColor Green
} else {
    Write-Host "   ⚠ MinIO volume 不存在或為空" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== 遷移完成 ===" -ForegroundColor Green
Write-Host ""
Write-Host "下一步操作:" -ForegroundColor Cyan
Write-Host "1. 停止現有容器: docker-compose down"
Write-Host "2. 啟動新配置: docker-compose up -d"
Write-Host "3. 檢查資料: 訪問 http://localhost:5173"
Write-Host ""
Write-Host "資料位置: ./docker-data/" -ForegroundColor Yellow
Write-Host "- MySQL: ./docker-data/mysql/"
Write-Host "- Redis: ./docker-data/redis/"
Write-Host "- MinIO: ./docker-data/minio/"

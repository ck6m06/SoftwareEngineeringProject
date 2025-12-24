# Celery Worker 啟動指令

## Windows (PowerShell)

```powershell
# 方法 1: 使用 Python 腳本
cd backend
python start_worker.py

# 方法 2: 直接使用 Celery 命令
cd backend
$env:FLASK_APP="app"
celery -A app.celery:celery worker --loglevel=info --pool=solo

# 方法 3: 使用 eventlet (需要安裝 eventlet)
pip install eventlet
celery -A app.celery:celery worker --loglevel=info --pool=eventlet
```

## Linux / macOS

```bash
# 方法 1: 使用 Python 腳本
cd backend
python start_worker.py

# 方法 2: 直接使用 Celery 命令
cd backend
export FLASK_APP=app
celery -A app.celery:celery worker --loglevel=info --concurrency=4

# 方法 3: 背景執行
celery -A app.celery:celery worker --loglevel=info --detach
```

## Docker Compose

如果使用 Docker Compose，可以在 `docker-compose.yml` 中添加 Worker 服務：

```yaml
services:
  # ... 其他服務 ...
  
  celery_worker:
    build: ./backend
    command: celery -A app.celery:celery worker --loglevel=info --concurrency=4
    environment:
      - FLASK_APP=app
      - DATABASE_URL=postgresql://user:password@postgres:5432/dbname
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
```

## 監控 Celery

### Flower (Web UI)

```bash
# 安裝 Flower
pip install flower

# 啟動 Flower
celery -A app.celery:celery flower --port=5555

# 訪問: http://localhost:5555
```

### Celery Events

```bash
# 即時監控任務
celery -A app.celery:celery events
```

### 檢查 Worker 狀態

```bash
# 檢查活躍的 worker
celery -A app.celery:celery inspect active

# 檢查已註冊的 tasks
celery -A app.celery:celery inspect registered

# 檢查統計資訊
celery -A app.celery:celery inspect stats
```

## 常見問題

### Redis 連線錯誤

確保 Redis 已啟動：
```bash
# Windows (需要安裝 Redis for Windows)
redis-server

# Linux / macOS
redis-server

# 或使用 Docker
docker run -d -p 6379:6379 redis:alpine
```

### Windows Pool 問題

Windows 不支援 `fork()`，必須使用 `--pool=solo` 或 `--pool=eventlet`

### 任務未執行

1. 檢查 Worker 是否啟動
2. 檢查 Redis 連線
3. 檢查 tasks 是否正確註冊: `celery -A app.celery:celery inspect registered`
4. 檢查日誌: `--loglevel=debug`

## 生產環境部署

### Systemd (Linux)

創建 `/etc/systemd/system/celery-worker.service`:

```ini
[Unit]
Description=Celery Worker
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/celery -A app.celery:celery worker \
    --loglevel=info \
    --concurrency=4 \
    --pidfile=/var/run/celery/worker.pid \
    --logfile=/var/log/celery/worker.log

[Install]
WantedBy=multi-user.target
```

啟動服務:
```bash
sudo systemctl daemon-reload
sudo systemctl enable celery-worker
sudo systemctl start celery-worker
sudo systemctl status celery-worker
```

### Supervisor (跨平台)

安裝 Supervisor:
```bash
pip install supervisor
```

配置 `/etc/supervisor/conf.d/celery.conf`:
```ini
[program:celery-worker]
command=/path/to/venv/bin/celery -A app.celery:celery worker --loglevel=info --concurrency=4
directory=/path/to/backend
user=www-data
numprocs=1
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker.err.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
```

管理 Worker:
```bash
supervisorctl reread
supervisorctl update
supervisorctl start celery-worker
supervisorctl status
```

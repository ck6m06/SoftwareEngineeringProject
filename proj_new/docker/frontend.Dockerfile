# Frontend Dockerfile - Multi-stage build

# Development stage
FROM node:18-alpine AS development

WORKDIR /app

# 安裝 git (某些 npm 套件需要)
RUN apk add --no-cache git

# 複製 package files
COPY package*.json ./

# 安裝依賴
RUN npm install

# 複製原始碼
COPY . .

# 暴露 Vite 開發伺服器端口
EXPOSE 5173

# 開發模式啟動 (支持熱重載)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Builder stage
FROM node:18-alpine AS builder

WORKDIR /app

# 複製 package files
COPY package*.json ./

# 安裝依賴
RUN npm ci

# 複製原始碼
COPY . .

# 建立生產版本
RUN npm run build

# Production stage
FROM nginx:alpine AS production

# 複製 nginx 設定
COPY ../docker/nginx.conf /etc/nginx/conf.d/default.conf

# 複製建構後的檔案
COPY --from=builder /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

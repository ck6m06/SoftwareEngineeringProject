import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://backend:5000',
        changeOrigin: true,
      },
      '/minio': {
        // 使用環境變數或容器名稱，支援本地開發和 Docker 環境
        target: process.env.VITE_MINIO_URL || 'http://minio:9000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/minio/, ''),
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})

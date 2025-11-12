<template>
  <div class="file-uploader">
    <!-- 上傳區域 -->
    <div
      class="upload-area"
      :class="{ 'drag-over': isDragOver, 'has-files': files.length > 0 }"
      @dragover.prevent="onDragOver"
      @dragleave.prevent="onDragLeave"
      @drop.prevent="onDrop"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        :accept="accept"
        :multiple="multiple"
        class="hidden"
        @change="onFileChange"
      />
      
      <div v-if="files.length === 0" class="upload-prompt">
        <svg class="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <p class="text-base text-gray-700">拖曳檔案到此處，或點擊選擇檔案</p>
        <p class="text-sm text-gray-500 mt-2">{{ acceptText }}</p>
        <p v-if="maxSize" class="text-sm text-gray-500">最大檔案大小: {{ formatSize(maxSize) }}</p>
      </div>
    </div>

    <!-- 檔案列表 -->
    <div v-if="files.length > 0" class="files-list mt-4">
      <div v-for="(item, index) in files" :key="index" class="file-item">
        <!-- 圖片預覽 -->
        <div class="file-preview">
          <img v-if="isImage(item.file)" :src="getPreviewUrl(item.file)" alt="預覽" class="preview-image" />
          <div v-else class="preview-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        </div>

        <!-- 檔案資訊 -->
        <div class="file-info">
          <p class="file-name">{{ item.file.name }}</p>
          <p class="file-size">{{ formatSize(item.file.size) }}</p>
          
          <!-- 進度條 -->
          <div v-if="item.status === 'uploading'" class="progress-bar">
            <div class="progress-fill" :style="{ width: item.progress + '%' }"></div>
          </div>
          
          <!-- 狀態訊息 -->
          <p v-if="item.status === 'success'" class="status-success">✓ 上傳成功</p>
          <p v-if="item.status === 'error'" class="status-error">✗ {{ item.error }}</p>
        </div>

        <!-- 操作按鈕 -->
        <button
          v-if="item.status !== 'uploading'"
          type="button"
          class="remove-btn"
          @click="removeFile(index)"
        >
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 操作按鈕組 -->
    <div v-if="files.length > 0" class="actions mt-4 flex gap-2">
      <button
        v-if="!autoUpload"
        type="button"
        class="btn-primary"
        :disabled="isUploading || files.every(f => f.status === 'success')"
        @click="handleUpload"
      >
        {{ isUploading ? '上傳中...' : '開始上傳' }}
      </button>
      <button
        type="button"
        class="btn-secondary"
        :disabled="isUploading"
        @click="clearFiles"
      >
        清除全部
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useUpload } from '@/composables/useUpload'
import type { UploadItem } from '@/composables/useUpload'

interface Props {
  accept?: string
  multiple?: boolean
  maxSize?: number // bytes
  autoUpload?: boolean
  ownerType?: string
  ownerId?: number
}

const props = withDefaults(defineProps<Props>(), {
  accept: 'image/*',
  multiple: true,
  maxSize: 10 * 1024 * 1024, // 10MB
  autoUpload: false,
})

const emit = defineEmits<{
  uploaded: [files: any[]]
  error: [error: string]
}>()

const fileInput = ref<HTMLInputElement>()
const isDragOver = ref(false)
const files = ref<UploadItem[]>([])
const { uploadMultiple, isUploading } = useUpload()

const acceptText = computed(() => {
  if (props.accept === 'image/*') return '支援 JPG, PNG, GIF 等圖片格式'
  if (props.accept.includes('image')) return '僅支援圖片檔案'
  return '支援多種檔案格式'
})

function triggerFileInput() {
  fileInput.value?.click()
}

function onDragOver() {
  isDragOver.value = true
}

function onDragLeave() {
  isDragOver.value = false
}

function onDrop(e: DragEvent) {
  isDragOver.value = false
  const droppedFiles = Array.from(e.dataTransfer?.files || [])
  addFiles(droppedFiles)
}

function onFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  const selectedFiles = Array.from(target.files || [])
  addFiles(selectedFiles)
  target.value = '' // 重置 input
}

function addFiles(newFiles: File[]) {
  for (const file of newFiles) {
    // 驗證檔案大小
    if (props.maxSize && file.size > props.maxSize) {
      emit('error', `檔案 ${file.name} 超過大小限制 ${formatSize(props.maxSize)}`)
      continue
    }

    // 驗證檔案類型
    if (props.accept && !matchAccept(file.type, props.accept)) {
      emit('error', `檔案 ${file.name} 格式不符`)
      continue
    }

    files.value.push({
      file,
      progress: 0,
      status: 'pending',
    })
  }

  // 自動上傳
  if (props.autoUpload && props.ownerType && props.ownerId) {
    handleUpload()
  }
}

function matchAccept(fileType: string, accept: string): boolean {
  if (accept === '*' || accept === '*/*') return true
  const acceptTypes = accept.split(',').map(t => t.trim())
  return acceptTypes.some(type => {
    if (type.endsWith('/*')) {
      const prefix = type.slice(0, -2)
      return fileType.startsWith(prefix)
    }
    return fileType === type
  })
}

async function handleUpload() {
  if (!props.ownerType || !props.ownerId) {
    emit('error', '缺少上傳參數')
    return
  }

  const pendingFiles = files.value.filter(f => f.status === 'pending')
  if (pendingFiles.length === 0) return

  try {
    const results = await uploadMultiple(
      pendingFiles.map(f => f.file),
      props.ownerType,
      props.ownerId
    )
    
    // 更新狀態
    pendingFiles.forEach((item, idx) => {
      item.status = 'success'
      item.progress = 100
      item.result = results[idx]
    })

    emit('uploaded', results)
  } catch (error: any) {
    emit('error', error.message || '上傳失敗')
  }
}

function removeFile(index: number) {
  files.value.splice(index, 1)
}

function clearFiles() {
  files.value = []
}

function isImage(file: File): boolean {
  return file.type.startsWith('image/')
}

function getPreviewUrl(file: File): string {
  return URL.createObjectURL(file)
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// 暴露方法給父元件
defineExpose({
  files,
  clearFiles,
})
</script>

<style scoped>
.file-uploader {
  width: 100%;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #f9fafb;
}

.upload-area:hover {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

.upload-area.drag-over {
  border-color: #3b82f6;
  background-color: #dbeafe;
}

.upload-area.has-files {
  border-color: #10b981;
  background-color: #f0fdf4;
}

.upload-icon {
  width: 3rem;
  height: 3rem;
  margin: 0 auto 1rem;
  color: #9ca3af;
}

.hidden {
  display: none;
}

.files-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  background-color: white;
}

.file-preview {
  flex-shrink: 0;
  width: 4rem;
  height: 4rem;
  border-radius: 0.375rem;
  overflow: hidden;
  background-color: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-icon svg {
  width: 2rem;
  height: 2rem;
  color: #9ca3af;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-weight: 500;
  color: #374151;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.progress-bar {
  margin-top: 0.5rem;
  height: 0.5rem;
  background-color: #e5e7eb;
  border-radius: 0.25rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #3b82f6;
  transition: width 0.3s ease;
}

.status-success {
  color: #10b981;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.status-error {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.remove-btn {
  flex-shrink: 0;
  padding: 0.5rem;
  border: none;
  background: none;
  color: #9ca3af;
  cursor: pointer;
  border-radius: 0.375rem;
  transition: all 0.2s;
}

.remove-btn:hover {
  color: #ef4444;
  background-color: #fee2e2;
}

.remove-btn svg {
  width: 1.25rem;
  height: 1.25rem;
}

.btn-primary {
  padding: 0.5rem 1rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-primary:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 0.5rem 1rem;
  background-color: white;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #f3f4f6;
}

.btn-secondary:disabled {
  color: #9ca3af;
  cursor: not-allowed;
}
</style>

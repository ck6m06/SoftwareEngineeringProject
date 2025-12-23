/**
 * useUploadPresign - 封裝 presigned URL 上傳邏輯的 composable
 */
import { ref, computed } from 'vue'
import { uploadFile } from '@/api/uploads'
import type { AttachmentMetadata } from '@/api/uploads'

export interface UploadItem {
  file: File
  progress: number
  status: 'pending' | 'uploading' | 'success' | 'error'
  error?: string
  result?: AttachmentMetadata
}

export function useUploadPresign() {
  const uploads = ref<UploadItem[]>([])
  const isUploading = ref(false)

  /**
   * 上傳單個檔案
   */
  async function uploadSingle(
    file: File,
    ownerType: string,
    ownerId: number
  ): Promise<AttachmentMetadata> {
    const item: UploadItem = {
      file,
      progress: 0,
      status: 'pending',
    }
    uploads.value.push(item)

    try {
      item.status = 'uploading'
      const result = await uploadFile(file, ownerType, ownerId, (progress) => {
        item.progress = progress
      })
      item.status = 'success'
      item.result = result
      return result
    } catch (error: any) {
      item.status = 'error'
      item.error = error.response?.data?.message || error.message || '上傳失敗'
      throw error
    }
  }

  /**
   * 上傳多個檔案
   */
  async function uploadMultiple(
    files: File[],
    ownerType: string,
    ownerId: number
  ): Promise<AttachmentMetadata[]> {
    isUploading.value = true
    const results: AttachmentMetadata[] = []

    try {
      for (const file of files) {
        const result = await uploadSingle(file, ownerType, ownerId)
        results.push(result)
      }
      return results
    } finally {
      isUploading.value = false
    }
  }

  /**
   * 清除上傳記錄
   */
  function clearUploads() {
    uploads.value = []
  }

  /**
   * 移除特定上傳記錄
   */
  function removeUpload(file: File) {
    const index = uploads.value.findIndex((item) => item.file === file)
    if (index !== -1) {
      uploads.value.splice(index, 1)
    }
  }

  /**
   * 取得上傳統計
   */
  const uploadStats = computed(() => {
    const total = uploads.value.length
    const success = uploads.value.filter((item) => item.status === 'success').length
    const error = uploads.value.filter((item) => item.status === 'error').length
    const uploading = uploads.value.filter((item) => item.status === 'uploading').length
    
    return { total, success, error, uploading }
  })

  return {
    uploads,
    isUploading,
    uploadSingle,
    uploadMultiple,
    clearUploads,
    removeUpload,
    uploadStats,
  }
}

/**
 * Uploads API Service
 */
import api from './client'

export interface AttachmentMetadata {
  owner_type: string
  owner_id: number
  storage_key: string
  url: string
  filename: string
  mime_type: string
  size: number
}

/**
 * 直接上傳檔案 (後端代理)
 */
export async function uploadDirect(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post<{
    upload_id: string
    storage_key: string
    filename: string
    size: number
    content_type: string
    url: string
  }>('/uploads/direct', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  
  return response.data
}

/**
 * 完整上傳流程: 直接上傳到後端 (後端代理模式)
 * 注意: 這個函數只負責上傳文件到 MinIO 並返回 URL
 * 調用者需要自行將 URL 保存到相應的數據表 (如 animal_images)
 */
export async function uploadFile(
  file: File,
  ownerType: string,
  ownerId: number,
  onProgress?: (progress: number) => void
) {
  // 使用直接上傳模式 (後端代理)
  if (onProgress) onProgress(50)
  
  const uploadResult = await uploadDirect(file)
  
  if (onProgress) onProgress(100)

  // 返回上傳結果 (包含 URL 和 storage_key)
  return {
    attachment_id: 0,
    object_key: uploadResult.storage_key,
    filename: uploadResult.filename,
    content_type: uploadResult.content_type,
    size: uploadResult.size,
    url: uploadResult.url,
    uploaded_by_id: 0,
    created_at: new Date().toISOString(),
    owner_type: ownerType,
    owner_id: ownerId,
    storage_key: uploadResult.storage_key,
    mime_type: uploadResult.content_type,
  } as AttachmentMetadata
}


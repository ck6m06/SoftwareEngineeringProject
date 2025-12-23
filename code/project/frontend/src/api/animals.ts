/**
 * Animals API Service
 */
import api from './client'

export interface AnimalFilters {
  species?: 'CAT' | 'DOG'
  breed?: string
  sex?: 'MALE' | 'FEMALE' | 'UNKNOWN'
  status?: 'DRAFT' | 'SUBMITTED' | 'PUBLISHED' | 'ADOPTED' | 'RETIRED'
  shelter_id?: number
  owner_id?: number
  source_type?: 'shelter' | 'personal'  // 來源類型
  region?: string  // 地區/縣市
  min_age?: number  // 最小年齡(月數)
  max_age?: number  // 最大年齡(月數)
  featured?: boolean
  q?: string  // 搜尋關鍵字
  page?: number
  per_page?: number
}

export interface Animal {
  animal_id: number
  name?: string
  species?: 'CAT' | 'DOG'
  breed?: string
  color?: string
  sex?: 'MALE' | 'FEMALE' | 'UNKNOWN'
  dob?: string
  age?: number
  description?: string
  status: 'DRAFT' | 'SUBMITTED' | 'PUBLISHED' | 'ADOPTED' | 'RETIRED'
  shelter_id?: number
  owner_id?: number
  medical_summary?: string
  rejection_reason?: string
  rejected_at?: string
  rejected_by?: number
  created_by: number
  created_at: string
  updated_at: string
  deleted_at?: string
  images?: Array<{
    animal_image_id: number
    storage_key: string
    url: string
    mime_type?: string
    width?: number
    height?: number
    order: number
  }>
  featured?: boolean
  has_pending_application?: boolean
}

export interface AnimalsResponse {
  animals: Animal[]
  page: number
  per_page: number
  total: number
  pages: number
}

/**
 * 取得動物列表
 */
export async function getAnimals(filters?: AnimalFilters) {
  const response = await api.get<AnimalsResponse>('/animals', { params: filters })
  return response.data
}

/**
 * 取得單一動物詳情
 */
export async function getAnimal(id: number) {
  const response = await api.get<Animal>(`/animals/${id}`)
  return response.data
}

/**
 * 建立動物 (送養)
 */
export async function createAnimal(data: Partial<Animal>) {
  const response = await api.post<{ message: string; animal: Animal }>('/animals', data)
  return response.data
}

/**
 * 更新動物資訊
 */
export async function updateAnimal(id: number, data: Partial<Animal>) {
  const response = await api.patch<{ message: string; animal: Animal }>(`/animals/${id}`, data)
  return response.data
}

/**
 * 刪除動物
 */
export async function deleteAnimal(id: number) {
  const response = await api.delete<{ message: string }>(`/animals/${id}`)
  return response.data
}

/**
 * 發佈動物 (變更狀態為 PUBLISHED)
 */
export async function publishAnimal(id: number) {
  const response = await api.post<{ message: string; animal: Animal }>(`/animals/${id}/publish`)
  return response.data
}

/**
 * 下架動物 (變更狀態為 RETIRED)
 */
export async function retireAnimal(id: number) {
  const response = await api.post<{ message: string; animal: Animal }>(`/animals/${id}/retire`)
  return response.data
}

/**
 * 拒絕批准動物上架 (問題4、問題5)
 * SUBMITTED -> DRAFT,並記錄拒絕原因
 */
export async function rejectAnimal(id: number, rejectionReason: string) {
  const response = await api.post<{ message: string; animal: Animal }>(`/animals/${id}/reject`, {
    rejection_reason: rejectionReason
  })
  return response.data
}

/**
 * 新增動物圖片
 */
export async function addAnimalImage(animalId: number, data: { 
  image_url: string
  storage_key?: string
  mime_type?: string
  description?: string 
}) {
  const response = await api.post<{ message: string; image: any }>(`/animals/${animalId}/images`, data)
  return response.data
}

/**
 * 刪除動物圖片
 */
export async function deleteAnimalImage(animalId: number, imageId: number) {
  const response = await api.delete<{ message: string }>(`/animals/${animalId}/images/${imageId}`)
  return response.data
}

/**
 * 提交動物供審核 (DRAFT → SUBMITTED)
 */
export async function submitAnimal(animalId: number) {
  const response = await api.post<{ message: string; animal: Animal }>(`/animals/${animalId}/submit`)
  return response.data
}

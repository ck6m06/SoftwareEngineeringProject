/**
 * Shelters API Client
 * 收容所管理相關 API
 */
import api from './client'
import type { Shelter } from '@/types/models'
import type { Animal } from './animals'

export interface ShelterFilters {
  verified?: boolean
  city?: string
  district?: string
  page?: number
  per_page?: number
}

export interface SheltersResponse {
  shelters: Shelter[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export interface ShelterAnimalsFilters {
  status?: 'DRAFT' | 'SUBMITTED' | 'PUBLISHED' | 'RETIRED'
  species?: 'CAT' | 'DOG'
  page?: number
  per_page?: number
}

export interface ShelterAnimalsResponse {
  animals: Animal[]
  page: number
  per_page: number
  total: number
  pages: number
  has_prev: boolean
  has_next: boolean
}

export interface BatchStatusUpdateRequest {
  animal_ids: number[]
  action: 'draft' | 'submit' | 'publish' | 'retire'
}

export interface BatchStatusUpdateResponse {
  message: string
  success_count: number
  failed_count: number
  total_count: number
  errors: string[]
}

/**
 * 取得收容所列表
 */
export async function getShelters(filters?: ShelterFilters): Promise<SheltersResponse> {
  const response = await api.get('/shelters', { params: filters })
  return response.data
}

/**
 * 取得單一收容所詳情
 */
export async function getShelter(shelterId: number): Promise<Shelter> {
  const response = await api.get(`/shelters/${shelterId}`)
  return response.data
}

/**
 * 建立收容所
 */
export async function createShelter(data: Partial<Shelter>): Promise<Shelter> {
  const response = await api.post('/shelters', data)
  return response.data
}

/**
 * 更新收容所資訊
 */
export async function updateShelter(shelterId: number, data: Partial<Shelter>): Promise<Shelter> {
  const response = await api.patch(`/shelters/${shelterId}`, data)
  return response.data
}

/**
 * 驗證收容所 (管理員專用)
 */
export async function verifyShelter(shelterId: number): Promise<{ message: string }> {
  const response = await api.post(`/shelters/${shelterId}/verify`)
  return response.data
}

/**
 * 批次匯入動物資料 (返回 Job)
 */
export async function batchImportAnimals(shelterId: number, file: File): Promise<{ job_id: number; message: string }> {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post(`/shelters/${shelterId}/animals/batch`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  
  return response.data
}

/**
 * 取得收容所的動物列表 (含草稿狀態)
 */
export async function getShelterAnimals(shelterId: number, filters?: ShelterAnimalsFilters): Promise<ShelterAnimalsResponse> {
  const response = await api.get(`/shelters/${shelterId}/animals`, { params: filters })
  return response.data
}

/**
 * 批次更新動物狀態
 */
export async function batchUpdateAnimalStatus(shelterId: number, data: BatchStatusUpdateRequest): Promise<BatchStatusUpdateResponse> {
  const response = await api.patch(`/shelters/${shelterId}/animals/batch/status`, data)
  return response.data
}

/**
 * 獲取動物的醫療記錄
 */
export async function getAnimalMedicalRecords(animalId: number): Promise<Array<{
  medical_record_id: number
  record_type: string
  date: string
  provider: string
  details: string
  verified: boolean
  created_at: string
}>> {
  const response = await api.get(`/medical-records/animals/${animalId}/medical-records`)
  return response.data.medical_records || []
}
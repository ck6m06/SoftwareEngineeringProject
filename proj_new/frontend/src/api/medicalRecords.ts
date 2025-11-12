/**
 * Medical Records API Service
 */
import api from './client'
import type { MedicalRecord } from '@/types/models'

export interface CreateMedicalRecordData {
  record_type?: 'TREATMENT' | 'CHECKUP' | 'VACCINE' | 'SURGERY' | 'OTHER'
  date?: string  // YYYY-MM-DD format
  provider?: string
  details?: string
  attachments?: any[]
}

export interface MedicalRecordsResponse {
  total: number
  medical_records: MedicalRecord[]
}

/**
 * 建立醫療記錄
 * @param animalId 動物ID
 * @param data 醫療記錄資料
 */
export async function createMedicalRecord(animalId: number, data: CreateMedicalRecordData) {
  const response = await api.post<{ message: string; medical_record: MedicalRecord }>(
    `/medical-records/animals/${animalId}/medical-records`,
    data
  )
  return response.data
}

/**
 * 取得動物的醫療記錄列表
 * @param animalId 動物ID
 */
export async function getMedicalRecords(animalId: number) {
  const response = await api.get<MedicalRecordsResponse>(`/medical-records/animals/${animalId}/medical-records`)
  return response.data
}

/**
 * 更新醫療記錄
 * @param recordId 醫療記錄ID
 * @param data 更新的資料
 */
export async function updateMedicalRecord(recordId: number, data: Partial<CreateMedicalRecordData>) {
  const response = await api.patch<{ message: string; medical_record: MedicalRecord }>(
    `/medical-records/${recordId}`,
    data
  )
  return response.data
}

/**
 * 驗證醫療記錄 (僅 ADMIN)
 * @param recordId 醫療記錄ID
 * @param verified 是否驗證
 */
export async function verifyMedicalRecord(recordId: number, verified: boolean) {
  const response = await api.post<{ message: string; medical_record: MedicalRecord }>(
    `/medical-records/${recordId}/verify`,
    { verified }
  )
  return response.data
}

/**
 * Applications API Service
 */
import api from './client'

export interface Application {
  application_id: number
  applicant_id: number
  animal_id: number
  type: 'ADOPTION' | 'REHOME'
  status: 'PENDING' | 'UNDER_REVIEW' | 'APPROVED' | 'REJECTED' | 'WITHDRAWN'
  submitted_at?: string
  reviewed_at?: string
  review_notes?: string
  assignee_id?: number
  version: number
  attachments?: any
  // 申請人詳細資料
  contact_phone?: string
  contact_address?: string
  occupation?: string
  housing_type?: string
  has_experience?: boolean
  reason?: string
  notes?: string
  created_at: string
  updated_at: string
  applicant?: any
  animal?: any
  assignee?: any
}

export interface ApplicationFilters {
  status?: string
  animal_id?: number
  applicant_id?: number
  mode?: 'all' | 'review' | 'my'  // 新增查詢模式
  page?: number
  per_page?: number
}

export interface ApplicationsResponse {
  items: Application[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface CreateApplicationData {
  animal_id: number
  type?: 'ADOPTION' | 'REHOME'
  attachments?: any
  // 申請人詳細資料
  contact_phone?: string
  contact_address?: string
  occupation?: string
  housing_type?: string
  has_experience?: boolean
  reason?: string
  notes?: string
}

export interface ReviewApplicationData {
  action: 'approve' | 'reject'
  review_notes?: string
  version?: number
}

/**
 * 取得申請列表
 */
export async function getApplications(filters?: ApplicationFilters) {
  const response = await api.get<ApplicationsResponse>('/applications', { params: filters })
  return response.data
}

/**
 * 取得單一申請詳情
 */
export async function getApplication(id: number) {
  const response = await api.get<Application>(`/applications/${id}`)
  return response.data
}

/**
 * 建立申請 (支援 Idempotency-Key)
 */
export async function createApplication(data: CreateApplicationData, idempotencyKey?: string) {
  const headers: any = {}
  if (idempotencyKey) {
    headers['Idempotency-Key'] = idempotencyKey
  }
  
  const response = await api.post<{ message: string; application: Application }>(
    '/applications',
    data,
    { headers }
  )
  return response.data
}

/**
 * 審核申請 (核准/拒絕)
 */
export async function reviewApplication(id: number, data: ReviewApplicationData) {
  const response = await api.post<{ message: string; application: Application }>(
    `/applications/${id}/review`,
    data
  )
  return response.data
}

/**
 * 指派申請給處理人員
 */
export async function assignApplication(id: number, assigneeId: number) {
  const response = await api.post<{ message: string; application: Application }>(
    `/applications/${id}/assign`,
    { assignee_id: assigneeId }
  )
  return response.data
}

/**
 * 撤回申請
 */
export async function withdrawApplication(id: number) {
  const response = await api.post<{ message: string; application: Application }>(
    `/applications/${id}/withdraw`
  )
  return response.data
}

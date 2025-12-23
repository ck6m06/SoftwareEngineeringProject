/**
 * Jobs API Service
 */
import api from './client'
import type { Job } from '@/types/models'

export interface JobFilters {
  type?: string
  status?: 'PENDING' | 'RUNNING' | 'SUCCEEDED' | 'FAILED'
  created_by?: number
  page?: number
  per_page?: number
}

export interface JobsResponse {
  jobs: Job[]
  total: number
  page: number
  per_page: number
  pages: number
}

/**
 * 取得任務列表
 */
export async function getJobs(filters?: JobFilters) {
  const response = await api.get<JobsResponse>('/jobs', { params: filters })
  return response.data
}

/**
 * 取得單一任務狀態
 */
export async function getJob(jobId: number) {
  const response = await api.get<Job>(`/jobs/${jobId}`)
  return response.data
}

/**
 * 重試失敗的任務
 */
export async function retryJob(jobId: number) {
  const response = await api.post<{ message: string; job: Job }>(`/jobs/${jobId}/retry`)
  return response.data
}

/**
 * 取消任務
 */
export async function cancelJob(jobId: number) {
  const response = await api.post<{ message: string; job: Job }>(`/jobs/${jobId}/cancel`)
  return response.data
}

/**
 * 核准任務 (僅管理員)
 */
export async function approveJob(jobId: number, notes?: string) {
  const response = await api.post<{ message: string; job: Job }>(`/jobs/${jobId}/approve`, { notes })
  return response.data
}

/**
 * 拒絕任務 (僅管理員)
 */
export async function rejectJob(jobId: number, reason: string) {
  const response = await api.post<{ message: string; job: Job }>(`/jobs/${jobId}/reject`, { reason })
  return response.data
}

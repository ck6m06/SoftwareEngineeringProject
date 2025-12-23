/**
 * Audit Logs API Client
 * 審計日誌 API 客戶端
 */

import client from './client'

/**
 * 審計日誌篩選條件
 */
export interface AuditLogFilters {
  actor_id?: number
  action?: string
  target_type?: string
  target_id?: number
  shelter_id?: number
  start_time?: string  // ISO 8601 format
  end_time?: string    // ISO 8601 format
  page?: number
  per_page?: number
}

/**
 * 審計日誌項目
 */
export interface AuditLog {
  audit_log_id: number
  actor_id: number | null
  actor_email?: string
  action: string
  target_type: string | null
  target_id: number | null
  shelter_id: number | null
  before_state: Record<string, any> | null
  after_state: Record<string, any> | null
  notes: string | null
  timestamp: string
}

/**
 * 審計日誌查詢回應
 */
export interface AuditLogsResponse {
  audit_logs: AuditLog[]
  pagination: {
    page: number
    per_page: number
    total: number
    pages: number
  }
}

/**
 * 查詢審計日誌
 * @param filters 篩選條件
 * @returns 審計日誌列表與分頁資訊
 */
export async function getAuditLogs(filters?: AuditLogFilters): Promise<AuditLogsResponse> {
  const params = new URLSearchParams()
  
  if (filters?.actor_id) params.append('actor_id', filters.actor_id.toString())
  if (filters?.action) params.append('action', filters.action)
  if (filters?.target_type) params.append('target_type', filters.target_type)
  if (filters?.target_id) params.append('target_id', filters.target_id.toString())
  if (filters?.shelter_id) params.append('shelter_id', filters.shelter_id.toString())
  if (filters?.start_time) params.append('start_time', filters.start_time)
  if (filters?.end_time) params.append('end_time', filters.end_time)
  if (filters?.page) params.append('page', filters.page.toString())
  if (filters?.per_page) params.append('per_page', filters.per_page.toString())
  
  const response = await client.get(`/admin/audit?${params.toString()}`)
  return response.data
}

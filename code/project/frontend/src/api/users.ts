/**
 * Users API Client
 * 使用者 API 客戶端
 */

import client from './client'

/**
 * 使用者資料
 */
export interface User {
  user_id: number
  email: string
  username: string | null
  phone_number: string | null
  first_name: string | null
  last_name: string | null
  region: string | null
  address: {
    district?: string
    street?: string
    postal_code?: string
    city?: string
    country?: string
  } | null
  role: 'ADMIN' | 'SHELTER_MEMBER' | 'GENERAL_MEMBER'
  verified: boolean
  primary_shelter_id: number | null
  profile_photo_url: string | null
  settings: Record<string, any> | null
  created_at: string
  updated_at: string
}

/**
 * 使用者更新資料
 */
export interface UserUpdateData {
  username?: string
  phone_number?: string
  first_name?: string
  last_name?: string
  region?: string
  address?: {
    district?: string
    street?: string
    postal_code?: string
    city?: string
    country?: string
  }
  profile_photo_url?: string
  settings?: Record<string, any>
}

/**
 * 變更密碼資料
 */
export interface ChangePasswordData {
  old_password: string
  new_password: string
}

/**
 * 取得使用者資料
 * @param userId 使用者 ID
 * @returns 使用者資料
 */
export async function getUser(userId: number): Promise<User> {
  const response = await client.get(`/users/${userId}`)
  // 後端直接返回 user 資料,不是包在 user key 中
  return response.data
}

/**
 * 更新使用者資料
 * @param userId 使用者 ID
 * @param data 更新資料
 * @returns 更新後的使用者資料
 */
export async function updateUser(userId: number, data: UserUpdateData): Promise<User> {
  const response = await client.patch(`/users/${userId}`, data)
  // 後端直接返回 user 資料
  return response.data
}

/**
 * 變更密碼
 * @param userId 使用者 ID
 * @param data 變更密碼資料
 * @returns 成功訊息
 */
export async function changePassword(userId: number, data: ChangePasswordData): Promise<{ message: string }> {
  const response = await client.patch(`/users/${userId}/password`, data)
  return response.data
}

/**
 * 請求匯出個人資料
 * @param userId 使用者 ID
 * @returns Job ID
 */
export async function requestDataExport(userId: number): Promise<{ job_id: number; message: string }> {
  const response = await client.post(`/users/${userId}/data/export`)
  return response.data
}

/**
 * 請求刪除帳號
 * @param userId 使用者 ID
 * @param reason 刪除原因
 * @returns Job ID
 */
export async function requestAccountDeletion(userId: number, reason?: string): Promise<{ job_id: number; message: string }> {
  const response = await client.post(`/users/${userId}/data/delete`, { reason })
  return response.data
}

/**
 * 審核者資料
 */
export interface Reviewer {
  user_id: number
  username: string
  email: string
  role: 'ADMIN' | 'SHELTER_MEMBER'
  shelter_id?: number | null
}

/**
 * 取得所有審核者列表 (管理員 + 收容所會員)
 * @returns 審核者列表
 */
export async function getReviewers(): Promise<Reviewer[]> {
  const response = await client.get('/admin/reviewers')
  return response.data.reviewers
}

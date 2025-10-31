/**
 * Type Definitions - Models
 */

export interface User {
  user_id: number
  email: string
  username?: string
  phone_number?: string
  first_name?: string
  last_name?: string
  role: 'GENERAL_MEMBER' | 'SHELTER_MEMBER' | 'ADMIN'
  verified: boolean
  primary_shelter_id?: number
  profile_photo_url?: string
  created_at: string
  updated_at: string
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
  images?: AnimalImage[]
  shelter?: Shelter
  has_pending_application?: boolean
}

export interface AnimalImage {
  animal_image_id: number
  animal_id: number
  storage_key: string
  url: string
  mime_type?: string
  width?: number
  height?: number
  order: number
  created_at: string
}

export interface Shelter {
  shelter_id: number
  name: string
  slug?: string
  contact_email: string
  contact_phone: string
  address: {
    street?: string
    city?: string
    county?: string
    postal_code?: string
  }
  region?: string
  verified: boolean
  primary_account_user_id?: number
  created_at: string
  updated_at: string
}

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
  attachments?: any[]
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
  applicant?: User
  animal?: Animal
  assignee?: User
}

export interface MedicalRecord {
  medical_record_id: number
  animal_id: number
  record_type?: 'TREATMENT' | 'CHECKUP' | 'VACCINE' | 'SURGERY' | 'OTHER'
  date?: string
  provider?: string
  details?: string
  attachments?: any[]
  verified: boolean
  verified_by?: number
  created_by?: number
  created_at: string
  updated_at: string
}

export interface Notification {
  notification_id: number
  recipient_id: number
  actor_id?: number
  type: string
  payload?: any
  read: boolean
  created_at: string
  read_at?: string
}

export interface Job {
  job_id: number
  type: string
  status: 'PENDING' | 'RUNNING' | 'SUCCEEDED' | 'FAILED'
  payload?: any
  result_summary?: any
  created_by?: number
  created_at: string
  started_at?: string
  finished_at?: string
  attempts: number
}

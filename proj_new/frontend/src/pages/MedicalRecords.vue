<template>
  <div class="medical-records-page">
    <div class="container">
      <!-- 頁面標題 -->
      <div class="page-header">
        <h1 class="page-title">醫療記錄管理</h1>
        <p class="page-description">查看與管理動物的醫療記錄</p>
      </div>

      <!-- 動物選擇器 -->
      <div class="animal-selector">
        <label for="animal-select" class="selector-label">選擇動物:</label>
        <select 
          id="animal-select" 
          v-model="selectedAnimalId" 
          class="animal-select"
          @change="loadMedicalRecords"
        >
          <option :value="null">-- 請選擇動物 --</option>
          <option v-for="animal in animals" :key="animal.animal_id" :value="animal.animal_id">
            {{ animal.name || `動物 #${animal.animal_id}` }} 
            ({{ getSpeciesLabel(animal.species) }})
          </option>
        </select>
      </div>

      <!-- 新增記錄按鈕 (擁有者或管理員) -->
      <div v-if="selectedAnimalId && canManageRecords" class="action-bar">
        <button @click="openAddModal" class="btn-primary">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          新增醫療記錄
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-container">
        <div class="spinner"></div>
        <p>載入中...</p>
      </div>

      <!-- 空狀態 -->
      <div v-else-if="!selectedAnimalId" class="empty-state">
        <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="empty-text">請先選擇一個動物</p>
      </div>

      <div v-else-if="records.length === 0" class="empty-state">
        <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="empty-text">此動物尚無醫療記錄</p>
        <button v-if="canManageRecords" @click="openAddModal" class="btn-secondary">
          新增第一筆記錄
        </button>
      </div>

      <!-- 醫療記錄時間線 -->
      <div v-else class="timeline-container">
        <div class="timeline">
          <div 
            v-for="record in records" 
            :key="record.medical_record_id" 
            class="timeline-item"
          >
            <div class="timeline-marker"></div>
            <div class="timeline-content">
              <div class="record-card">
                <div class="record-header">
                  <div class="record-type-badge" :class="getRecordTypeClass(record.record_type)">
                    {{ getRecordTypeLabel(record.record_type) }}
                  </div>
                  <div class="record-date">{{ formatDate(record.date) }}</div>
                  <div v-if="record.verified" class="verified-badge">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                    已驗證
                  </div>
                </div>

                <div class="record-body">
                  <div v-if="record.provider" class="record-provider">
                    <strong>醫療提供者:</strong> {{ record.provider }}
                  </div>
                  <div v-if="record.details" class="record-details">
                    <strong>詳細說明:</strong>
                    <p>{{ record.details }}</p>
                  </div>
                  <div v-if="record.attachments && record.attachments.length > 0" class="record-attachments">
                    <strong>附件:</strong>
                    <ul>
                      <li v-for="(attachment, index) in record.attachments" :key="index">
                        📎 {{ attachment.filename || attachment.storage_key || '附件' }}
                      </li>
                    </ul>
                  </div>
                </div>

                <div class="record-footer">
                  <div class="record-meta">
                    <span class="meta-item">建立於 {{ formatDateTime(record.created_at) }}</span>
                  </div>
                  <div class="record-actions">
                    <button 
                      v-if="canEditRecord(record)" 
                      @click="openEditModal(record)" 
                      class="btn-icon"
                      title="編輯"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button 
                      v-if="isAdmin && !record.verified" 
                      @click="handleVerify(record.medical_record_id, true)" 
                      class="btn-icon verify"
                      title="驗證"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新增/編輯記錄 Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">{{ isEditing ? '編輯醫療記錄' : '新增醫療記錄' }}</h2>
          <button @click="closeModal" class="modal-close">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="modal-body">
          <div class="form-group">
            <label for="record-type" class="form-label">記錄類型 *</label>
            <select id="record-type" v-model="formData.record_type" class="form-select" required>
              <option value="">-- 請選擇 --</option>
              <option value="TREATMENT">治療</option>
              <option value="CHECKUP">健康檢查</option>
              <option value="VACCINE">疫苗接種</option>
              <option value="SURGERY">手術</option>
              <option value="OTHER">其他</option>
            </select>
          </div>

          <div class="form-group">
            <label for="record-date" class="form-label">日期 *</label>
            <input 
              id="record-date" 
              v-model="formData.date" 
              type="date" 
              class="form-input" 
              required
              :max="today"
            />
          </div>

          <div class="form-group">
            <label for="provider" class="form-label">醫療提供者</label>
            <input 
              id="provider" 
              v-model="formData.provider" 
              type="text" 
              class="form-input" 
              placeholder="例如: 台北動物醫院 - 王醫師"
            />
          </div>

          <div class="form-group">
            <label for="details" class="form-label">詳細說明</label>
            <textarea 
              id="details" 
              v-model="formData.details" 
              class="form-textarea" 
              rows="4"
              placeholder="請描述治療內容、診斷結果或注意事項..."
            ></textarea>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn-secondary">取消</button>
            <button type="submit" class="btn-primary" :disabled="submitting">
              {{ submitting ? '處理中...' : (isEditing ? '更新' : '新增') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getAnimals, type Animal as ApiAnimal } from '@/api/animals'
import { 
  getMedicalRecords, 
  createMedicalRecord, 
  updateMedicalRecord, 
  verifyMedicalRecord,
  type CreateMedicalRecordData 
} from '@/api/medicalRecords'
import type { MedicalRecord } from '@/types/models'

// Store & Router
const authStore = useAuthStore()
const route = useRoute()

// State
const animals = ref<ApiAnimal[]>([])
const selectedAnimalId = ref<number | null>(null)
const records = ref<MedicalRecord[]>([])
const loading = ref(false)
const showModal = ref(false)
const isEditing = ref(false)
const editingRecordId = ref<number | null>(null)
const submitting = ref(false)
const formData = ref<CreateMedicalRecordData>({
  record_type: undefined,
  date: undefined,
  provider: '',
  details: '',
  attachments: []
})

// Computed
const canManageRecords = computed(() => {
  // 管理員可以管理所有動物的醫療紀錄
  if (authStore.user?.role === 'ADMIN') {
    return true
  }
  
  // 一般會員(包含收容所會員)可以管理自己擁有的動物的醫療紀錄
  if (selectedAnimalId.value) {
    const selectedAnimal = animals.value.find(a => a.animal_id === selectedAnimalId.value)
    if (selectedAnimal && selectedAnimal.owner_id === authStore.user?.user_id) {
      return true
    }
  }
  
  return false
})

const isAdmin = computed(() => {
  return authStore.user?.role === 'ADMIN'
})

const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

// Methods
async function loadAnimals() {
  try {
    const response = await getAnimals({ per_page: 100 })
    animals.value = response.animals
  } catch (error) {
    console.error('載入動物列表失敗:', error)
    alert('載入動物列表失敗')
  }
}

async function loadMedicalRecords() {
  if (!selectedAnimalId.value) {
    records.value = []
    return
  }

  loading.value = true
  try {
    const response = await getMedicalRecords(selectedAnimalId.value)
    records.value = response.medical_records || []
  } catch (error) {
    console.error('載入醫療記錄失敗:', error)
    alert('載入醫療記錄失敗')
    records.value = []
  } finally {
    loading.value = false
  }
}

function canEditRecord(record: MedicalRecord): boolean {
  if (authStore.user?.role === 'ADMIN') return true
  // 所有用戶(包括收容所會員)只能編輯自己創建的醫療記錄
  if (record.created_by === authStore.user?.user_id) return true
  return false
}

function openAddModal() {
  isEditing.value = false
  editingRecordId.value = null
  formData.value = {
    record_type: undefined,
    date: today.value,
    provider: '',
    details: '',
    attachments: []
  }
  showModal.value = true
}

function openEditModal(record: MedicalRecord) {
  isEditing.value = true
  editingRecordId.value = record.medical_record_id
  formData.value = {
    record_type: record.record_type,
    date: record.date,
    provider: record.provider || '',
    details: record.details || '',
    attachments: record.attachments || []
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  isEditing.value = false
  editingRecordId.value = null
}

async function handleSubmit() {
  if (!selectedAnimalId.value) return

  submitting.value = true
  try {
    if (isEditing.value && editingRecordId.value) {
      await updateMedicalRecord(editingRecordId.value, formData.value)
      alert('醫療記錄更新成功')
    } else {
      await createMedicalRecord(selectedAnimalId.value, formData.value)
      alert('醫療記錄新增成功')
    }
    closeModal()
    await loadMedicalRecords()
  } catch (error: any) {
    console.error('處理醫療記錄失敗:', error)
    alert(error.response?.data?.message || '處理醫療記錄失敗')
  } finally {
    submitting.value = false
  }
}

async function handleVerify(recordId: number, verified: boolean) {
  if (!confirm(`確定要${verified ? '驗證' : '取消驗證'}此醫療記錄嗎?`)) return

  try {
    await verifyMedicalRecord(recordId, verified)
    alert(`醫療記錄已${verified ? '驗證' : '取消驗證'}`)
    await loadMedicalRecords()
  } catch (error: any) {
    console.error('驗證失敗:', error)
    alert(error.response?.data?.message || '驗證失敗')
  }
}

// Helpers
function getRecordTypeLabel(type?: string): string {
  const labels: Record<string, string> = {
    TREATMENT: '治療',
    CHECKUP: '健康檢查',
    VACCINE: '疫苗接種',
    SURGERY: '手術',
    OTHER: '其他'
  }
  return type ? labels[type] || type : '未分類'
}

function getRecordTypeClass(type?: string): string {
  const classes: Record<string, string> = {
    TREATMENT: 'type-treatment',
    CHECKUP: 'type-checkup',
    VACCINE: 'type-vaccine',
    SURGERY: 'type-surgery',
    OTHER: 'type-other'
  }
  return type ? classes[type] || 'type-default' : 'type-default'
}

function getSpeciesLabel(species?: string): string {
  return species === 'DOG' ? '狗' : species === 'CAT' ? '貓' : '未知'
}

function formatDate(dateString?: string): string {
  if (!dateString) return '未記錄日期'
  return new Date(dateString).toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

function formatDateTime(dateString?: string): string {
  if (!dateString) return '未知時間'
  return new Date(dateString).toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Lifecycle
onMounted(async () => {
  await loadAnimals()
  
  // 檢查 URL 參數,如果有 animal_id,自動選擇該動物
  const animalIdFromQuery = route.query.animal_id
  if (animalIdFromQuery) {
    const animalId = parseInt(animalIdFromQuery as string, 10)
    if (!isNaN(animalId) && animals.value.some(a => a.animal_id === animalId)) {
      selectedAnimalId.value = animalId
      await loadMedicalRecords()
    }
  }
})
</script>

<style scoped>
.medical-records-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* Page Header */
.page-header {
  text-align: center;
  margin-bottom: 2rem;
  color: white;
}

.page-title {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.page-description {
  font-size: 1.125rem;
  opacity: 0.9;
}

/* Animal Selector */
.animal-selector {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.selector-label {
  font-weight: 600;
  color: #374151;
  font-size: 1rem;
}

.animal-select {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s;
}

.animal-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Action Bar */
.action-bar {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: flex-end;
}

/* Buttons */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background: white;
  color: #374151;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.btn-icon {
  padding: 0.5rem;
  background: transparent;
  border: none;
  color: #6b7280;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: #f3f4f6;
  color: #374151;
}

.btn-icon.verify {
  color: #10b981;
}

.btn-icon.verify:hover {
  background: #d1fae5;
  color: #059669;
}

/* Loading */
.loading-container {
  background: white;
  padding: 4rem 2rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.spinner {
  width: 3rem;
  height: 3rem;
  border: 4px solid #e5e7eb;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Empty State */
.empty-state {
  background: white;
  padding: 4rem 2rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  width: 5rem;
  height: 5rem;
  color: #d1d5db;
  margin: 0 auto 1rem;
}

.empty-text {
  font-size: 1.125rem;
  color: #6b7280;
  margin-bottom: 1.5rem;
}

/* Timeline */
.timeline-container {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.timeline {
  position: relative;
  padding-left: 2rem;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 0.5rem;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e5e7eb;
}

.timeline-item {
  position: relative;
  margin-bottom: 2rem;
}

.timeline-marker {
  position: absolute;
  left: -1.625rem;
  top: 0.5rem;
  width: 1rem;
  height: 1rem;
  background: white;
  border: 3px solid #667eea;
  border-radius: 50%;
  z-index: 1;
}

.timeline-content {
  margin-left: 1rem;
}

/* Record Card */
.record-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.record-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}

.record-type-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
}

.type-treatment {
  background: #fee2e2;
  color: #991b1b;
}

.type-checkup {
  background: #dbeafe;
  color: #1e40af;
}

.type-vaccine {
  background: #d1fae5;
  color: #065f46;
}

.type-surgery {
  background: #fed7aa;
  color: #92400e;
}

.type-other {
  background: #e5e7eb;
  color: #374151;
}

.record-date {
  font-weight: 600;
  color: #374151;
}

.verified-badge {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  background: #d1fae5;
  color: #065f46;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
  margin-left: auto;
}

.record-body {
  padding: 1rem;
}

.record-body > div {
  margin-bottom: 0.75rem;
}

.record-body > div:last-child {
  margin-bottom: 0;
}

.record-provider,
.record-details,
.record-attachments {
  color: #374151;
}

.record-details p {
  margin-top: 0.5rem;
  line-height: 1.6;
  white-space: pre-wrap;
}

.record-attachments ul {
  margin-top: 0.5rem;
  padding-left: 1.5rem;
}

.record-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: white;
  border-top: 1px solid #e5e7eb;
}

.record-meta {
  font-size: 0.875rem;
  color: #6b7280;
}

.record-actions {
  display: flex;
  gap: 0.5rem;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: #111827;
}

.modal-close {
  padding: 0.5rem;
  background: transparent;
  border: none;
  color: #6b7280;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-body {
  padding: 1.5rem;
}

/* Form */
.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

/* Responsive */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }
  
  .animal-selector {
    flex-direction: column;
    align-items: stretch;
  }
  
  .timeline {
    padding-left: 1.5rem;
  }
  
  .timeline-marker {
    left: -1.375rem;
  }
  
  .record-header {
    flex-wrap: wrap;
  }
  
  .verified-badge {
    margin-left: 0;
  }
}
</style>
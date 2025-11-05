<template>
  <div class="rehome-form-page max-w-4xl mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">
      {{ isEditMode ? '編輯送養資訊' : '刊登送養資訊' }}
    </h1>

    <!-- 收容所會員提示 -->
    <div v-if="authStore.user?.role === 'SHELTER_MEMBER'" class="bg-amber-50 border border-amber-200 rounded-lg p-6 mb-8">
      <div class="flex items-start gap-3">
        <div class="text-2xl">⚠️</div>
        <div>
          <h2 class="text-lg font-semibold text-amber-900 mb-2">收容所會員注意事項</h2>
          <p class="text-amber-800 mb-3">您正在進行<strong>單次送養</strong>操作。根據系統設計：</p>
          <ul class="list-disc list-inside text-amber-800 space-y-1 mb-3">
            <li>此動物仍然歸屬於收容所機構</li>
            <li>可在「收容所動物管理」中進行批次操作</li>
            <li>如需批次匯入，請使用收容所管理功能</li>
          </ul>
          <button
            type="button"
            @click="router.push('/shelter/animals')"
            class="inline-flex items-center px-4 py-2 bg-amber-600 text-white rounded-md hover:bg-amber-700 transition text-sm"
          >
            🐾 前往收容所動物管理
          </button>
        </div>
      </div>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-8">
      <!-- 步驟指示器 -->
      <div class="steps flex items-center justify-between mb-8">
        <div
          v-for="(step, index) in steps"
          :key="index"
          class="step-item flex items-center"
          :class="{ active: currentStep === index, completed: currentStep > index }"
        >
          <div class="step-number">{{ index + 1 }}</div>
          <span class="step-label ml-2">{{ step }}</span>
          <div v-if="index < steps.length - 1" class="step-line"></div>
        </div>
      </div>

      <!-- 步驟 1: 基本資訊 -->
      <div v-show="currentStep === 0" class="form-section">
        <h2 class="text-xl font-semibold mb-4">動物基本資訊</h2>
        
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label required">名稱</label>
            <input
              v-model="formData.name"
              type="text"
              class="form-input"
              placeholder="例: 小白"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label required">物種</label>
            <select v-model="formData.species" class="form-input" required>
              <option value="">請選擇</option>
              <option value="CAT">貓</option>
              <option value="DOG">狗</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label required">品種</label>
            <input
              v-model="formData.breed"
              type="text"
              class="form-input"
              placeholder="例: 米克斯、波斯貓、黃金獵犬"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label required">性別</label>
            <select v-model="formData.sex" class="form-input" required>
              <option value="">請選擇</option>
              <option value="MALE">公</option>
              <option value="FEMALE">母</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label required">出生日期</label>
            <input
              v-model="formData.dob"
              type="date"
              class="form-input"
              :max="today"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label required">顏色</label>
            <input
              v-model="formData.color"
              type="text"
              class="form-input"
              placeholder="例: 白色、橘色、三花"
              required
            />
          </div>
        </div>

        <div class="form-group mt-4">
          <label class="form-label required">描述</label>
          <textarea
            v-model="formData.description"
            class="form-input"
            rows="4"
            placeholder="請描述動物的個性、習慣、特徵等..."
            required
          ></textarea>
        </div>
      </div>

      <!-- 步驟 2: 照片上傳 -->
      <div v-show="currentStep === 1" class="form-section">
        <h2 class="text-xl font-semibold mb-4">上傳照片</h2>
        <p class="text-gray-600 mb-4">
          {{ isEditMode ? '選擇新照片(選填)。點擊「儲存草稿」會立即上傳照片。' : '請選擇清晰的動物照片,至少一張。點擊「儲存草稿」會立即上傳照片。' }}
        </p>
        
        <!-- 現有照片 (編輯模式) -->
        <div v-if="isEditMode && uploadedPhotos.length > 0" class="mb-4">
          <h3 class="text-sm font-semibold text-gray-700 mb-2">現有照片</h3>
          <div class="grid grid-cols-3 gap-2">
            <div v-for="(photo, index) in uploadedPhotos" :key="index" class="relative">
              <img :src="photo.url" :alt="`Photo ${index + 1}`" class="w-full h-24 object-cover rounded" />
            </div>
          </div>
        </div>
        
        <FileUploader
          ref="fileUploader"
          accept="image/*"
          :multiple="true"
          :max-size="5 * 1024 * 1024"
          :auto-upload="false"
          @uploaded="onPhotosUploaded"
          @error="onUploadError"
        />

        <div v-if="fileUploader?.files && fileUploader.files.length > 0" class="mt-4">
          <p class="text-sm text-green-600">✓ 已選擇 {{ fileUploader.files.length }} 張新照片</p>
          <p class="text-xs text-blue-600">💡 提示: 點擊「儲存草稿」按鈕會立即上傳這些照片</p>
        </div>
        
        <div v-if="!isEditMode && uploadedPhotos.length === 0 && (!fileUploader?.files || fileUploader.files.length === 0)" class="mt-4">
          <p class="text-sm text-orange-600">⚠️ 建議至少上傳一張照片以提高領養機會</p>
        </div>
      </div>

      <!-- 步驟 3: 醫療紀錄管理 -->
      <div v-show="currentStep === 2" class="form-section">
        <h2 class="text-xl font-semibold mb-6">醫療紀錄管理</h2>
        
        <div class="medical-records-manager">
          <!-- 新增模式提示 -->
          <div v-if="!editingAnimalId" class="info-box mb-4">
            <p class="text-sm text-blue-800">
              <strong>提示:</strong> 您現在可以直接新增醫療紀錄。這些紀錄會在確認送出時一併儲存。
            </p>
          </div>

          <!-- 醫療紀錄管理介面 -->
          <div class="medical-records-container">
            <!-- 新增記錄按鈕 -->
            <div class="action-bar mb-4">
              <button type="button" @click="openMedicalModal" class="btn-add-record">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                新增醫療記錄
              </button>
            </div>

            <!-- Loading -->
            <div v-if="loadingRecords" class="loading-container">
              <div class="spinner"></div>
              <p>載入醫療記錄中...</p>
            </div>

            <!-- 空狀態 -->
            <div v-else-if="allMedicalRecords.length === 0" class="empty-state">
              <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p class="empty-text">尚無醫療記錄</p>
              <button type="button" @click="openMedicalModal" class="btn-secondary mt-3">
                新增第一筆記錄
              </button>
            </div>

            <!-- 醫療記錄列表 -->
            <div v-else class="medical-records-list">
              <div 
                v-for="(record, index) in allMedicalRecords" 
                :key="record.medical_record_id || `temp-${index}`" 
                class="medical-record-card"
              >
                <div class="record-header">
                  <div class="record-type-badge" :class="getMedicalRecordTypeClass(record.record_type)">
                    {{ getMedicalRecordTypeLabel(record.record_type) }}
                  </div>
                  <div class="record-date">{{ formatMedicalDate(record.date) }}</div>
                  <!-- 暫存標籤 -->
                  <div v-if="!editingAnimalId" class="temp-badge">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
                    </svg>
                    暫存
                  </div>
                  <div v-else-if="record.verified" class="verified-badge">
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
                  
                  <!-- 附件顯示 -->
                  <div v-if="record.attachments && record.attachments.length > 0" class="record-attachments">
                    <strong class="block mb-2">相關文件:</strong>
                    <div class="attachments-grid">
                      <a 
                        v-for="(attachment, idx) in record.attachments" 
                        :key="idx"
                        :href="attachment.url" 
                        target="_blank" 
                        class="attachment-link"
                      >
                        <svg v-if="attachment.mime_type?.startsWith('image')" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span class="text-sm">{{ attachment.filename || attachment.name || `附件 ${idx + 1}` }}</span>
                      </a>
                    </div>
                  </div>
                </div>

                <div class="record-footer">
                  <div class="record-meta">
                    <span v-if="!editingAnimalId" class="meta-item text-orange-600">將在送出時儲存</span>
                    <span v-else class="meta-item">建立於 {{ formatMedicalDateTime(record.created_at) }}</span>
                  </div>
                  <div class="record-actions">
                    <button 
                      type="button"
                      @click="editingAnimalId ? openEditMedicalModal(record) : openEditTempMedicalModal(index)" 
                      class="btn-icon-small"
                      title="編輯"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button 
                      v-if="!editingAnimalId"
                      type="button"
                      @click="removeTempMedicalRecord(index)" 
                      class="btn-icon-small text-red-600"
                      title="刪除"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 步驟 4: 確認送出 -->
      <div v-show="currentStep === 3" class="form-section">
        <h2 class="text-xl font-semibold mb-4">確認資訊</h2>
        
        <div class="preview-card">
          <div class="preview-section">
            <h3 class="font-semibold mb-2">基本資訊</h3>
            <div class="preview-grid">
              <div><span class="text-gray-600">名稱:</span> {{ formData.name }}</div>
              <div><span class="text-gray-600">物種:</span> {{ speciesText }}</div>
              <div><span class="text-gray-600">品種:</span> {{ formData.breed || '未提供' }}</div>
              <div><span class="text-gray-600">性別:</span> {{ sexText }}</div>
              <div><span class="text-gray-600">出生日期:</span> {{ formData.dob || '未提供' }}</div>
              <div><span class="text-gray-600">顏色:</span> {{ formData.color || '未提供' }}</div>
            </div>
            <p class="mt-2"><span class="text-gray-600">描述:</span> {{ formData.description }}</p>
          </div>

          <div class="preview-section mt-4">
            <h3 class="font-semibold mb-2">照片</h3>
            <div v-if="isEditMode && uploadedPhotos.length > 0">
              <p class="text-sm text-gray-600">現有照片: {{ uploadedPhotos.length }} 張</p>
            </div>
            <div v-if="fileUploader?.files?.length">
              <p class="text-sm" :class="isEditMode ? 'text-blue-600' : 'text-green-600'">
                {{ isEditMode ? '將新增' : '已選擇' }} {{ fileUploader.files.length }} 張照片
              </p>
            </div>
            <p v-if="!fileUploader?.files?.length && !uploadedPhotos.length" class="text-sm text-red-600">
              尚未選擇照片
            </p>
          </div>

          <div v-if="formData.medical_summary" class="preview-section mt-4">
            <h3 class="font-semibold mb-2">醫療資訊</h3>
            <p>{{ formData.medical_summary }}</p>
            <p v-if="formData.is_neutered" class="text-green-600 mt-1">✓ 已結紮</p>
          </div>
        </div>

        <div class="mt-4 p-4 bg-blue-50 border border-blue-200 rounded">
          <p class="text-sm text-blue-800">
            <strong>注意:</strong> 送出後資訊將進入審核,審核通過後才會公開顯示。
          </p>
        </div>
      </div>

      <!-- 錯誤訊息 -->
      <div v-if="errorMessage" class="alert alert-error">
        {{ errorMessage }}
      </div>

      <!-- 按鈕群組 -->
      <div class="form-actions flex justify-between">
        <button
          v-if="currentStep > 0"
          type="button"
          class="btn-secondary"
          @click="prevStep"
        >
          上一步
        </button>
        <div v-else></div>

        <div class="flex gap-2">
          <button
            type="button"
            class="btn-secondary"
            @click="saveDraft"
            :disabled="isSubmitting"
          >
            儲存草稿
          </button>
          
          <button
            v-if="currentStep < steps.length - 1"
            type="button"
            class="btn-primary"
            @click="nextStep"
          >
            下一步
          </button>
          
          <button
            v-else
            type="submit"
            class="btn-primary"
            :disabled="isSubmitting || (!isEditMode && !fileUploader?.files?.length && !uploadedPhotos.length)"
          >
            {{ isSubmitting ? '送出中...' : isEditMode ? '儲存修改' : '確認送出' }}
          </button>
        </div>
      </div>
    </form>

    <!-- 醫療紀錄 Modal -->
    <div v-if="showMedicalModal" class="modal-overlay" @click.self="closeMedicalModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">{{ isEditingMedical ? '編輯醫療記錄' : '新增醫療記錄' }}</h2>
          <button type="button" @click="closeMedicalModal" class="modal-close">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="handleMedicalSubmit" class="modal-body">
          <div class="form-group">
            <label for="medical-record-type" class="form-label required">記錄類型</label>
            <select id="medical-record-type" v-model="medicalFormData.record_type" class="form-select" required>
              <option value="">-- 請選擇 --</option>
              <option value="TREATMENT">治療</option>
              <option value="CHECKUP">健康檢查</option>
              <option value="VACCINE">疫苗接種</option>
              <option value="SURGERY">手術</option>
              <option value="OTHER">其他</option>
            </select>
          </div>

          <div class="form-group">
            <label for="medical-record-date" class="form-label required">日期</label>
            <input 
              id="medical-record-date" 
              v-model="medicalFormData.date" 
              type="date" 
              class="form-input" 
              required
              :max="todayDate"
            />
          </div>

          <div class="form-group">
            <label for="medical-provider" class="form-label">醫療提供者</label>
            <input 
              id="medical-provider" 
              v-model="medicalFormData.provider" 
              type="text" 
              class="form-input" 
              placeholder="例如: 台北動物醫院 - 王醫師"
            />
          </div>

          <div class="form-group">
            <label for="medical-details" class="form-label">詳細說明</label>
            <textarea 
              id="medical-details" 
              v-model="medicalFormData.details" 
              class="form-textarea" 
              rows="4"
              placeholder="請描述治療內容、診斷結果或注意事項..."
            ></textarea>
          </div>

          <!-- 文件上傳 -->
          <div class="form-group">
            <label class="form-label">相關證明文件或圖片</label>
            <p class="text-sm text-gray-600 mb-2">請上傳醫療證明、檢驗報告或相關照片</p>
            <FileUploader
              ref="medicalFileUploader"
              accept="image/*,.pdf"
              :multiple="true"
              :max-size="10 * 1024 * 1024"
              :auto-upload="false"
              @uploaded="onMedicalFilesUploaded"
              @error="onMedicalUploadError"
            />
            
            <!-- 顯示現有附件(編輯模式) -->
            <div v-if="isEditingMedical && medicalFormData.attachments && medicalFormData.attachments.length > 0" class="mt-3">
              <p class="text-sm font-semibold text-gray-700 mb-2">現有附件:</p>
              <div class="existing-attachments">
                <div 
                  v-for="(attachment, index) in medicalFormData.attachments" 
                  :key="index" 
                  class="attachment-item"
                >
                  <a :href="attachment.url" target="_blank" class="text-blue-600 hover:underline text-sm">
                    📎 {{ attachment.filename || attachment.name || `附件 ${index + 1}` }}
                  </a>
                  <button 
                    type="button" 
                    @click="removeMedicalAttachment(index)" 
                    class="btn-remove-attachment"
                  >
                    ✕
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeMedicalModal" class="btn-secondary">取消</button>
            <button type="submit" class="btn-primary" :disabled="submittingMedical">
              {{ submittingMedical ? '處理中...' : (isEditingMedical ? '更新' : '新增') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { createAnimal, getAnimal, updateAnimal, addAnimalImage, submitAnimal } from '@/api/animals'
import { 
  getMedicalRecords, 
  createMedicalRecord, 
  updateMedicalRecord,
  type CreateMedicalRecordData 
} from '@/api/medicalRecords'
import type { MedicalRecord } from '@/types/models'
import { useUpload } from '@/composables/useUpload'
import FileUploader from '@/components/uploads/FileUploader.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 編輯模式相關 (基於 query 參數)
const isEditMode = computed(() => !!route.query.id)
const editingAnimalId = computed(() => route.query.id ? Number(route.query.id) : null)

const steps = ['基本資訊', '上傳照片', '醫療資訊', '確認送出']
const currentStep = ref(0)
const isSubmitting = ref(false)
const errorMessage = ref('')

const fileUploader = ref<InstanceType<typeof FileUploader>>()
const medicalFileUploader = ref<InstanceType<typeof FileUploader>>()
const uploadedPhotos = ref<any[]>([])
const medicalUploadError = ref('')

const today = new Date().toISOString().split('T')[0]

// 醫療紀錄相關狀態
const medicalRecords = ref<MedicalRecord[]>([])
const tempMedicalRecords = ref<any[]>([]) // 暫存的醫療紀錄(新增模式用)
const loadingRecords = ref(false)
const showMedicalModal = ref(false)
const isEditingMedical = ref(false)
const editingMedicalRecordId = ref<number | null>(null)
const editingTempRecordIndex = ref<number | null>(null) // 編輯暫存記錄的索引
const submittingMedical = ref(false)
const todayDate = computed(() => new Date().toISOString().split('T')[0])

const medicalFormData = ref<CreateMedicalRecordData>({
  record_type: undefined,
  date: undefined,
  provider: '',
  details: '',
  attachments: []
})

const formData = reactive<{
  name: string
  species: 'CAT' | 'DOG' | ''
  breed: string
  sex: 'MALE' | 'FEMALE' | ''
  dob: string
  color: string
  description: string
  medical_summary: string
  is_neutered: boolean
  source_type: 'PERSONAL'
}>({
  name: '',
  species: '',
  breed: '',
  sex: '',
  dob: '',
  color: '',
  description: '',
  medical_summary: '',
  is_neutered: false,
  source_type: 'PERSONAL',
})

const speciesText = computed(() => {
  return formData.species === 'CAT' ? '貓' : formData.species === 'DOG' ? '狗' : ''
})

const sexText = computed(() => {
  return formData.sex === 'MALE' ? '公' : formData.sex === 'FEMALE' ? '母' : ''
})

// 合併已儲存的醫療記錄和暫存的記錄
const allMedicalRecords = computed(() => {
  // 如果有動物ID,顯示已儲存的記錄
  if (editingAnimalId.value) {
    return medicalRecords.value
  }
  // 否則顯示暫存的記錄
  return tempMedicalRecords.value
})

onMounted(async () => {
  // 檢查是否已登入
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }

  // 檢查是否為編輯模式 (computed 會自動從 route.query.id 判斷)
  const animalId = route.query.id
  console.log('RehomeForm onMounted - animalId from route:', animalId)
  console.log('RehomeForm onMounted - current user:', authStore.user?.user_id, authStore.user?.role)
  
  if (animalId) {
    await loadAnimalData(Number(animalId))
  } else {
    // 新增模式：嘗試從 localStorage 載入草稿
    console.log('RehomeForm onMounted - loading draft from localStorage')
    loadDraft()
  }
})

async function loadAnimalData(id: number) {
  try {
    const animal = await getAnimal(id)
    
    // 檢查權限：個人動物或收容所動物
    const isOwner = animal.owner_id === authStore.user?.user_id
    const isShelterAnimal = animal.shelter_id && 
                           authStore.user?.role === 'SHELTER_MEMBER' && 
                           authStore.user?.primary_shelter_id === animal.shelter_id
    
    if (!isOwner && !isShelterAnimal) {
      alert('無權限編輯此動物資料')
      router.push('/my-rehomes')
      return
    }
    
    // 填充表單資料
    formData.name = animal.name || ''
    formData.species = animal.species || ''
    formData.breed = animal.breed || ''
    formData.sex = (animal.sex === 'MALE' || animal.sex === 'FEMALE') ? animal.sex : ''
    formData.dob = animal.dob || ''
    formData.color = animal.color || ''
    formData.description = animal.description || ''
    formData.medical_summary = animal.medical_summary || ''
    formData.is_neutered = false // 後端沒有這個欄位
    
    // 如果有圖片,顯示現有圖片
    if (animal.images && animal.images.length > 0) {
      uploadedPhotos.value = animal.images
    }
  } catch (error: any) {
    console.error('Load animal error:', error)
    
    // 更詳細的錯誤處理
    if (error.response?.status === 404) {
      alert('此動物資料不存在或已被刪除')
    } else if (error.response?.status === 403) {
      alert('無權限編輯此動物資料')
    } else {
      alert(error.response?.data?.message || '載入動物資料失敗')
    }
    
    // 返回到我的送養列表
    router.push('/my-rehomes')
  }
}

function nextStep() {
  // 驗證當前步驟
  if (currentStep.value === 0) {
    if (!formData.name || !formData.species || !formData.sex || !formData.description) {
      errorMessage.value = '請填寫所有必填欄位'
      return
    }
  }

  if (currentStep.value === 1) {
    // 檢查 FileUploader 中的檔案
    const uploaderFiles = fileUploader.value?.files || []
    // 新增模式必須有照片,編輯模式可以沒有(使用現有照片)
    if (!isEditMode.value && uploaderFiles.length === 0 && uploadedPhotos.value.length === 0) {
      errorMessage.value = '請至少選擇一張照片'
      return
    }
  }

  errorMessage.value = ''
  currentStep.value++
}

function prevStep() {
  currentStep.value--
  errorMessage.value = ''
}

function onPhotosUploaded(photos: any[]) {
  uploadedPhotos.value = photos
  console.log('Photos uploaded:', photos)
}

function onUploadError(error: string) {
  errorMessage.value = error
}

async function saveDraft() {
  // 基本驗證
  if (!formData.name || !formData.species) {
    alert('請至少填寫動物名稱和物種')
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    // 準備動物資料
    const animalData = {
      name: formData.name,
      species: formData.species as 'CAT' | 'DOG',
      breed: formData.breed || undefined,
      color: formData.color || undefined,
      sex: formData.sex || undefined,
      dob: formData.dob || undefined,
      description: formData.description || undefined,
      medical_summary: formData.medical_summary || undefined,
      status: 'DRAFT' as const,
    }

    let animalId: number

    // 如果是編輯模式,更新現有草稿
    if (isEditMode.value && editingAnimalId.value) {
      const result = await updateAnimal(editingAnimalId.value, animalData)
      animalId = result.animal.animal_id
      
      // 上傳新照片(如果有)
      const uploaderFiles = fileUploader.value?.files || []
      if (uploaderFiles.length > 0) {
        try {
          const { uploadMultiple } = useUpload()
          const files = uploaderFiles.map(item => item.file)
          const uploadResults = await uploadMultiple(files, 'ANIMAL', animalId)
          
          // 將上傳的圖片 URL 添加到 animal_images 表
          for (const result of uploadResults) {
            await addAnimalImage(animalId, { 
              image_url: result.url,
              storage_key: result.storage_key,
              mime_type: result.mime_type
            })
          }
          
          // 清空 FileUploader 並重新載入圖片
          if (fileUploader.value) {
            fileUploader.value.files = []
          }
          const animal = await getAnimal(animalId)
          uploadedPhotos.value = animal.images || []
        } catch (uploadError) {
          console.error('Photo upload error:', uploadError)
          alert('草稿已更新,但照片上傳失敗。請稍後再試。')
        }
      }
      
      alert('草稿已更新')
    } else {
      // 新增模式,創建新草稿
      const result = await createAnimal(animalData)
      animalId = result.animal.animal_id
      
      // 上傳照片(如果有)
      const uploaderFiles = fileUploader.value?.files || []
      if (uploaderFiles.length > 0) {
        try {
          const { uploadMultiple } = useUpload()
          const files = uploaderFiles.map(item => item.file)
          const uploadResults = await uploadMultiple(files, 'ANIMAL', animalId)
          
          // 將上傳的圖片 URL 添加到 animal_images 表
          for (const result of uploadResults) {
            await addAnimalImage(animalId, { 
              image_url: result.url,
              storage_key: result.storage_key,
              mime_type: result.mime_type
            })
          }
          
          // 清空 FileUploader 並設置已上傳的圖片
          if (fileUploader.value) {
            fileUploader.value.files = []
          }
          const animal = await getAnimal(animalId)
          uploadedPhotos.value = animal.images || []
        } catch (uploadError) {
          console.error('Photo upload error:', uploadError)
          alert('草稿已儲存,但照片上傳失敗。請稍後再試。')
        }
      }
      
      // 儲存草稿 ID 後,導航到編輯模式
      await router.replace({ path: '/rehome-form', query: { id: animalId } })
      
      // 等待路由更新後載入醫療記錄
      await loadMedicalRecords()
      
      alert('草稿已儲存到資料庫,現在可以新增醫療記錄了')
    }

    // 同時儲存到 localStorage 作為備份
    const draft = {
      animalId: animalId,
      formData: { ...formData },
      uploadedPhotos: uploadedPhotos.value,
      currentStep: currentStep.value,
    }
    localStorage.setItem('rehome_draft', JSON.stringify(draft))

  } catch (error: any) {
    console.error('Save draft error:', error)
    
    // 處理動物不存在的情況
    if (error.response?.status === 404) {
      alert('此動物資料不存在或已被刪除,將建立新的草稿')
      // 切換為新增模式 - 清除 query 參數
      router.replace('/rehome-form')
      localStorage.removeItem('rehome_draft')
      // 嘗試重新儲存為新草稿
      try {
        const animalData = {
          name: formData.name,
          species: formData.species as 'CAT' | 'DOG',
          breed: formData.breed || undefined,
          color: formData.color || undefined,
          sex: formData.sex || undefined,
          dob: formData.dob || undefined,
          description: formData.description || undefined,
          medical_summary: formData.medical_summary || undefined,
          status: 'DRAFT' as const,
        }
        const result = await createAnimal(animalData)
        const newAnimalId = result.animal.animal_id
        
        // 導航到編輯模式
        router.replace({ path: '/rehome-form', query: { id: newAnimalId } })
        alert('已建立新的草稿')
      } catch (retryError) {
        alert('建立新草稿失敗')
      }
    } else {
      errorMessage.value = error.response?.data?.message || '儲存草稿失敗'
      alert('儲存草稿失敗: ' + errorMessage.value)
    }
  } finally {
    isSubmitting.value = false
  }
}

function loadDraft() {
  const draftStr = localStorage.getItem('rehome_draft')
  console.log('loadDraft - raw draft string:', draftStr)
  if (!draftStr) return

  try {
    const draft = JSON.parse(draftStr)
    console.log('loadDraft - parsed draft:', draft)
    
    // 如果草稿有 animalId,驗證該動物是否仍然存在且屬於當前用戶
    if (draft.animalId) {
      console.log('loadDraft - checking animal permissions for ID:', draft.animalId)
      // 嘗試載入該動物資料來驗證權限
      getAnimal(draft.animalId)
        .then((animal) => {
          console.log('loadDraft - loaded animal:', animal)
          // 檢查權限：個人動物或收容所動物
          const isOwner = animal.owner_id === authStore.user?.user_id
          const isShelterAnimal = animal.shelter_id && 
                                 authStore.user?.role === 'SHELTER_MEMBER' && 
                                 authStore.user?.primary_shelter_id === animal.shelter_id
          
          console.log('loadDraft - permission check:', { isOwner, isShelterAnimal, animalOwnerId: animal.owner_id, animalShelterId: animal.shelter_id, currentUserId: authStore.user?.user_id, userRole: authStore.user?.role, userShelterId: authStore.user?.primary_shelter_id })
          
          if (isOwner || isShelterAnimal) {
            // 有權限，導航到編輯模式
            router.replace({ path: '/rehome-form', query: { id: draft.animalId } })
            console.log('載入已儲存的草稿 ID:', draft.animalId)
          } else {
            // 無權限，清除草稿
            console.warn('無權限編輯草稿中的動物，清除草稿:', draft.animalId)
            localStorage.removeItem('rehome_draft')
            // 但仍然載入表單資料
            Object.assign(formData, draft.formData)
            uploadedPhotos.value = []
            currentStep.value = draft.currentStep || 0
          }
        })
        .catch((error) => {
          console.warn('草稿中的動物不存在,清除草稿:', draft.animalId, error)
          localStorage.removeItem('rehome_draft')
          // 但仍然載入表單資料
          Object.assign(formData, draft.formData)
          uploadedPhotos.value = []
          currentStep.value = draft.currentStep || 0
        })
    }
    
    Object.assign(formData, draft.formData)
    uploadedPhotos.value = draft.uploadedPhotos || []
    currentStep.value = draft.currentStep || 0
  } catch (error) {
    console.error('載入草稿失敗:', error)
    localStorage.removeItem('rehome_draft')
  }
}

async function handleSubmit() {
  // 檢查 FileUploader 中的檔案
  const uploaderFiles = fileUploader.value?.files || []
  
  // 編輯模式可以沒有新照片(使用現有照片)
  if (!isEditMode.value && uploaderFiles.length === 0) {
    errorMessage.value = '請至少選擇一張照片'
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    // 步驟 1: 準備動物資料
    const animalData = {
      name: formData.name,
      species: formData.species as 'CAT' | 'DOG',
      breed: formData.breed || undefined,
      sex: formData.sex as 'MALE' | 'FEMALE',
      dob: formData.dob || undefined,
      color: formData.color || undefined,
      description: formData.description,
      medical_summary: formData.medical_summary || undefined,
      is_neutered: formData.is_neutered,
      source_type: 'PERSONAL' as const,
      status: 'DRAFT' as const,
    }

    let animalId: number

    // 步驟 2: 建立或更新動物記錄
    if (isEditMode.value && editingAnimalId.value) {
      // 更新模式
      const result = await updateAnimal(editingAnimalId.value, animalData)
      animalId = result.animal.animal_id
    } else {
      // 新增模式
      const result = await createAnimal(animalData)
      animalId = result.animal.animal_id
    }

    // 步驟 3: 上傳新照片 (如果有)
    if (uploaderFiles.length > 0) {
      try {
        const { uploadMultiple } = useUpload()
        const files = uploaderFiles.map(item => item.file)
        const uploadResults = await uploadMultiple(files, 'ANIMAL', animalId)
        
        // 將上傳的圖片 URL 添加到 animal_images 表
        for (const result of uploadResults) {
          await addAnimalImage(animalId, { 
            image_url: result.url,
            storage_key: result.storage_key,
            mime_type: result.mime_type
          })
        }
      } catch (uploadError) {
        console.error('Photo upload error:', uploadError)
        alert('動物資訊已儲存,但照片上傳失敗。您可以稍後在編輯頁面重新上傳照片。')
      }
    }
    
    // 步驟 3.5: 處理暫存的醫療記錄 (如果有)
    if (tempMedicalRecords.value.length > 0) {
      try {
        for (const tempRecord of tempMedicalRecords.value) {
          // 先上傳附件
          let uploadedAttachments: any[] = []
          if (tempRecord.files && tempRecord.files.length > 0) {
            const { uploadMultiple } = useUpload()
            const files = tempRecord.files.map((item: any) => item.file)
            const uploadResults = await uploadMultiple(files, 'MEDICAL_RECORD', animalId)
            
            uploadedAttachments = uploadResults.map(result => ({
              url: result.url,
              storage_key: result.storage_key,
              filename: result.filename,
              mime_type: result.mime_type,
              size: result.size
            }))
          }
          
          // 合併附件
          const allAttachments = [
            ...(tempRecord.attachments || []),
            ...uploadedAttachments
          ]
          
          // 創建醫療記錄
          const medicalData = {
            record_type: tempRecord.record_type,
            date: tempRecord.date,
            provider: tempRecord.provider,
            details: tempRecord.details,
            attachments: allAttachments
          }
          
          await createMedicalRecord(animalId, medicalData)
        }
        
        // 清空暫存記錄
        tempMedicalRecords.value = []
        console.log('暫存的醫療記錄已儲存')
      } catch (medicalError) {
        console.error('醫療記錄儲存失敗:', medicalError)
        alert('動物資訊已儲存,但部分醫療記錄儲存失敗。您可以稍後在編輯頁面重新新增。')
      }
    }
    
    // 步驟 4: 提交審核 (將狀態從 DRAFT 改為 SUBMITTED)
    try {
      await submitAnimal(animalId)
      console.log('已提交審核')
    } catch (submitError) {
      console.error('Submit for review error:', submitError)
      alert('動物資訊已儲存,但提交審核失敗。請稍後在「我的送養」頁面手動提交審核。')
    }
    
    // 清除草稿
    localStorage.removeItem('rehome_draft')

    // 導向到合適的頁面：收容所成員在單次送養後應回到「收容所動物管理」，其他使用者回到「我的送養」
    const message = isEditMode.value ? '送養資訊已更新並提交審核成功!' : '送養資訊已建立並提交審核成功!'
    alert(message + '\n審核通過後將會公開顯示。')
    if (authStore.user?.role === 'SHELTER_MEMBER') {
      router.push('/shelter/animals')
    } else {
      router.push('/my-rehomes')
    }
  } catch (error: any) {
    console.error('Submit error:', error)
    
    // 處理動物不存在的情況
    if (error.response?.status === 404 && isEditMode.value) {
      alert('此動物資料不存在或已被刪除,將建立新的送養資訊')
      // 清除草稿並導航到新增模式
      localStorage.removeItem('rehome_draft')
      router.replace('/rehome-form')
      
      // 自動重試提交為新動物
      try {
        const animalData = {
          name: formData.name,
          species: formData.species as 'CAT' | 'DOG',
          breed: formData.breed || undefined,
          sex: formData.sex as 'MALE' | 'FEMALE',
          dob: formData.dob || undefined,
          color: formData.color || undefined,
          description: formData.description,
          medical_summary: formData.medical_summary || undefined,
          is_neutered: formData.is_neutered,
          source_type: 'PERSONAL' as const,
          status: 'DRAFT' as const,
        }
        
        const result = await createAnimal(animalData)
        const newAnimalId = result.animal.animal_id
        
        // 上傳照片
        const uploaderFiles = fileUploader.value?.files || []
        if (uploaderFiles.length > 0) {
          const { uploadMultiple } = useUpload()
          const files = uploaderFiles.map(item => item.file)
          const uploadResults = await uploadMultiple(files, 'ANIMAL', newAnimalId)
          
          for (const uploadResult of uploadResults) {
            await addAnimalImage(newAnimalId, { 
              image_url: uploadResult.url,
              storage_key: uploadResult.storage_key,
              mime_type: uploadResult.mime_type
            })
          }
        }
        
        alert('送養資訊已建立成功!')
        if (authStore.user?.role === 'SHELTER_MEMBER') {
          router.push('/shelter/animals')
        } else {
          router.push('/my-rehomes')
        }
        return
      } catch (retryError) {
        alert('重新建立送養資訊失敗')
      }
    }
    
    errorMessage.value = error.response?.data?.message || '送出失敗,請稍後再試'
    alert(errorMessage.value)
  } finally {
    isSubmitting.value = false
  }
}

// 醫療紀錄管理函數
async function loadMedicalRecords() {
  if (!editingAnimalId.value) return

  loadingRecords.value = true
  try {
    const response = await getMedicalRecords(editingAnimalId.value)
    medicalRecords.value = response.medical_records || []
  } catch (error) {
    console.error('載入醫療記錄失敗:', error)
    medicalRecords.value = []
  } finally {
    loadingRecords.value = false
  }
}

function openMedicalModal() {
  isEditingMedical.value = false
  editingMedicalRecordId.value = null
  medicalFormData.value = {
    record_type: undefined,
    date: todayDate.value,
    provider: '',
    details: '',
    attachments: []
  }
  showMedicalModal.value = true
}

function openEditMedicalModal(record: MedicalRecord) {
  isEditingMedical.value = true
  editingMedicalRecordId.value = record.medical_record_id
  editingTempRecordIndex.value = null
  medicalFormData.value = {
    record_type: record.record_type,
    date: record.date,
    provider: record.provider || '',
    details: record.details || '',
    attachments: record.attachments || []
  }
  showMedicalModal.value = true
}

function openEditTempMedicalModal(index: number) {
  const record = tempMedicalRecords.value[index]
  isEditingMedical.value = false
  editingMedicalRecordId.value = null
  editingTempRecordIndex.value = index
  medicalFormData.value = {
    record_type: record.record_type,
    date: record.date,
    provider: record.provider || '',
    details: record.details || '',
    attachments: record.attachments || []
  }
  // 恢復暫存的文件
  if (medicalFileUploader.value && record.files) {
    medicalFileUploader.value.files = record.files
  }
  showMedicalModal.value = true
}

function removeTempMedicalRecord(index: number) {
  if (confirm('確定要刪除這筆暫存的醫療記錄嗎?')) {
    tempMedicalRecords.value.splice(index, 1)
  }
}

function closeMedicalModal() {
  showMedicalModal.value = false
  isEditingMedical.value = false
  editingMedicalRecordId.value = null
  editingTempRecordIndex.value = null
}

async function handleMedicalSubmit() {
  submittingMedical.value = true
  medicalUploadError.value = ''
  
  try {
    // 如果沒有動物ID,儲存為暫存記錄
    if (!editingAnimalId.value) {
      // 處理暫存記錄
      const tempRecord = {
        record_type: medicalFormData.value.record_type,
        date: medicalFormData.value.date,
        provider: medicalFormData.value.provider,
        details: medicalFormData.value.details,
        attachments: medicalFormData.value.attachments || [],
        files: medicalFileUploader.value?.files || [] // 保存File對象,稍後上傳
      }
      
      if (editingTempRecordIndex.value !== null) {
        // 更新暫存記錄
        tempMedicalRecords.value[editingTempRecordIndex.value] = tempRecord
        alert('暫存醫療記錄已更新')
      } else {
        // 新增暫存記錄
        tempMedicalRecords.value.push(tempRecord)
        alert('醫療記錄已暫存,將在確認送出時一併儲存')
      }
      
      closeMedicalModal()
      submittingMedical.value = false
      return
    }

    // 有動物ID,直接儲存到後端
    // 先上傳附件(如果有新選擇的檔案)
    const uploaderFiles = medicalFileUploader.value?.files || []
    let uploadedAttachments: any[] = []
    
    if (uploaderFiles.length > 0) {
      try {
        const { uploadMultiple } = useUpload()
        const files = uploaderFiles.map(item => item.file)
        const uploadResults = await uploadMultiple(files, 'MEDICAL_RECORD', editingAnimalId.value!)
        
        uploadedAttachments = uploadResults.map(result => ({
          url: result.url,
          storage_key: result.storage_key,
          filename: result.filename,
          mime_type: result.mime_type,
          size: result.size
        }))
      } catch (uploadError) {
        console.error('附件上傳失敗:', uploadError)
        medicalUploadError.value = '附件上傳失敗,請稍後再試'
        submittingMedical.value = false
        return
      }
    }
    
    // 合併現有附件和新上傳的附件
    const allAttachments = [
      ...(medicalFormData.value.attachments || []),
      ...uploadedAttachments
    ]
    
    // 準備提交資料
    const submitData = {
      ...medicalFormData.value,
      attachments: allAttachments
    }
    
    if (isEditingMedical.value && editingMedicalRecordId.value) {
      await updateMedicalRecord(editingMedicalRecordId.value, submitData)
      alert('醫療記錄更新成功')
    } else {
      await createMedicalRecord(editingAnimalId.value, submitData)
      alert('醫療記錄新增成功')
    }
    
    // 清空 FileUploader
    if (medicalFileUploader.value) {
      medicalFileUploader.value.files = []
    }
    
    closeMedicalModal()
    await loadMedicalRecords()
  } catch (error: any) {
    console.error('處理醫療記錄失敗:', error)
    alert(error.response?.data?.message || '處理醫療記錄失敗')
  } finally {
    submittingMedical.value = false
  }
}

// 附件相關函數
function onMedicalFilesUploaded(files: any[]) {
  console.log('Medical files ready:', files)
}

function onMedicalUploadError(error: string) {
  medicalUploadError.value = error
}

function removeMedicalAttachment(index: number) {
  if (medicalFormData.value.attachments) {
    medicalFormData.value.attachments.splice(index, 1)
  }
}

// 醫療紀錄輔助函數
function getMedicalRecordTypeLabel(type: string | undefined): string {
  if (!type) return ''
  const labels: Record<string, string> = {
    TREATMENT: '治療',
    CHECKUP: '健康檢查',
    VACCINE: '疫苗接種',
    SURGERY: '手術',
    OTHER: '其他'
  }
  return labels[type] || type
}

function getMedicalRecordTypeClass(type: string | undefined): string {
  if (!type) return 'type-other'
  const classes: Record<string, string> = {
    TREATMENT: 'type-treatment',
    CHECKUP: 'type-checkup',
    VACCINE: 'type-vaccine',
    SURGERY: 'type-surgery',
    OTHER: 'type-other'
  }
  return classes[type] || 'type-other'
}

function formatMedicalDate(dateString: string | undefined): string {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW', { year: 'numeric', month: 'long', day: 'numeric' })
}

function formatMedicalDateTime(dateString: string | undefined): string {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-TW', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 監聽編輯模式變化,載入醫療紀錄
watch(() => editingAnimalId.value, (newId) => {
  if (newId) {
    loadMedicalRecords()
  } else {
    medicalRecords.value = []
  }
}, { immediate: true })
</script>

<style scoped>
.rehome-form-page {
  min-height: calc(100vh - 4rem);
}

.steps {
  position: relative;
  padding: 2rem 0;
}

.step-item {
  flex: 1;
  display: flex;
  align-items: center;
  position: relative;
}

.step-number {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background-color: #e5e7eb;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  z-index: 1;
}

.step-item.active .step-number {
  background-color: #3b82f6;
  color: white;
}

.step-item.completed .step-number {
  background-color: #10b981;
  color: white;
}

.step-label {
  font-weight: 500;
  color: #6b7280;
}

.step-item.active .step-label {
  color: #3b82f6;
}

.step-item.completed .step-label {
  color: #10b981;
}

.step-line {
  flex: 1;
  height: 2px;
  background-color: #e5e7eb;
  margin: 0 1rem;
}

.step-item.completed .step-line {
  background-color: #10b981;
}

.form-section {
  background-color: white;
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #374151;
}

.form-label.required::after {
  content: ' *';
  color: #ef4444;
}

.form-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.preview-card {
  background-color: #f9fafb;
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.preview-section {
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.preview-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.alert {
  padding: 1rem;
  border-radius: 0.375rem;
  margin-top: 1rem;
}

.alert-error {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.form-actions {
  margin-top: 2rem;
}

.btn-primary {
  padding: 0.625rem 1.5rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-primary:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 0.625rem 1.5rem;
  background-color: white;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #f3f4f6;
}

.btn-secondary:disabled {
  color: #9ca3af;
  cursor: not-allowed;
}

/* 醫療紀錄管理樣式 */
.medical-records-manager {
  background-color: #f9fafb;
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.info-box {
  background-color: #dbeafe;
  border: 1px solid #93c5fd;
  border-radius: 0.375rem;
  padding: 1rem;
}

.medical-link-box {
  background-color: #f3e8ff;
  border: 1px solid #c084fc;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.btn-medical-link {
  display: inline-flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(139, 92, 246, 0.2);
}

.btn-medical-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(139, 92, 246, 0.3);
  background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%);
}

.btn-medical-link:active {
  transform: translateY(0);
}

.medical-summary-section {
  border-top: 1px solid #e5e7eb;
  padding-top: 1.5rem;
}

/* 醫療紀錄容器 */
.medical-records-container {
  background-color: white;
  border-radius: 0.5rem;
  padding: 1rem;
}

.action-bar {
  display: flex;
  justify-content: flex-end;
}

.btn-add-record {
  display: inline-flex;
  align-items: center;
  padding: 0.625rem 1.25rem;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(139, 92, 246, 0.2);
}

.btn-add-record:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(139, 92, 246, 0.3);
}

.loading-container {
  text-align: center;
  padding: 3rem 0;
}

.spinner {
  border: 3px solid #f3f4f6;
  border-top: 3px solid #8b5cf6;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #6b7280;
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  margin: 0 auto 1rem;
  color: #d1d5db;
}

.empty-text {
  font-size: 1.125rem;
  margin-bottom: 0.5rem;
}

.medical-records-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.medical-record-card {
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  transition: box-shadow 0.2s;
}

.medical-record-card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.record-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}

.record-type-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
}

.type-treatment {
  background-color: #fef3c7;
  color: #92400e;
}

.type-checkup {
  background-color: #dbeafe;
  color: #1e40af;
}

.type-vaccine {
  background-color: #d1fae5;
  color: #065f46;
}

.type-surgery {
  background-color: #fee2e2;
  color: #991b1b;
}

.type-other {
  background-color: #f3f4f6;
  color: #374151;
}

.record-date {
  font-size: 0.875rem;
  color: #6b7280;
}

.temp-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background-color: #fef3c7;
  color: #92400e;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.verified-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background-color: #d1fae5;
  color: #065f46;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.record-body {
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
}

.record-provider,
.record-details {
  margin-bottom: 0.5rem;
}

.record-details p {
  margin-top: 0.25rem;
  color: #4b5563;
  line-height: 1.5;
}

.record-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.75rem;
  border-top: 1px solid #f3f4f6;
}

.record-meta {
  font-size: 0.75rem;
  color: #9ca3af;
}

.record-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon-small {
  padding: 0.375rem;
  background-color: #f3f4f6;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #6b7280;
}

.btn-icon-small:hover {
  background-color: #e5e7eb;
  color: #374151;
}

/* Modal 樣式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background-color: white;
  border-radius: 0.5rem;
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
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

.modal-close {
  padding: 0.5rem;
  background-color: transparent;
  border: none;
  cursor: pointer;
  color: #6b7280;
  transition: color 0.2s;
}

.modal-close:hover {
  color: #111827;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-select,
.form-textarea {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #8b5cf6;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

/* 隱藏 FileUploader 中的"開始上傳"按鈕 */
.form-section :deep(.file-uploader .actions) {
  display: none;
}

/* 醫療附件樣式 */
.record-attachments {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f3f4f6;
}

.attachments-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.attachment-link {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  background-color: #f3f4f6;
  border-radius: 0.375rem;
  color: #3b82f6;
  text-decoration: none;
  transition: all 0.2s;
}

.attachment-link:hover {
  background-color: #e5e7eb;
  color: #2563eb;
}

.existing-attachments {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.attachment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
}

.btn-remove-attachment {
  padding: 0.25rem 0.5rem;
  background-color: #fee2e2;
  color: #991b1b;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.btn-remove-attachment:hover {
  background-color: #fecaca;
}
</style>

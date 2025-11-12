<template>
  <div class="my-rehomes-page max-w-6xl mx-auto px-4 py-8">
    <div class="header flex justify-between items-center mb-8">
      <h1 class="text-3xl font-bold text-gray-900">我的送養</h1>
      <router-link to="/rehome-form" class="btn-primary">
        <svg class="inline-block w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        新增送養
      </router-link>
    </div>

    <!-- 收容所會員提示 -->
    <div v-if="authStore.user?.role === 'SHELTER_MEMBER'" class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
      <div class="flex items-start gap-3">
        <div class="text-2xl">💡</div>
        <div>
          <h2 class="text-lg font-semibold text-blue-900 mb-2">收容所會員提醒</h2>
          <p class="text-blue-800 mb-3">您正在查看<strong>單次送養</strong>的動物。如需管理<strong>收容所批次</strong>的動物，請使用：</p>
          <button
            @click="router.push('/shelter/animals')"
            class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
          >
            🐾 前往收容所動物管理
          </button>
        </div>
      </div>
    </div>

    <!-- 狀態篩選 -->
    <div class="filters mb-6 flex gap-2">
      <button
        v-for="status in statusFilters"
        :key="status.value"
        class="filter-btn"
        :class="{ active: currentStatus === status.value }"
        @click="currentStatus = status.value"
      >
        {{ status.label }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="spinner"></div>
      <p class="text-gray-500 mt-4">載入中...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="alert alert-error">
      {{ error }}
    </div>

    <!-- 動物列表 -->
    <div v-else-if="filteredAnimals.length > 0" class="animals-grid">
      <div v-for="animal in filteredAnimals" :key="animal.animal_id" class="animal-card">
        <!-- 圖片 -->
        <div class="card-image">
          <img
            v-if="animal.images && animal.images.length > 0"
            :src="animal.images[0].url"
            :alt="animal.name"
            class="w-full h-48 object-cover"
          />
          <div v-else class="w-full h-48 bg-gray-200 flex items-center justify-center">
            <span class="text-4xl">🐾</span>
          </div>
          
          <!-- 狀態標籤 -->
          <div class="status-badge" :class="getStatusClass(animal.status)">
            {{ getStatusText(animal.status) }}
          </div>
        </div>

        <!-- 內容 -->
        <div class="card-content">
          <h3 class="card-title">{{ animal.name || '未命名' }}</h3>
          
          <!-- 基本資訊標籤 -->
          <div class="info-badges">
            <span class="badge badge-species">
              {{ getSpeciesText(animal.species || 'UNKNOWN') }}
            </span>
            <span v-if="animal.breed" class="badge badge-breed">
              {{ animal.breed }}
            </span>
            <span class="badge badge-sex">
              {{ getSexText(animal.sex || 'UNKNOWN') }}
            </span>
            <span v-if="animal.color" class="badge badge-color">
              {{ animal.color }}
            </span>
            <span v-if="animal.age !== null && animal.age !== undefined" class="badge badge-age">
              {{ animal.age }} 歲
            </span>
          </div>

          <p v-if="animal.description" class="card-description">{{ animal.description }}</p>
          
          <!-- 詳細資訊 -->
          <div class="detail-info">
            <div class="detail-row">
              <span class="detail-label">動物 ID:</span>
              <span class="detail-value">{{ animal.animal_id }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">出生日期:</span>
              <span class="detail-value">{{ animal.dob ? formatDateOnly(animal.dob) : '未提供' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">建立時間:</span>
              <span class="detail-value">{{ formatDate(animal.created_at) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">更新時間:</span>
              <span class="detail-value">{{ formatDate(animal.updated_at) }}</span>
            </div>
            <div v-if="animal.rejection_reason" class="detail-row rejection-row">
              <span class="detail-label">拒絕原因:</span>
              <span class="detail-value rejection-reason">{{ animal.rejection_reason }}</span>
            </div>
          </div>
          
          <!-- 統計資訊 -->
          <div class="card-stats">
            <div class="stat-item">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <span>{{ (animal as any).view_count || 0 }} 次瀏覽</span>
            </div>
            <div v-if="animal.images && animal.images.length > 0" class="stat-item">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>{{ animal.images.length }} 張照片</span>
            </div>
            <div v-if="animal.has_pending_application" class="stat-item stat-warning">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span>有待審核申請</span>
            </div>
          </div>

          <!-- 操作按鈕 -->
          <div class="card-actions">
            <router-link :to="`/animals/${animal.animal_id}`" class="btn-view">查看</router-link>
            <button
              v-if="animal.status === 'DRAFT' || animal.status === 'SUBMITTED'"
              class="btn-edit"
              @click="editAnimal(animal.animal_id)"
            >
              編輯
            </button>
            <button
              v-if="animal.status === 'DRAFT'"
              class="btn-submit"
              @click="confirmSubmit(animal.animal_id)"
            >
              提交審核
            </button>
            <button
              v-if="animal.images && animal.images.length > 0"
              class="btn-secondary"
              @click="manageImages(animal)"
            >
              管理圖片 ({{ animal.images.length }})
            </button>
            <button
              v-if="animal.status === 'PUBLISHED'"
              class="btn-secondary"
              @click="viewApplications(animal.animal_id)"
            >
              申請列表
            </button>
            <button
              v-if="animal.status !== 'RETIRED'"
              class="btn-danger"
              @click="confirmDelete(animal.animal_id)"
            >
              刪除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空狀態 -->
    <div v-else class="empty-state">
      <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="empty-text">目前沒有{{ getStatusText(currentStatus) }}的送養資訊</p>
      <router-link to="/rehome-form" class="btn-primary mt-4">新增送養</router-link>
    </div>

    <!-- 圖片管理對話框 -->
    <div v-if="showImageModal" class="modal-overlay" @click.self="closeImageModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">管理圖片 - {{ currentAnimal?.name }}</h2>
          <button class="modal-close" @click="closeImageModal">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="modal-body">
          <div v-if="currentAnimal?.images && currentAnimal.images.length > 0" class="images-grid">
            <div v-for="(image, index) in currentAnimal.images" :key="image.animal_image_id" class="image-item">
              <div class="image-wrapper">
                <img :src="image.url" :alt="`圖片 ${index + 1}`" />
                <div class="image-overlay">
                  <button
                    class="delete-image-btn"
                    @click="confirmDeleteImage(image.animal_image_id)"
                    title="刪除圖片"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
              <div class="image-info">
                <span class="image-number">圖片 {{ index + 1 }}</span>
                <span class="image-order">順序: {{ image.order }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-images">
            <p>目前沒有圖片</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAnimals, deleteAnimal, deleteAnimalImage, submitAnimal, type Animal } from '@/api/animals'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isLoading = ref(false)
const error = ref('')
const animals = ref<Animal[]>([])
const currentStatus = ref<string>('')
const showImageModal = ref(false)
const currentAnimal = ref<Animal | null>(null)

const statusFilters = [
  { value: '', label: '全部' },
  { value: 'DRAFT', label: '草稿' },
  { value: 'SUBMITTED', label: '審核中' },
  { value: 'PUBLISHED', label: '已發布' },
  { value: 'RETIRED', label: '已下架' },
]

const filteredAnimals = computed(() => {
  if (!currentStatus.value) return animals.value
  return animals.value.filter(a => a.status === currentStatus.value)
})

onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  fetchAnimals()
})

async function fetchAnimals() {
  isLoading.value = true
  error.value = ''

  try {
    const response = await getAnimals({
      owner_id: authStore.user?.user_id,
    })
    animals.value = response.animals
  } catch (err: any) {
    console.error('Fetch error:', err)
    error.value = err.response?.data?.message || '載入失敗'
  } finally {
    isLoading.value = false
  }
}

function getStatusText(status: string): string {
  const map: Record<string, string> = {
    DRAFT: '草稿',
    SUBMITTED: '審核中',
    PUBLISHED: '已發布',
    RETIRED: '已下架',
  }
  return map[status] || status
}

function getStatusClass(status: string): string {
  const map: Record<string, string> = {
    DRAFT: 'status-draft',
    SUBMITTED: 'status-submitted',
    PUBLISHED: 'status-published',
    RETIRED: 'status-retired',
  }
  return map[status] || ''
}

function getSpeciesText(species: string): string {
  return species === 'CAT' ? '貓' : species === 'DOG' ? '狗' : species
}

function getSexText(sex: string): string {
  return sex === 'MALE' ? '公' : sex === 'FEMALE' ? '母' : sex
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatDateOnly(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit'
  })
}

function editAnimal(id: number) {
  router.push(`/rehome-form?id=${id}`)
}

async function confirmSubmit(id: number) {
  if (!confirm('確定要提交審核嗎?提交後將由管理員審核是否發布。')) return

  try {
    const response = await submitAnimal(id)
    
    // 更新本地列表中的動物狀態
    const index = animals.value.findIndex(a => a.animal_id === id)
    if (index !== -1) {
      animals.value[index] = response.animal
    }
    
    alert('已提交審核,等待管理員審核')
  } catch (err: any) {
    alert(err.response?.data?.message || '提交失敗')
  }
}

function viewApplications(id: number) {
  // 收容所成員和管理員可以查看申請審核頁面
  if (authStore.isShelterMember || authStore.isAdmin) {
    router.push(`/admin/applications?animal_id=${id}`)
  } else {
    // 一般會員跳轉到我的申請頁面
    router.push(`/my/applications`)
  }
}

async function confirmDelete(id: number) {
  if (!confirm('確定要刪除此送養資訊嗎?')) return

  try {
    await deleteAnimal(id)
    animals.value = animals.value.filter(a => a.animal_id !== id)
    alert('刪除成功')
  } catch (err: any) {
    alert(err.response?.data?.message || '刪除失敗')
  }
}

function manageImages(animal: Animal) {
  currentAnimal.value = animal
  showImageModal.value = true
}

function closeImageModal() {
  showImageModal.value = false
  currentAnimal.value = null
}

async function confirmDeleteImage(imageId: number) {
  if (!confirm('確定要刪除此圖片嗎?')) return
  if (!currentAnimal.value) return

  try {
    await deleteAnimalImage(currentAnimal.value.animal_id, imageId)
    
    // 更新當前動物的圖片列表
    if (currentAnimal.value.images) {
      currentAnimal.value.images = currentAnimal.value.images.filter(
        img => img.animal_image_id !== imageId
      )
    }
    
    // 更新主列表中的動物
    const animalInList = animals.value.find(a => a.animal_id === currentAnimal.value?.animal_id)
    if (animalInList && animalInList.images) {
      animalInList.images = animalInList.images.filter(
        img => img.animal_image_id !== imageId
      )
    }
    
    alert('圖片已刪除')
  } catch (err: any) {
    alert(err.response?.data?.message || '刪除圖片失敗')
  }
}
</script>

<style scoped>
.my-rehomes-page {
  min-height: calc(100vh - 4rem);
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  padding: 0.625rem 1.25rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #2563eb;
}

.filters {
  display: flex;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 0.5rem 1rem;
  background-color: white;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  background-color: #f3f4f6;
}

.filter-btn.active {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.spinner {
  width: 3rem;
  height: 3rem;
  border: 4px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.alert {
  padding: 1rem;
  border-radius: 0.375rem;
}

.alert-error {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.animals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.animal-card {
  background-color: white;
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s;
}

.animal-card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card-image {
  position: relative;
}

.status-badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-draft {
  background-color: #e5e7eb;
  color: #374151;
}

.status-submitted {
  background-color: #fef3c7;
  color: #92400e;
}

.status-published {
  background-color: #d1fae5;
  color: #065f46;
}

.status-retired {
  background-color: #fee2e2;
  color: #991b1b;
}

.card-content {
  padding: 1rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.75rem;
}

.info-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge-species {
  background-color: #dbeafe;
  color: #1e40af;
}

.badge-breed {
  background-color: #e9d5ff;
  color: #6b21a8;
}

.badge-sex {
  background-color: #fce7f3;
  color: #9f1239;
}

.badge-color {
  background-color: #f3f4f6;
  color: #374151;
}

.badge-age {
  background-color: #d1fae5;
  color: #065f46;
}

.detail-info {
  background-color: #f9fafb;
  border-radius: 0.375rem;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  font-size: 0.813rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 0.25rem 0;
}

.detail-row:not(:last-child) {
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.5rem;
  margin-bottom: 0.5rem;
}

.detail-label {
  font-weight: 500;
  color: #6b7280;
  min-width: 5rem;
}

.detail-value {
  color: #111827;
  text-align: right;
  flex: 1;
}

.rejection-row {
  background-color: #fef2f2;
  border-radius: 0.25rem;
  padding: 0.5rem;
  margin: 0.5rem -0.75rem -0.75rem -0.75rem;
  border-top: 1px solid #fecaca;
}

.rejection-row .detail-label {
  color: #991b1b;
}

.rejection-reason {
  color: #dc2626;
  font-weight: 500;
}

.card-info {
  display: flex;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.card-info span:not(:last-child)::after {
  content: '•';
  margin-left: 0.5rem;
}

.card-description {
  color: #4b5563;
  font-size: 0.875rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 1rem;
}

.card-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 0.75rem 0;
  border-top: 1px solid #e5e7eb;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.813rem;
  color: #6b7280;
}

.stat-warning {
  color: #d97706;
  font-weight: 500;
}

.stat-warning svg {
  color: #f59e0b;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-view,
.btn-edit,
.btn-submit,
.btn-secondary,
.btn-danger {
  padding: 0.375rem 0.75rem;
  border: 1px solid;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
}

.btn-view {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.btn-view:hover {
  background-color: #2563eb;
}

.btn-edit {
  background-color: white;
  color: #374151;
  border-color: #d1d5db;
}

.btn-edit:hover {
  background-color: #f3f4f6;
}

.btn-submit {
  background-color: #8b5cf6;
  color: white;
  border-color: #8b5cf6;
}

.btn-submit:hover {
  background-color: #7c3aed;
}

.btn-secondary {
  background-color: #10b981;
  color: white;
  border-color: #10b981;
}

.btn-secondary:hover {
  background-color: #059669;
}

.btn-medical {
  background-color: #8b5cf6 !important;
  border-color: #8b5cf6 !important;
}

.btn-medical:hover {
  background-color: #7c3aed !important;
}

.btn-danger {
  background-color: white;
  color: #ef4444;
  border-color: #fecaca;
}

.btn-danger:hover {
  background-color: #fee2e2;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  margin: 0 auto 1rem;
  color: #9ca3af;
}

.empty-text {
  font-size: 1.125rem;
  color: #6b7280;
}

/* 圖片管理對話框 */
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
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
}

.modal-close {
  padding: 0.5rem;
  background-color: transparent;
  border: none;
  color: #6b7280;
  cursor: pointer;
  border-radius: 0.375rem;
  transition: all 0.2s;
}

.modal-close:hover {
  background-color: #f3f4f6;
  color: #111827;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.image-item {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
  background-color: white;
}

.image-wrapper {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
}

.image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.image-wrapper:hover .image-overlay {
  opacity: 1;
}

.delete-image-btn {
  padding: 0.75rem;
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-image-btn:hover {
  background-color: #dc2626;
  transform: scale(1.1);
}

.image-info {
  padding: 0.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f9fafb;
  font-size: 0.875rem;
  color: #6b7280;
}

.image-number {
  font-weight: 500;
  color: #374151;
}

.empty-images {
  text-align: center;
  padding: 3rem;
  color: #9ca3af;
}
</style>

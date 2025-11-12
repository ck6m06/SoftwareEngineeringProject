<template>
  <div class="my-applications-page max-w-6xl mx-auto px-4 py-8">
    <div class="header mb-8">
      <h1 class="text-3xl font-bold text-gray-900">我的申請</h1>
      <p class="text-gray-600 mt-2">查看您提交的所有領養申請及其狀態</p>
    </div>

    <!-- 狀態篩選 -->
    <div class="filters mb-6 flex gap-2">
      <button
        v-for="status in statusFilters"
        :key="status.value"
        class="filter-btn"
        :class="{ active: currentStatus === status.value }"
        @click="changeStatus(status.value)"
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

    <!-- 申請列表 -->
    <div v-else-if="applications.length > 0" class="applications-list">
      <div v-for="application in applications" :key="application.application_id" class="application-card">
        <!-- 狀態標籤 -->
        <div class="status-badge" :class="getStatusClass(application.status)">
          {{ getStatusText(application.status) }}
        </div>

        <div class="card-content">
          <!-- 動物資訊 -->
          <div class="animal-section">
            <div v-if="application.animal?.images?.[0]" class="animal-image">
              <img :src="application.animal.images[0].url" :alt="application.animal.name" />
            </div>
            <div v-else class="animal-image-placeholder">
              <span class="text-4xl">🐾</span>
            </div>
            <div class="animal-info">
              <h3 class="animal-name">{{ application.animal?.name || '未命名' }}</h3>
              <div class="animal-meta">
                <span>{{ getSpeciesText(application.animal?.species) }}</span>
                <span v-if="application.animal?.breed">{{ application.animal.breed }}</span>
                <span>{{ getSexText(application.animal?.sex) }}</span>
              </div>
            </div>
          </div>

          <!-- 申請資訊 -->
          <div class="application-info">
            <div class="info-row">
              <span class="label">申請編號:</span>
              <span class="value">#{{ application.application_id }}</span>
            </div>
            <div class="info-row">
              <span class="label">申請類型:</span>
              <span class="value">{{ getTypeText(application.type) }}</span>
            </div>
            <div class="info-row">
              <span class="label">提交時間:</span>
              <span class="value">{{ formatDate(application.submitted_at) }}</span>
            </div>
            <div v-if="application.reviewed_at" class="info-row">
              <span class="label">審核時間:</span>
              <span class="value">{{ formatDate(application.reviewed_at) }}</span>
            </div>
            <div v-if="application.review_notes" class="info-row">
              <span class="label">審核備註:</span>
              <span class="value">{{ application.review_notes }}</span>
            </div>
          </div>

          <!-- 操作按鈕 -->
          <div class="card-actions">
            <router-link :to="`/animals/${application.animal_id}`" class="btn-view">
              查看動物
            </router-link>
            <button
              v-if="canWithdraw(application)"
              class="btn-danger"
              @click="confirmWithdraw(application.application_id)"
            >
              撤回申請
            </button>
          </div>
        </div>
      </div>

      <!-- 分頁 -->
      <div v-if="totalPages > 1" class="pagination">
        <button
          class="pagination-btn"
          :disabled="currentPage === 1"
          @click="changePage(currentPage - 1)"
        >
          上一頁
        </button>
        <span class="pagination-info">第 {{ currentPage }} / {{ totalPages }} 頁</span>
        <button
          class="pagination-btn"
          :disabled="currentPage === totalPages"
          @click="changePage(currentPage + 1)"
        >
          下一頁
        </button>
      </div>
    </div>

    <!-- 空狀態 -->
    <div v-else class="empty-state">
      <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="empty-text">
        {{ currentStatus ? `目前沒有${getStatusText(currentStatus)}的申請` : '目前沒有任何申請' }}
      </p>
      <router-link to="/animals" class="btn-primary mt-4">瀏覽動物</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getApplications, withdrawApplication, type Application } from '@/api/applications'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isLoading = ref(false)
const error = ref('')
const applications = ref<Application[]>([])
const currentStatus = ref<string>('')
const currentPage = ref(1)
const totalPages = ref(1)
const perPage = 20

const statusFilters = [
  { value: '', label: '全部' },
  { value: 'PENDING', label: '待審核' },
  { value: 'UNDER_REVIEW', label: '審核中' },
  { value: 'APPROVED', label: '已核准' },
  { value: 'REJECTED', label: '已拒絕' },
  { value: 'WITHDRAWN', label: '已撤回' },
]

onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  fetchApplications()
})

async function fetchApplications() {
  isLoading.value = true
  error.value = ''

  try {
    const filters: any = {
      mode: 'my',  // 使用我的申請模式
      page: currentPage.value,
      per_page: perPage
    }
    
    if (currentStatus.value) {
      filters.status = currentStatus.value
    }

    console.log('Fetching applications with filters:', filters)
    const response = await getApplications(filters)
    console.log('Applications response:', response)
    
    applications.value = response.items
    totalPages.value = response.pages
    currentPage.value = response.page
  } catch (err: any) {
    console.error('Fetch error:', err)
    error.value = err.response?.data?.message || '載入失敗'
  } finally {
    isLoading.value = false
  }
}

function changeStatus(status: string) {
  currentStatus.value = status
  currentPage.value = 1  // 重置頁碼
  fetchApplications()
}

function changePage(page: number) {
  currentPage.value = page
  fetchApplications()
}

function getStatusText(status: string): string {
  const map: Record<string, string> = {
    '': '全部',
    PENDING: '待審核',
    UNDER_REVIEW: '審核中',
    APPROVED: '已核准',
    REJECTED: '已拒絕',
    WITHDRAWN: '已撤回',
  }
  return map[status] || status
}

function getStatusClass(status: string): string {
  const map: Record<string, string> = {
    PENDING: 'status-pending',
    UNDER_REVIEW: 'status-review',
    APPROVED: 'status-approved',
    REJECTED: 'status-rejected',
    WITHDRAWN: 'status-withdrawn',
  }
  return map[status] || ''
}

function getTypeText(type: string): string {
  return type === 'ADOPTION' ? '領養' : type === 'REHOME' ? '送養' : type
}

function getSpeciesText(species: string): string {
  return species === 'CAT' ? '貓' : species === 'DOG' ? '狗' : species
}

function getSexText(sex: string): string {
  return sex === 'MALE' ? '公' : sex === 'FEMALE' ? '母' : sex
}

function formatDate(dateString?: string): string {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function canWithdraw(application: Application): boolean {
  return ['PENDING', 'UNDER_REVIEW'].includes(application.status)
}

async function confirmWithdraw(id: number) {
  if (!confirm('確定要撤回此申請嗎?')) return

  try {
    await withdrawApplication(id)
    alert('申請已撤回')
    fetchApplications()
  } catch (err: any) {
    alert(err.response?.data?.message || '撤回失敗')
  }
}
</script>

<style scoped>
.my-applications-page {
  min-height: calc(100vh - 4rem);
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

.applications-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.application-card {
  position: relative;
  background-color: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s;
}

.application-card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.status-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-pending {
  background-color: #fef3c7;
  color: #92400e;
}

.status-review {
  background-color: #dbeafe;
  color: #1e40af;
}

.status-approved {
  background-color: #d1fae5;
  color: #065f46;
}

.status-rejected {
  background-color: #fee2e2;
  color: #991b1b;
}

.status-withdrawn {
  background-color: #e5e7eb;
  color: #374151;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.animal-section {
  display: flex;
  gap: 1rem;
  align-items: start;
  padding-right: 6rem;
}

.animal-image {
  width: 120px;
  height: 120px;
  flex-shrink: 0;
  border-radius: 0.5rem;
  overflow: hidden;
}

.animal-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.animal-image-placeholder {
  width: 120px;
  height: 120px;
  flex-shrink: 0;
  border-radius: 0.5rem;
  background-color: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.animal-info {
  flex: 1;
}

.animal-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.5rem;
}

.animal-meta {
  display: flex;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.animal-meta span:not(:last-child)::after {
  content: '•';
  margin-left: 0.5rem;
}

.application-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
  padding: 1rem;
  background-color: #f9fafb;
  border-radius: 0.375rem;
}

.info-row {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.label {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 500;
}

.value {
  font-size: 0.875rem;
  color: #111827;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-view,
.btn-danger,
.btn-primary {
  padding: 0.5rem 1rem;
  border: 1px solid;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
}

.btn-view {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.btn-view:hover {
  background-color: #2563eb;
}

.btn-danger {
  background-color: white;
  color: #ef4444;
  border-color: #fecaca;
}

.btn-danger:hover {
  background-color: #fee2e2;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.btn-primary:hover {
  background-color: #2563eb;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  background-color: white;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #f3f4f6;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 0.875rem;
  color: #6b7280;
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
</style>

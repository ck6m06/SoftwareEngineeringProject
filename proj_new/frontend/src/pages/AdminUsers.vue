<template>
  <div class="admin-users-page">
    <div class="container">
      <!-- 頁面標題 -->
      <div class="page-header">
        <h1 class="page-title">用戶管理</h1>
        <p class="page-description">管理系統用戶、角色與權限</p>
      </div>

      <!-- 搜尋與篩選 -->
      <div class="filters-bar">
        <div class="search-box">
          <input
            v-model="searchQuery"
            @input="debouncedSearch"
            type="text"
            placeholder="搜尋用戶名稱或 Email..."
            class="search-input"
          />
          <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        <select v-model="filterRole" @change="fetchUsers" class="role-filter">
          <option value="">所有角色</option>
          <option value="ADMIN">管理員</option>
          <option value="SHELTER_MEMBER">收容所成員</option>
          <option value="GENERAL_MEMBER">一般會員</option>
        </select>

        <button @click="fetchUsers" class="btn-refresh">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 0 0 4.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 0 1-15.357-2m15.357 2H15" />
          </svg>
          刷新
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>載入中...</p>
      </div>

      <!-- 用戶列表 -->
      <div v-else-if="users.length > 0" class="users-table-wrapper">
        <table class="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>用戶名稱</th>
              <th>Email</th>
              <th>角色</th>
              <th>驗證狀態</th>
              <th>註冊時間</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.user_id">
              <td>{{ user.user_id }}</td>
              <td>
                <div class="user-info">
                  <span class="user-avatar">{{ getInitials(user.username || user.email) }}</span>
                  <span>{{ user.username || '-' }}</span>
                </div>
              </td>
              <td>{{ user.email }}</td>
              <td>
                <span :class="['role-badge', getRoleClass(user.role)]">
                  {{ getRoleText(user.role) }}
                </span>
              </td>
              <td>
                <span :class="['status-badge', user.verified ? 'verified' : 'unverified']">
                  {{ user.verified ? '✓ 已驗證' : '✗ 未驗證' }}
                </span>
              </td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td>
                <div class="action-buttons">
                  <button @click="viewUser(user)" class="btn-action btn-view" title="查看">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                  <button 
                    v-if="user.role !== 'ADMIN'"
                    @click="openBanModal(user)" 
                    class="btn-action btn-ban" 
                    title="封禁"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 空狀態 -->
      <div v-else class="empty-state">
        <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
        <p>沒有找到用戶</p>
      </div>

      <!-- 分頁 -->
      <div v-if="pagination.pages > 1" class="pagination">
        <button 
          @click="goToPage(pagination.page - 1)" 
          :disabled="pagination.page <= 1"
          class="btn-page"
        >
          上一頁
        </button>
        <span class="page-info">
          第 {{ pagination.page }} / {{ pagination.pages }} 頁 (共 {{ pagination.total }} 筆)
        </span>
        <button 
          @click="goToPage(pagination.page + 1)" 
          :disabled="pagination.page >= pagination.pages"
          class="btn-page"
        >
          下一頁
        </button>
      </div>
    </div>

    <!-- 用戶詳情 Modal -->
    <Transition name="modal">
      <div v-if="showUserModal" class="modal-overlay" @click="closeUserModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h2>用戶詳情</h2>
            <button @click="closeUserModal" class="btn-close">✕</button>
          </div>
          <div v-if="selectedUser" class="modal-body">
            <div class="detail-row">
              <span class="label">用戶 ID:</span>
              <span class="value">{{ selectedUser.user_id }}</span>
            </div>
            <div class="detail-row">
              <span class="label">用戶名稱:</span>
              <span class="value">{{ selectedUser.username || '-' }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Email:</span>
              <span class="value">{{ selectedUser.email }}</span>
            </div>
            <div class="detail-row">
              <span class="label">角色:</span>
              <span class="value">
                <span :class="['role-badge', getRoleClass(selectedUser.role)]">
                  {{ getRoleText(selectedUser.role) }}
                </span>
              </span>
            </div>
            <div class="detail-row">
              <span class="label">手機:</span>
              <span class="value">{{ selectedUser.phone_number || '-' }}</span>
            </div>
            <div class="detail-row">
              <span class="label">姓名:</span>
              <span class="value">{{ [selectedUser.first_name, selectedUser.last_name].filter(Boolean).join(' ') || '-' }}</span>
            </div>
            <div class="detail-row">
              <span class="label">驗證狀態:</span>
              <span class="value">
                <span :class="['status-badge', selectedUser.verified ? 'verified' : 'unverified']">
                  {{ selectedUser.verified ? '✓ 已驗證' : '✗ 未驗證' }}
                </span>
              </span>
            </div>
            <div class="detail-row">
              <span class="label">註冊時間:</span>
              <span class="value">{{ formatDate(selectedUser.created_at) }}</span>
            </div>
            <div class="detail-row">
              <span class="label">最後更新:</span>
              <span class="value">{{ formatDate(selectedUser.updated_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 封禁 Modal -->
    <Transition name="modal">
      <div v-if="showBanModal" class="modal-overlay" @click="closeBanModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h2>封禁用戶</h2>
            <button @click="closeBanModal" class="btn-close">✕</button>
          </div>
          <div class="modal-body">
            <p class="warning-text">確定要封禁用戶 <strong>{{ banTarget?.email }}</strong> 嗎?</p>
            <div class="form-group">
              <label>封禁天數:</label>
              <input v-model.number="banDays" type="number" min="1" max="365" class="input-field" />
            </div>
            <div class="form-group">
              <label>封禁原因:</label>
              <textarea v-model="banReason" rows="3" class="input-field" placeholder="請輸入封禁原因..."></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="closeBanModal" class="btn-cancel">取消</button>
            <button @click="confirmBan" :disabled="banning" class="btn-danger">
              {{ banning ? '處理中...' : '確認封禁' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { formatDistanceToNow } from 'date-fns'
import { zhTW } from 'date-fns/locale'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

interface User {
  user_id: number
  email: string
  username?: string
  phone_number?: string
  first_name?: string
  last_name?: string
  role: 'ADMIN' | 'SHELTER_MEMBER' | 'GENERAL_MEMBER'
  verified: boolean
  created_at: string
  updated_at: string
}

const users = ref<User[]>([])
const loading = ref(false)
const searchQuery = ref('')
const filterRole = ref('')
const pagination = ref({
  page: 1,
  per_page: 20,
  pages: 1,
  total: 0
})

// Modals
const showUserModal = ref(false)
const selectedUser = ref<User | null>(null)
const showBanModal = ref(false)
const banTarget = ref<User | null>(null)
const banDays = ref(30)
const banReason = ref('')
const banning = ref(false)

// Debounce timer
let searchTimeout: number | null = null

onMounted(() => {
  fetchUsers()
})

async function fetchUsers() {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: pagination.value.page.toString(),
      per_page: pagination.value.per_page.toString(),
    })
    
    if (filterRole.value) {
      params.append('role', filterRole.value)
    }
    
    if (searchQuery.value.trim()) {
      params.append('search', searchQuery.value.trim())
    }

    const response = await fetch(`http://localhost:5000/api/admin/users?${params}`, {
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`
      }
    })

    if (!response.ok) throw new Error('獲取用戶列表失敗')

    const data = await response.json()
    users.value = data.users
    pagination.value = {
      page: data.page,
      per_page: data.per_page,
      pages: data.pages || Math.ceil(data.total / data.per_page),
      total: data.total
    }
  } catch (error: any) {
    console.error('Fetch error:', error)
    alert(error.message || '獲取用戶列表失敗')
  } finally {
    loading.value = false
  }
}

function debouncedSearch() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = window.setTimeout(() => {
    pagination.value.page = 1
    fetchUsers()
  }, 500)
}

function goToPage(page: number) {
  if (page < 1 || page > pagination.value.pages) return
  pagination.value.page = page
  fetchUsers()
}

function viewUser(user: User) {
  selectedUser.value = user
  showUserModal.value = true
}

function closeUserModal() {
  showUserModal.value = false
  selectedUser.value = null
}

function openBanModal(user: User) {
  banTarget.value = user
  banDays.value = 30
  banReason.value = ''
  showBanModal.value = true
}

function closeBanModal() {
  showBanModal.value = false
  banTarget.value = null
}

async function confirmBan() {
  if (!banTarget.value) return
  
  banning.value = true
  try {
    const response = await fetch(`http://localhost:5000/api/admin/users/${banTarget.value.user_id}/ban`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.accessToken}`
      },
      body: JSON.stringify({
        days: banDays.value,
        reason: banReason.value
      })
    })

    if (!response.ok) throw new Error('封禁失敗')

    alert(`已成功封禁用戶 ${banTarget.value.username}`)
    closeBanModal()
    fetchUsers()
  } catch (error: any) {
    console.error('Ban error:', error)
    alert(error.message || '封禁失敗')
  } finally {
    banning.value = false
  }
}

function getRoleText(role: string): string {
  const map: Record<string, string> = {
    ADMIN: '管理員',
    SHELTER_MEMBER: '收容所成員',
    GENERAL_MEMBER: '一般會員'
  }
  return map[role] || role
}

function getRoleClass(role: string): string {
  const map: Record<string, string> = {
    ADMIN: 'role-admin',
    SHELTER_MEMBER: 'role-shelter',
    GENERAL_MEMBER: 'role-general'
  }
  return map[role] || ''
}

function getInitials(name: string): string {
  return name.slice(0, 2).toUpperCase()
}

function formatDate(dateString: string): string {
  try {
    return formatDistanceToNow(new Date(dateString), {
      addSuffix: true,
      locale: zhTW
    })
  } catch {
    return dateString
  }
}
</script>

<style scoped>
.admin-users-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 1rem;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  color: white;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.page-description {
  font-size: 1.1rem;
  opacity: 0.9;
}

.filters-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 300px;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 1rem;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1.25rem;
  height: 1.25rem;
  color: #9ca3af;
}

.role-filter {
  padding: 0.75rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  background: white;
  font-size: 1rem;
  cursor: pointer;
}

.btn-refresh {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-refresh:hover {
  background: #f3f4f6;
}

.loading-state {
  text-align: center;
  padding: 4rem;
  background: white;
  border-radius: 0.5rem;
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

.users-table-wrapper {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th {
  background: #f9fafb;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
}

.users-table td {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: bold;
}

.role-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
}

.role-admin {
  background: #fef3c7;
  color: #92400e;
}

.role-shelter {
  background: #dbeafe;
  color: #1e40af;
}

.role-general {
  background: #e5e7eb;
  color: #374151;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
}

.verified {
  background: #d1fae5;
  color: #065f46;
}

.unverified {
  background: #fee2e2;
  color: #991b1b;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-action {
  padding: 0.5rem;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-view {
  background: #dbeafe;
  color: #1e40af;
}

.btn-view:hover {
  background: #bfdbfe;
}

.btn-ban {
  background: #fee2e2;
  color: #991b1b;
}

.btn-ban:hover {
  background: #fecaca;
}

.empty-state {
  text-align: center;
  padding: 4rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  color: #9ca3af;
  margin: 0 auto 1rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  padding: 1rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.btn-page {
  padding: 0.5rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-page:hover:not(:disabled) {
  background: #5a67d8;
}

.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #374151;
  font-weight: 500;
}

/* Modal 樣式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 20px 25px rgba(0, 0, 0, 0.15);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  font-size: 1.5rem;
  font-weight: bold;
  color: #111827;
}

.btn-close {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  border-radius: 0.375rem;
  transition: all 0.3s;
}

.btn-close:hover {
  background: #f3f4f6;
  color: #111827;
}

.modal-body {
  padding: 1.5rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.detail-row .label {
  font-weight: 500;
  color: #6b7280;
}

.detail-row .value {
  color: #111827;
}

.warning-text {
  margin-bottom: 1rem;
  color: #991b1b;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.input-field {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.btn-cancel {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-danger {
  padding: 0.5rem 1rem;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>

<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 頁面標題 -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900">👤 個人資料</h1>
        <p class="mt-2 text-gray-600">管理您的帳號資訊與設定</p>
      </div>

      <!-- 載入狀態 -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-gray-600">載入中...</p>
      </div>

      <!-- 錯誤訊息 -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <p class="text-red-800">❌ {{ error }}</p>
      </div>

      <!-- Tab 導航 -->
      <div v-else class="bg-white rounded-lg shadow overflow-hidden">
        <div class="border-b border-gray-200">
          <nav class="flex -mb-px">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="currentTab = tab.id"
              :class="[
                'px-6 py-3 text-sm font-medium transition',
                currentTab === tab.id
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900 hover:border-gray-300'
              ]"
            >
              {{ tab.icon }} {{ tab.label }}
            </button>
          </nav>
        </div>

        <div class="p-6">
          <!-- Tab 1: 個人資料 -->
          <div v-if="currentTab === 'profile'" class="space-y-6">
            <form @submit.prevent="updateProfile" class="space-y-4">
              <!-- Email (唯讀) -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  電子郵件 <span class="text-red-500">*</span>
                </label>
                <input
                  type="email"
                  :value="user?.email"
                  disabled
                  class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500 cursor-not-allowed"
                />
                <p class="mt-1 text-xs text-gray-500">
                  ✅ 已驗證 | 電子郵件無法變更
                </p>
              </div>

              <!-- 使用者名稱 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">使用者名稱</label>
                <input
                  v-model="profileForm.username"
                  type="text"
                  placeholder="請輸入使用者名稱"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <!-- 姓名 -->
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">姓氏</label>
                  <input
                    v-model="profileForm.last_name"
                    type="text"
                    placeholder="姓氏"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">名字</label>
                  <input
                    v-model="profileForm.first_name"
                    type="text"
                    placeholder="名字"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <!-- 電話號碼 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">電話號碼</label>
                <input
                  v-model="profileForm.phone_number"
                  type="tel"
                  placeholder="例: 0912345678"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <!-- 地區 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">縣市</label>
                <select
                  v-model="profileForm.region"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">請選擇縣市</option>
                  <option v-for="region in taiwanRegions" :key="region" :value="region">
                    {{ region }}
                  </option>
                </select>
              </div>

              <!-- 詳細地址 (僅收容所會員顯示) -->
              <div v-if="user?.role === 'SHELTER_MEMBER'" class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    詳細地址 <span class="text-red-500">*</span>
                    <span class="text-xs text-gray-500">(收容所必填)</span>
                  </label>
                  <div class="space-y-2">
                    <input
                      v-model="profileForm.address.district"
                      type="text"
                      placeholder="區/鄉/鎮/市"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      v-model="profileForm.address.street"
                      type="text"
                      placeholder="街道地址"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      v-model="profileForm.address.postal_code"
                      type="text"
                      placeholder="郵遞區號"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>

              <!-- 一般用戶地址 (可選) -->
              <div v-else-if="user?.role === 'GENERAL_MEMBER'" class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    詳細地址 (可選)
                  </label>
                  <div class="space-y-2">
                    <input
                      v-model="profileForm.address.district"
                      type="text"
                      placeholder="區/鄉/鎮/市"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      v-model="profileForm.address.street"
                      type="text"
                      placeholder="街道地址"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>

              <!-- 角色 (唯讀) -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">帳號類型</label>
                <div class="flex items-center gap-2">
                  <span
                    :class="getRoleBadgeColor(user?.role)"
                    class="px-3 py-1 text-sm font-medium rounded-full"
                  >
                    {{ getRoleText(user?.role) }}
                  </span>
                  <span v-if="user?.primary_shelter_id" class="text-sm text-gray-600">
                    (收容所 ID: {{ user.primary_shelter_id }})
                  </span>
                </div>
              </div>

              <!-- 按鈕 -->
              <div class="flex gap-2 pt-4">
                <button
                  type="submit"
                  :disabled="saving"
                  class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {{ saving ? '儲存中...' : '💾 儲存變更' }}
                </button>
                <button
                  type="button"
                  @click="resetProfileForm"
                  class="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition"
                >
                  🔄 重置
                </button>
              </div>
            </form>
          </div>

          <!-- Tab 2: 安全設定 -->
          <div v-else-if="currentTab === 'security'" class="space-y-6">
            <form @submit.prevent="changeUserPassword" class="space-y-4 max-w-md">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">變更密碼</h3>

              <!-- 目前密碼 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  目前密碼 <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="passwordForm.old_password"
                  type="password"
                  required
                  placeholder="請輸入目前密碼"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <!-- 新密碼 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  新密碼 <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="passwordForm.new_password"
                  type="password"
                  required
                  minlength="8"
                  placeholder="至少 8 個字元"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p class="mt-1 text-xs text-gray-500">密碼至少需要 8 個字元</p>
              </div>

              <!-- 確認新密碼 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  確認新密碼 <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="passwordForm.confirm_password"
                  type="password"
                  required
                  placeholder="再次輸入新密碼"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <!-- 按鈕 -->
              <div class="flex gap-2 pt-4">
                <button
                  type="submit"
                  :disabled="changingPassword"
                  class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {{ changingPassword ? '變更中...' : '🔒 變更密碼' }}
                </button>
                <button
                  type="button"
                  @click="resetPasswordForm"
                  class="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition"
                >
                  清除
                </button>
              </div>
            </form>

            <!-- 最近登入資訊 -->
            <div v-if="user?.last_login_at" class="mt-8 p-4 bg-gray-50 rounded-lg">
              <h4 class="text-sm font-semibold text-gray-700 mb-2">🕐 帳號活動</h4>
              <p class="text-sm text-gray-600">
                最近登入時間: {{ formatDateTime(user.last_login_at) }}
              </p>
            </div>
          </div>

          <!-- Tab 3: 帳號管理 -->
          <div v-else-if="currentTab === 'account'" class="space-y-6">
            <!-- 帳號資訊 -->
            <div class="bg-gray-50 p-4 rounded-lg">
              <h3 class="text-lg font-semibold text-gray-900 mb-3">帳號資訊</h3>
              <div class="space-y-2 text-sm">
                <p><strong>帳號 ID:</strong> {{ user?.user_id }}</p>
                <p><strong>建立時間:</strong> {{ formatDateTime(user?.created_at) }}</p>
                <p><strong>更新時間:</strong> {{ formatDateTime(user?.updated_at) }}</p>
                <p><strong>驗證狀態:</strong> 
                  <span v-if="user?.verified" class="text-green-600">✅ 已驗證</span>
                  <span v-else class="text-red-600">❌ 未驗證</span>
                </p>
              </div>
            </div>

            <!-- GDPR 功能 -->
            <div class="border border-gray-200 rounded-lg p-4">
              <h3 class="text-lg font-semibold text-gray-900 mb-3">資料管理 (GDPR)</h3>

              <!-- 匯出個人資料 -->
              <div class="mb-4">
                <h4 class="text-sm font-semibold text-gray-700 mb-2">📦 匯出個人資料</h4>
                <p class="text-sm text-gray-600 mb-3">
                  下載您在平台上的所有個人資料 (JSON 格式)
                </p>
                <button
                  @click="exportData"
                  :disabled="exporting"
                  class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {{ exporting ? '處理中...' : '📥 匯出資料' }}
                </button>
              </div>

              <!-- 刪除帳號 -->
              <div class="border-t border-gray-200 pt-4">
                <h4 class="text-sm font-semibold text-red-700 mb-2">⚠️ 刪除帳號</h4>
                <p class="text-sm text-gray-600 mb-3">
                  永久刪除您的帳號與所有相關資料。此操作無法復原!
                </p>
                <button
                  @click="showDeleteConfirm = true"
                  class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition"
                >
                  🗑️ 刪除我的帳號
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 成功訊息 Toast -->
      <Transition name="fade">
        <div
          v-if="successMessage"
          class="fixed bottom-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg"
        >
          ✅ {{ successMessage }}
        </div>
      </Transition>

      <!-- 刪除確認對話框 -->
      <Transition name="fade">
        <div
          v-if="showDeleteConfirm"
          class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          @click="showDeleteConfirm = false"
        >
          <div
            class="bg-white rounded-lg p-6 max-w-md w-full mx-4"
            @click.stop
          >
            <h3 class="text-xl font-bold text-red-700 mb-4">⚠️ 確認刪除帳號</h3>
            <p class="text-gray-700 mb-4">
              此操作將永久刪除您的帳號與所有相關資料,包括:
            </p>
            <ul class="list-disc list-inside text-sm text-gray-600 mb-4 space-y-1">
              <li>個人資料</li>
              <li>送養刊登</li>
              <li>申請記錄</li>
              <li>醫療記錄</li>
              <li>通知記錄</li>
            </ul>
            <p class="text-red-600 font-semibold mb-4">此操作無法復原!</p>

            <!-- 刪除原因 -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                刪除原因 (選填)
              </label>
              <textarea
                v-model="deleteReason"
                rows="3"
                placeholder="請告訴我們為什麼要刪除帳號..."
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              ></textarea>
            </div>

            <div class="flex gap-2">
              <button
                @click="confirmDelete"
                :disabled="deleting"
                class="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition disabled:opacity-50"
              >
                {{ deleting ? '處理中...' : '確認刪除' }}
              </button>
              <button
                @click="showDeleteConfirm = false"
                class="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getUser, updateUser, changePassword, requestDataExport, requestAccountDeletion, type UserUpdateData, type ChangePasswordData } from '@/api/users'
import { updateShelter, getShelter } from '@/api/shelters'

const router = useRouter()
const authStore = useAuthStore()

// 狀態
const user = ref<any>(null)
const loading = ref(false)
const error = ref('')
const saving = ref(false)
const changingPassword = ref(false)
const exporting = ref(false)
const deleting = ref(false)
const successMessage = ref('')
const showDeleteConfirm = ref(false)
const deleteReason = ref('')

// 當前 Tab
const currentTab = ref('profile')

// Tab 定義
const tabs = [
  { id: 'profile', label: '個人資料', icon: '👤' },
  { id: 'security', label: '安全設定', icon: '🔒' },
  { id: 'account', label: '帳號管理', icon: '⚙️' }
]

// 表單資料
const profileForm = ref<UserUpdateData & { region?: string; address: any }>({
  username: '',
  phone_number: '',
  first_name: '',
  last_name: '',
  region: '',
  address: {
    district: '',
    street: '',
    postal_code: ''
  }
})

// 台灣縣市列表
const taiwanRegions = [
  '台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市',
  '基隆市', '新竹市', '嘉義市',
  '新竹縣', '苗栗縣', '彰化縣', '南投縣', '雲林縣', '嘉義縣',
  '屏東縣', '宜蘭縣', '花蓮縣', '台東縣', '澎湖縣', '金門縣', '連江縣'
]

const passwordForm = ref<ChangePasswordData & { confirm_password: string }>({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 載入使用者資料
const loadUser = async () => {
  if (!authStore.user?.user_id) {
    error.value = '未登入或無效的使用者 ID'
    console.error('❌ authStore.user:', authStore.user)
    return
  }

  loading.value = true
  error.value = ''

  try {
    console.log('🔍 載入使用者資料, user_id:', authStore.user.user_id)
    user.value = await getUser(authStore.user.user_id)
    console.log('✅ 使用者資料載入成功:', user.value)
    
    // 填充表單 - 基本資料來自用戶
    profileForm.value = {
      username: user.value.username || '',
      phone_number: user.value.phone_number || '',
      first_name: user.value.first_name || '',
      last_name: user.value.last_name || '',
      region: '',
      address: {
        district: '',
        street: '',
        postal_code: ''
      }
    }
    
    // 收容所會員：載入收容所的地區和地址資料
    if (user.value.role === 'SHELTER_MEMBER' && user.value.primary_shelter_id) {
      try {
        const shelterData = await getShelter(user.value.primary_shelter_id)
        console.log('✅ 收容所資料載入成功:', shelterData)
        
        // 使用收容所的地區和地址資料
        profileForm.value.region = shelterData.region || ''
        profileForm.value.address = shelterData.address || {
          district: '',
          street: '',
          postal_code: ''
        }
      } catch (shelterErr: any) {
        console.error('❌ 載入收容所資料失敗:', shelterErr)
        // 收容所資料載入失敗不影響主要功能，只記錄錯誤
      }
    } else {
      // 一般用戶：使用用戶的地區和地址資料
      profileForm.value.region = user.value.region || ''
      profileForm.value.address = user.value.address || {
        district: '',
        street: '',
        postal_code: ''
      }
    }
  } catch (err: any) {
    console.error('❌ 載入使用者資料失敗:', err)
    console.error('錯誤詳情:', err.response?.data)
    error.value = err.response?.data?.message || err.message || '無法載入使用者資料'
  } finally {
    loading.value = false
  }
}

// 更新個人資料
const updateProfile = async () => {
  if (!authStore.user?.user_id) return

  saving.value = true

  try {
    // 收容所會員需要分別更新用戶和收容所資料
    if (user.value?.role === 'SHELTER_MEMBER' && user.value?.primary_shelter_id) {
      // 1. 更新用戶基本資料 (username, first_name, last_name, phone_number)
      const userUpdateData = {
        username: profileForm.value.username,
        first_name: profileForm.value.first_name,
        last_name: profileForm.value.last_name,
        phone_number: profileForm.value.phone_number
      }
      user.value = await updateUser(authStore.user.user_id, userUpdateData)
      
      // 2. 更新收容所地區和地址資料
      const shelterUpdateData = {
        region: profileForm.value.region,
        address: profileForm.value.address
      }
      await updateShelter(user.value.primary_shelter_id, shelterUpdateData)
      
      showSuccess('收容所資料已更新')
    } else {
      // 一般用戶更新所有資料到用戶表
      user.value = await updateUser(authStore.user.user_id, profileForm.value)
      showSuccess('個人資料已更新')
    }
    
    // 更新 auth store
    if (authStore.user) {
      authStore.user.username = user.value.username
      authStore.user.first_name = user.value.first_name
      authStore.user.last_name = user.value.last_name
    }
  } catch (err: any) {
    alert(err.response?.data?.message || '更新失敗')
  } finally {
    saving.value = false
  }
}

// 變更密碼
const changeUserPassword = async () => {
  if (!authStore.user?.user_id) return

  // 驗證密碼一致
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    alert('新密碼與確認密碼不一致')
    return
  }

  changingPassword.value = true

  try {
    await changePassword(authStore.user.user_id, {
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password
    })
    
    showSuccess('密碼已變更')
    resetPasswordForm()
  } catch (err: any) {
    alert(err.response?.data?.message || '密碼變更失敗')
  } finally {
    changingPassword.value = false
  }
}

// 匯出資料
const exportData = async () => {
  if (!authStore.user?.user_id) return

  exporting.value = true

  try {
    const result = await requestDataExport(authStore.user.user_id)
    showSuccess(`資料匯出請求已建立 (Job ID: ${result.job_id})`)
    alert(`資料匯出正在處理中\n\nJob ID: ${result.job_id}\n\n您可以在「任務狀態」頁面查看進度`)
  } catch (err: any) {
    alert(err.response?.data?.message || '匯出請求失敗')
  } finally {
    exporting.value = false
  }
}

// 確認刪除帳號
const confirmDelete = async () => {
  if (!authStore.user?.user_id) return

  deleting.value = true

  try {
    const result = await requestAccountDeletion(authStore.user.user_id, deleteReason.value)
    showSuccess(`帳號刪除請求已建立 (Job ID: ${result.job_id})`)
    
    alert(`帳號刪除請求已提交\n\nJob ID: ${result.job_id}\n\n管理員將審核您的請求,審核通過後帳號將被刪除。\n您將在 3 秒後登出...`)
    
    // 3 秒後登出
    setTimeout(() => {
      authStore.logout()
      router.push('/login')
    }, 3000)
  } catch (err: any) {
    alert(err.response?.data?.message || '刪除請求失敗')
  } finally {
    deleting.value = false
    showDeleteConfirm.value = false
  }
}

// 重置表單
const resetProfileForm = () => {
  if (user.value) {
    profileForm.value = {
      username: user.value.username || '',
      phone_number: user.value.phone_number || '',
      first_name: user.value.first_name || '',
      last_name: user.value.last_name || '',
      region: user.value.region || '',
      address: user.value.address || {
        district: '',
        street: '',
        postal_code: ''
      }
    }
  }
}

const resetPasswordForm = () => {
  passwordForm.value = {
    old_password: '',
    new_password: '',
    confirm_password: ''
  }
}

// 顯示成功訊息
const showSuccess = (message: string) => {
  successMessage.value = message
  setTimeout(() => {
    successMessage.value = ''
  }, 3000)
}

// 格式化時間
const formatDateTime = (timestamp?: string) => {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleString('zh-TW')
}

// 取得角色文字
const getRoleText = (role?: string) => {
  switch (role) {
    case 'ADMIN': return '管理員'
    case 'SHELTER_MEMBER': return '收容所會員'
    case 'GENERAL_MEMBER': return '一般會員'
    default: return '-'
  }
}

// 取得角色顏色
const getRoleBadgeColor = (role?: string) => {
  switch (role) {
    case 'ADMIN': return 'bg-red-100 text-red-800'
    case 'SHELTER_MEMBER': return 'bg-blue-100 text-blue-800'
    case 'GENERAL_MEMBER': return 'bg-green-100 text-green-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

// 初始化
onMounted(() => {
  loadUser()
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>

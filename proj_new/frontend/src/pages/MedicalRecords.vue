<template>
  <div class="medical-records-page min-h-screen bg-gray-50 py-8">
    <div class="container mx-auto px-4 max-w-7xl">
      <!-- 頁面標題和說明 -->
      <div class="page-header mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-4">動物醫療記錄管理</h1>
        
        <!-- 角色說明 -->
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
          <div class="flex items-start gap-3">
            <div class="text-2xl">🏥</div>
            <div>
              <h2 class="text-lg font-semibold text-blue-900 mb-2">醫療記錄管理說明</h2>
              <template v-if="authStore.user?.role === 'ADMIN'">
                <p class="text-blue-800 mb-2">作為系統管理員，您可以：</p>
                <ul class="list-disc list-inside text-blue-800 space-y-1">
                  <li><strong>查看所有動物</strong>：管理平台上所有動物的醫療記錄</li>
                  <li><strong>新增/編輯記錄</strong>：為任何動物建立或修改醫療記錄</li>
                  <li><strong>驗證記錄</strong>：驗證醫療記錄的真實性和準確性</li>
                  <li><strong>全面監管</strong>：確保醫療記錄的品質和合規性</li>
                </ul>
              </template>
              <template v-else-if="authStore.user?.role === 'SHELTER_MEMBER'">
                <p class="text-blue-800 mb-2">作為收容所會員，您可以：</p>
                <ul class="list-disc list-inside text-blue-800 space-y-1">
                  <li><strong>管理收容所動物</strong>：為所屬收容所的動物建立醫療記錄</li>
                  <li><strong>記錄治療過程</strong>：追蹤疫苗、治療、手術等醫療活動</li>
                  <li><strong>提高透明度</strong>：完整的醫療記錄有助於動物領養</li>
                  <li><strong>協助獸醫管理</strong>：建立完整的健康檔案</li>
                </ul>
              </template>
              <template v-else>
                <p class="text-blue-800 mb-2">作為動物主人，您可以：</p>
                <ul class="list-disc list-inside text-blue-800 space-y-1">
                  <li><strong>管理寵物健康</strong>：為您的動物建立完整醫療記錄</li>
                  <li><strong>記錄重要資訊</strong>：疫苗接種、健檢、治療等記錄</li>
                  <li><strong>提升領養機會</strong>：完整的醫療記錄增加領養者信心</li>
                  <li><strong>健康追蹤</strong>：持續監控動物的健康狀況</li>
                </ul>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- 篩選面板 -->
      <div class="mb-6 bg-white p-4 rounded-lg shadow-sm">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">名稱</label>
            <input v-model="filters.name" type="text" placeholder="輸入名稱或關鍵字" class="w-full border border-gray-300 rounded-md px-3 py-2" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">物種</label>
            <select v-model="filters.species" class="w-full border border-gray-300 rounded-md px-3 py-2">
              <option value="">全部</option>
              <option value="CAT">貓</option>
              <option value="DOG">狗</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">品種</label>
            <input v-model="filters.breed" type="text" placeholder="品種（部分匹配）" class="w-full border border-gray-300 rounded-md px-3 py-2" />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">年齡</label>
            <select
              v-model="ageRange"
              class="w-full border border-gray-300 rounded-md px-3 py-2"
              @change="handleAgeChange"
            >
              <option value="">全部年齡</option>
              <option value="0-6">幼年 (0-6個月)</option>
              <option value="6-12">青少年 (6個月-1歲)</option>
              <option value="12-36">成年 (1-3歲)</option>
              <option value="36-84">中年 (3-7歲)</option>
              <option value="84-999">老年 (7歲以上)</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">是否已領養</label>
              <select v-model="filters.adopted" class="w-full border border-gray-300 rounded-md px-3 py-2">
                <option value="">全部</option>
                <option :value="true">已領養</option>
                <option :value="false">未領養</option>
              </select>
          </div>

          <div>
            <!-- 空間保留，用於未來擴充 -->
          </div>
        </div>

        <div class="mt-4 flex items-center gap-3">
          <button @click="applyFilters" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">搜尋</button>
          <button @click="clearFilters" class="px-4 py-2 border rounded-md">清除</button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
        <p class="text-gray-600">載入中...</p>
      </div>

      <!-- 動物列表為空 -->
      <div v-else-if="animals.length === 0" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="text-gray-600 mb-4">
          <template v-if="authStore.user?.role === 'SHELTER_MEMBER'">
            您的收容所尚無動物記錄
          </template>
          <template v-else>
            您尚無動物記錄
          </template>
        </p>
        <button @click="goToAddAnimal" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition">
          <template v-if="authStore.user?.role === 'SHELTER_MEMBER'">
            前往批次匯入動物
          </template>
          <template v-else>
            前往新增動物
          </template>
        </button>
      </div>

      <!-- 動物卡片網格 -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <div 
          v-for="animal in animals" 
          :key="animal.animal_id" 
          class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition cursor-pointer"
          @click="selectAnimal(animal)"
        >
          <!-- 動物圖片 -->
          <div class="h-48 bg-gray-200 relative">
            <img 
              v-if="animal.images && animal.images.length > 0" 
              :src="animal.images[0].url" 
              :alt="animal.name || `動物 #${animal.animal_id}`"
              class="w-full h-full object-cover"
            />
            <div v-else class="w-full h-full flex items-center justify-center">
              <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
          
          <!-- 動物資訊 -->
          <div class="p-4">
            <h3 class="text-lg font-semibold text-gray-900 mb-2">
              {{ animal.name || `動物 #${animal.animal_id}` }}
            </h3>
            <div class="flex gap-2 mb-2">
              <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getSpeciesClass(animal.species)">
                {{ getSpeciesLabel(animal.species) }}
              </span>
              <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getStatusClass(animal.status)">
                {{ getStatusLabel(animal.status) }}
              </span>
            </div>
            <p class="text-gray-600 text-sm mb-2">{{ animal.breed || '未知品種' }}</p>
            <p class="text-gray-500 text-sm" v-if="animal.age !== undefined">{{ animal.age }} 歲</p>
            
            <div class="mt-4">
              <button class="w-full px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition">
                📋 查看醫療記錄
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 醫療記錄詳情 Modal -->
    <div v-if="selectedAnimal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click.self="closeAnimalModal">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <!-- Modal 標題 -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 class="text-2xl font-bold text-gray-900">
            {{ selectedAnimal.name || `動物 #${selectedAnimal.animal_id}` }} 的醫療記錄
          </h2>
          <button @click="closeAnimalModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-6">
          <!-- 動物摘要 -->
          <div class="flex items-center gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
            <div class="w-16 h-16 rounded-full overflow-hidden bg-gray-200">
              <img 
                v-if="selectedAnimal.images && selectedAnimal.images.length > 0" 
                :src="selectedAnimal.images[0].url" 
                :alt="selectedAnimal.name || `動物 #${selectedAnimal.animal_id}`"
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full flex items-center justify-center">
                <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
            <div class="flex-1">
              <h3 class="text-xl font-semibold text-gray-900">
                {{ selectedAnimal.name || `動物 #${selectedAnimal.animal_id}` }}
              </h3>
              <div class="flex gap-2 mt-2">
                <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getSpeciesClass(selectedAnimal.species)">
                  {{ getSpeciesLabel(selectedAnimal.species) }}
                </span>
                <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getStatusClass(selectedAnimal.status)">
                  {{ getStatusLabel(selectedAnimal.status) }}
                </span>
              </div>
              <p class="text-gray-600 mt-1">
                {{ selectedAnimal.breed || '未知品種' }}
                <span v-if="selectedAnimal.age !== undefined">・{{ selectedAnimal.age }} 歲</span>
              </p>
            </div>
            <div v-if="canManageSelectedAnimal">
              <button @click="openAddModal" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition flex items-center gap-2">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                新增醫療記錄
              </button>
            </div>
          </div>

          <!-- 醫療記錄載入中 -->
          <div v-if="loadingRecords" class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mb-2"></div>
            <p class="text-gray-600">載入醫療記錄中...</p>
          </div>

          <!-- 無醫療記錄 -->
          <div v-else-if="records.length === 0" class="text-center py-8">
            <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="text-gray-600 mb-4">此動物尚無醫療記錄</p>
            <button v-if="canManageSelectedAnimal" @click="openAddModal" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition">
              新增第一筆記錄
            </button>
          </div>

          <!-- 醫療記錄時間線 -->
          <div v-else class="space-y-4">
            <div 
              v-for="record in records" 
              :key="record.medical_record_id" 
              class="bg-white border border-gray-200 rounded-lg p-4"
            >
              <div class="flex items-start justify-between mb-3">
                <div class="flex items-center gap-3">
                  <span class="px-3 py-1 text-sm font-medium rounded-full" :class="getRecordTypeClass(record.record_type)">
                    {{ getRecordTypeLabel(record.record_type) }}
                  </span>
                  <span class="text-gray-600 font-medium">{{ formatDate(record.date) }}</span>
                  <span v-if="record.verified" class="flex items-center gap-1 px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                    已驗證
                  </span>
                </div>
                <div class="flex items-center gap-2">
                  <button 
                    v-if="canEditRecord(record)" 
                    @click="openEditModal(record)" 
                    class="p-2 text-gray-400 hover:text-blue-600 transition"
                    title="編輯"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  
                  <!-- 管理員驗證按鈕組 -->
                  <div v-if="isAdmin" class="flex items-center gap-1">
                    <button 
                      v-if="!record.verified"
                      @click="handleVerify(record.medical_record_id, true)" 
                      class="px-3 py-1 bg-green-100 text-green-700 hover:bg-green-200 transition rounded-md text-sm font-medium"
                      title="驗證此醫療記錄"
                    >
                      ✓ 驗證
                    </button>
                    <button 
                      v-else
                      @click="handleVerify(record.medical_record_id, false)" 
                      class="px-3 py-1 bg-red-100 text-red-700 hover:bg-red-200 transition rounded-md text-sm font-medium"
                      title="撤銷驗證"
                    >
                      ✗ 撤銷驗證
                    </button>
                  </div>
                </div>
              </div>

              <div class="space-y-2">
                <div v-if="record.provider" class="text-gray-700">
                  <strong class="text-gray-900">醫療提供者：</strong> {{ record.provider }}
                </div>
                <div v-if="record.details" class="text-gray-700">
                  <strong class="text-gray-900">詳細說明：</strong>
                  <p class="mt-1 whitespace-pre-wrap">{{ record.details }}</p>
                </div>
                <div v-if="record.attachments && record.attachments.length > 0" class="text-gray-700">
                  <strong class="text-gray-900">證明文件：</strong>
                  <div class="mt-2 grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div 
                      v-for="(attachment, index) in record.attachments" 
                      :key="index" 
                      class="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition cursor-pointer"
                      @click="viewAttachment(attachment)"
                    >
                      <div class="flex items-center gap-3">
                        <!-- 文件圖示 -->
                        <div class="flex-shrink-0">
                          <svg v-if="isImageFile(attachment.filename)" class="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                          <svg v-else-if="isPDFFile(attachment.filename)" class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                          </svg>
                          <svg v-else class="w-8 h-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </div>
                        
                        <!-- 文件信息 -->
                        <div class="flex-1 min-w-0">
                          <p class="text-sm font-medium text-gray-900 truncate">
                            {{ attachment.filename || attachment.name || '未知檔案' }}
                          </p>
                          <p class="text-xs text-gray-500">
                            {{ getFileTypeLabel(attachment.filename) }}
                            <span v-if="attachment.size">・{{ formatFileSize(attachment.size) }}</span>
                          </p>
                        </div>
                        
                        <!-- 操作按鈕 -->
                        <div class="flex items-center gap-2">
                          <button 
                            @click.stop="downloadAttachment(attachment)"
                            class="p-1 text-gray-400 hover:text-blue-600 transition"
                            title="下載"
                          >
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                          </button>
                          <button 
                            @click.stop="viewAttachment(attachment)"
                            class="p-1 text-gray-400 hover:text-green-600 transition"
                            title="查看"
                          >
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="mt-3 pt-3 border-t border-gray-200 text-sm text-gray-500">
                建立於 {{ formatDateTime(record.created_at) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新增/編輯醫療記錄 Modal -->
    <div v-if="showMedicalRecordModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click.self="closeMedicalRecordModal">
      <div class="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 class="text-xl font-bold text-gray-900">
            {{ editingRecord ? '編輯醫療記錄' : '新增醫療記錄' }}
          </h2>
          <button @click="closeMedicalRecordModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-6">
          <form @submit.prevent="submitMedicalRecord" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  記錄類型 <span class="text-red-500">*</span>
                </label>
                <select v-model="formData.recordType" required class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option value="">請選擇</option>
                  <option value="VACCINE">疫苗接種</option>
                  <option value="TREATMENT">治療</option>
                  <option value="SURGERY">手術</option>
                  <option value="CHECKUP">健康檢查</option>
                  <option value="OTHER">其他</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  日期 <span class="text-red-500">*</span>
                </label>
                <input 
                  type="date" 
                  v-model="formData.date" 
                  required 
                  class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">醫療提供者</label>
              <input 
                type="text" 
                v-model="formData.provider" 
                placeholder="獸醫姓名或醫院名稱"
                class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">詳細說明</label>
              <textarea 
                v-model="formData.details" 
                rows="4" 
                placeholder="請描述治療詳情、藥物、建議等..."
                class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              ></textarea>
            </div>

            <!-- 文件上傳區域 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                證明文件 
                <span class="text-sm font-normal text-gray-500">(請上傳醫療證明、檢驗報告或相關照片)</span>
              </label>
              
              <!-- 文件上傳區 -->
              <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition">
                <input 
                  ref="fileInput"
                  type="file" 
                  multiple 
                  accept="image/*,.pdf,.doc,.docx"
                  @change="handleFileSelect"
                  class="hidden"
                />
                
                <div @click="$refs.fileInput?.click()" class="cursor-pointer">
                  <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p class="text-sm text-gray-600 mb-2">點擊上傳文件或拖拽文件到此處</p>
                  <p class="text-xs text-gray-500">支援 JPG, PNG, PDF, DOC, DOCX 格式，單檔最大 10MB</p>
                </div>
              </div>
              
              <!-- 已選擇的文件列表 -->
              <div v-if="selectedFiles.length > 0" class="mt-4 space-y-2">
                <h4 class="text-sm font-medium text-gray-700">已選擇的文件：</h4>
                <div v-for="(file, index) in selectedFiles" :key="index" 
                     class="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                  <div class="flex items-center gap-3">
                    <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <div>
                      <p class="text-sm font-medium text-gray-900">{{ file.name }}</p>
                      <p class="text-xs text-gray-500">{{ formatFileSize(file.size) }}</p>
                    </div>
                  </div>
                  <button 
                    type="button" 
                    @click="removeFile(index)"
                    class="text-red-500 hover:text-red-700 transition"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              
              <!-- 上傳中的進度 -->
              <div v-if="uploadProgress > 0 && uploadProgress < 100" class="mt-4">
                <div class="flex justify-between text-sm text-gray-600 mb-1">
                  <span>上傳中...</span>
                  <span>{{ uploadProgress }}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" :style="{ width: uploadProgress + '%' }"></div>
                </div>
              </div>
            </div>

            <div class="flex justify-end gap-3 pt-4 border-t border-gray-200">
              <button type="button" @click="closeMedicalRecordModal" class="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50 transition">
                取消
              </button>
              <button type="submit" :disabled="submitting" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50">
                {{ submitting ? '儲存中...' : (editingRecord ? '更新' : '新增') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 文件查看 Modal -->
    <div v-if="showAttachmentModal" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4" @click.self="closeAttachmentModal">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <!-- Modal 標題 -->
        <div class="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 class="text-lg font-bold text-gray-900">
            {{ currentAttachment?.filename || '查看文件' }}
          </h2>
          <div class="flex items-center gap-3">
            <button 
              @click="downloadAttachment(currentAttachment)"
              class="px-3 py-1 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
            >
              下載
            </button>
            <button @click="closeAttachmentModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 文件內容 -->
        <div class="p-4 max-h-[calc(90vh-120px)] overflow-auto">
          <!-- 圖片預覽 -->
          <div v-if="isImageFile(currentAttachment?.filename)" class="text-center">
            <img 
              :src="currentAttachment?.url" 
              :alt="currentAttachment?.filename"
              class="max-w-full max-h-[70vh] mx-auto rounded-lg shadow-lg"
            />
          </div>
          
          <!-- PDF 預覽 -->
          <div v-else-if="isPDFFile(currentAttachment?.filename)" class="text-center">
            <iframe 
              :src="currentAttachment?.url" 
              class="w-full h-[70vh] border rounded-lg"
              title="PDF 預覽"
            >
            </iframe>
          </div>
          
          <!-- 其他文件類型 -->
          <div v-else class="text-center py-12">
            <svg class="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="text-gray-600 mb-4">此文件類型無法在瀏覽器中預覽</p>
            <p class="text-sm text-gray-500 mb-4">
              檔案：{{ currentAttachment?.filename }}<br>
              類型：{{ getFileTypeLabel(currentAttachment?.filename) }}<br>
              <span v-if="currentAttachment?.size">大小：{{ formatFileSize(currentAttachment.size) }}</span>
            </p>
            <button 
              @click="downloadAttachment(currentAttachment)"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
            >
              下載查看
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/client'
import { getAnimals } from '@/api/animals'
import { getMedicalRecords, createMedicalRecord, updateMedicalRecord, verifyMedicalRecord, getAnimalsForMedicalRecords } from '@/api/medicalRecords'
import { uploadFile } from '@/api/uploads'

const router = useRouter()
const authStore = useAuthStore()

// 響應式數據
const loading = ref(false)
const animals = ref([])
const selectedAnimal = ref(null)
const records = ref([])
const loadingRecords = ref(false)
const showMedicalRecordModal = ref(false)
const editingRecord = ref(null)
const submitting = ref(false)

// 文件上傳相關
const selectedFiles = ref([])
const uploadProgress = ref(0)
const fileInput = ref(null)

// 文件查看相關
const showAttachmentModal = ref(false)
const currentAttachment = ref(null)

const formData = reactive({
  recordType: '',
  date: '',
  provider: '',
  details: ''
})

// 計算屬性
const isAdmin = computed(() => authStore.user?.role === 'ADMIN')
const canManageSelectedAnimal = computed(() => {
  if (!selectedAnimal.value) return false
  
  const user = authStore.user
  
  // 管理員不能直接創建醫療記錄（保護醫療記錄的專業性）
  if (user.role === 'ADMIN') return false
  
  // 檢查是否為動物擁有者
  if (selectedAnimal.value.owner_id === user.user_id) return true
  
  // 檢查是否為收容所成員且動物屬於該收容所
  if (user.role === 'SHELTER_MEMBER' && 
      user.primary_shelter_id && 
      selectedAnimal.value.shelter_id === user.primary_shelter_id) {
    return true
  }
  
  return false
})

// 篩選條件
const filters = reactive({
  name: '',
  species: '',
  breed: '',
  min_age: null,
  max_age: null,
  adopted: ''
})

// 與 /animals 頁面一致的年齡範圍控制
const ageRange = ref('')

// 載入動物列表（支援篩選）
const loadAnimals = async (params = {}) => {
  loading.value = true
  try {
    console.log('🔍 載入動物列表（醫療記錄權限） with params', params)
    const response = await getAnimalsForMedicalRecords(params)
    animals.value = response.animals || []
    console.log('📋 載入到的動物數量:', animals.value.length)
  } catch (error) {
    console.error('載入動物列表失敗:', error)
  } finally {
    loading.value = false
  }
}

const applyFilters = async () => {
  const params = {}
  if (filters.name) params.name = filters.name
  if (filters.species) params.species = filters.species
  if (filters.breed) params.breed = filters.breed
  if (filters.min_age !== null && filters.min_age !== '') params.min_age = filters.min_age
  if (filters.max_age !== null && filters.max_age !== '') params.max_age = filters.max_age
  if (filters.adopted !== '') params.adopted = filters.adopted

  await loadAnimals(params)
}

const clearFilters = async () => {
  filters.name = ''
  filters.species = ''
  filters.breed = ''
  filters.min_age = null
  filters.max_age = null
  filters.adopted = ''
  ageRange.value = ''
  await loadAnimals()
}

// 將 ageRange 轉換為 min_age / max_age (單位：月)
const handleAgeChange = () => {
  if (!ageRange.value) {
    filters.min_age = null
    filters.max_age = null
  } else {
    const [min, max] = ageRange.value.split('-').map(v => parseInt(v, 10))
    filters.min_age = isNaN(min) ? null : min
    filters.max_age = (isNaN(max) || max === 999) ? null : max
  }
  // 立即套用
  applyFilters()
}

// 載入醫療記錄
const loadMedicalRecords = async (animalId) => {
  loadingRecords.value = true
  try {
    const response = await getMedicalRecords(animalId)
    records.value = response.medical_records || []
  } catch (error) {
    console.error('載入醫療記錄失敗:', error)
  } finally {
    loadingRecords.value = false
  }
}

// 選擇動物
const selectAnimal = async (animal) => {
  selectedAnimal.value = animal
  await loadMedicalRecords(animal.animal_id)
}

// 關閉動物詳情 Modal
const closeAnimalModal = () => {
  selectedAnimal.value = null
  records.value = []
}

// 開啟新增醫療記錄 Modal
const openAddModal = () => {
  editingRecord.value = null
  formData.recordType = ''
  formData.date = ''
  formData.provider = ''
  formData.details = ''
  selectedFiles.value = []
  uploadProgress.value = 0
  showMedicalRecordModal.value = true
}

// 開啟編輯醫療記錄 Modal
const openEditModal = (record) => {
  editingRecord.value = record
  formData.recordType = record.record_type
  formData.date = record.date
  formData.provider = record.provider || ''
  formData.details = record.details || ''
  selectedFiles.value = []
  uploadProgress.value = 0
  showMedicalRecordModal.value = true
}

// 關閉醫療記錄 Modal
const closeMedicalRecordModal = () => {
  showMedicalRecordModal.value = false
  editingRecord.value = null
  // 清空文件選擇
  selectedFiles.value = []
  uploadProgress.value = 0
}

// 文件處理函數
const handleFileSelect = (event) => {
  const files = Array.from(event.target.files || [])
  
  // 驗證文件
  for (const file of files) {
    // 檢查檔案大小 (10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert(`檔案 "${file.name}" 超過 10MB 限制`)
      continue
    }
    
    // 檢查檔案類型
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 
                         'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!allowedTypes.includes(file.type)) {
      alert(`檔案 "${file.name}" 格式不支援`)
      continue
    }
    
    selectedFiles.value.push(file)
  }
  
  // 清空 input
  if (event.target) {
    event.target.value = ''
  }
}

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 檢查是否為圖片文件
const isImageFile = (filename) => {
  if (!filename) return false
  const ext = filename.toLowerCase().split('.').pop()
  return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'].includes(ext)
}

// 檢查是否為 PDF 文件
const isPDFFile = (filename) => {
  if (!filename) return false
  return filename.toLowerCase().endsWith('.pdf')
}

// 獲取文件類型標籤
const getFileTypeLabel = (filename) => {
  if (!filename) return '未知'
  const ext = filename.toLowerCase().split('.').pop()
  
  const typeMap = {
    'pdf': 'PDF',
    'doc': 'Word',
    'docx': 'Word',
    'jpg': '圖片',
    'jpeg': '圖片',
    'png': '圖片',
    'gif': '圖片',
    'bmp': '圖片',
    'webp': '圖片',
    'svg': '圖片',
    'txt': '文字',
    'rtf': '文字'
  }
  
  return typeMap[ext] || ext.toUpperCase()
}

// 查看附件
const viewAttachment = (attachment) => {
  currentAttachment.value = attachment
  showAttachmentModal.value = true
}

// 下載附件
const downloadAttachment = async (attachment) => {
  try {
    const response = await fetch(attachment.url)
    const blob = await response.blob()
    
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = attachment.filename || 'download'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('下載文件失敗:', error)
    alert('下載文件失敗，請重試')
  }
}

// 關閉附件查看 Modal
const closeAttachmentModal = () => {
  showAttachmentModal.value = false
  currentAttachment.value = null
}

// 提交醫療記錄
const submitMedicalRecord = async () => {
  submitting.value = true
  uploadProgress.value = 0
  
  try {
    let attachments = []
    
    // 先上傳檔案
    if (selectedFiles.value.length > 0) {
      console.log('上傳檔案中...')
      uploadProgress.value = 10
      
      for (let i = 0; i < selectedFiles.value.length; i++) {
        const file = selectedFiles.value[i]
        const progressStep = 70 / selectedFiles.value.length
        
        try {
          const uploadResult = await uploadFile(
            file,
            'medical_record',
            editingRecord.value?.medical_record_id || 0,
            (progress) => {
              uploadProgress.value = 10 + (i * progressStep) + (progress * progressStep / 100)
            }
          )
          
          attachments.push({
            filename: uploadResult.filename,
            storage_key: uploadResult.storage_key,
            url: uploadResult.url,
            mime_type: uploadResult.mime_type,
            size: uploadResult.size
          })
        } catch (uploadError) {
          console.error(`上傳檔案 ${file.name} 失敗:`, uploadError)
          alert(`上傳檔案 "${file.name}" 失敗，請重試`)
          return
        }
      }
      
      uploadProgress.value = 80
    }
    
    const data = {
      record_type: formData.recordType,
      date: formData.date,
      provider: formData.provider,
      details: formData.details,
      attachments: attachments
    }
    
    uploadProgress.value = 90
    
    if (editingRecord.value) {
      await updateMedicalRecord(editingRecord.value.medical_record_id, data)
      console.log('醫療記錄已更新')
    } else {
      await createMedicalRecord(selectedAnimal.value.animal_id, data)
      console.log('醫療記錄已新增')
    }
    
    uploadProgress.value = 100
    closeMedicalRecordModal()
    await loadMedicalRecords(selectedAnimal.value.animal_id)
  } catch (error) {
    console.error('提交醫療記錄失敗:', error)
    alert('提交醫療記錄失敗，請重試')
  } finally {
    submitting.value = false
    uploadProgress.value = 0
  }
}

// 驗證醫療記錄
const handleVerify = async (recordId, verified) => {
  try {
    await verifyMedicalRecord(recordId, verified)
    
    // 更新本地記錄狀態
    const recordIndex = records.value.findIndex(r => r.medical_record_id === recordId)
    if (recordIndex !== -1) {
      records.value[recordIndex].verified = verified
      records.value[recordIndex].verified_by = verified ? authStore.user?.user_id : null
    }
    
    // 顯示成功消息
    const message = verified ? '✅ 醫療記錄已驗證' : '❌ 醫療記錄驗證已撤銷'
    alert(message)
    
    console.log(verified ? '醫療記錄已驗證' : '醫療記錄驗證已撤銷')
  } catch (error) {
    console.error('驗證醫療記錄失敗:', error)
    alert('操作失敗，請重試')
  }
}

// 檢查是否可編輯記錄
const canEditRecord = (record) => {
  const user = authStore.user
  if (!user) return false
  
  // 管理員不能直接編輯醫療記錄（僅能查看和驗證）
  if (user.role === 'ADMIN') return false
  
  // SHELTER_MEMBER 可以編輯庇護所動物的記錄
  if (user.role === 'SHELTER_MEMBER' && 
      user.primary_shelter_id && 
      selectedAnimal.value?.shelter_id === user.primary_shelter_id) {
    return true
  }
  
  // 動物擁有者可以編輯
  if (selectedAnimal.value?.owner_id === user.user_id) {
    return true
  }
  
  // 記錄創建者可以編輯（限時編輯，例如創建後24小時內）
  if (record.created_by === user.user_id) {
    const createdAt = new Date(record.created_at)
    const now = new Date()
    const hoursDiff = (now - createdAt) / (1000 * 60 * 60)
    return hoursDiff <= 24 // 24小時內可編輯
  }
  
  return false
}

// 前往新增動物頁面
const goToAddAnimal = () => {
  if (authStore.user.role === 'SHELTER_MEMBER') {
    router.push('/batch-import')
  } else {
    router.push('/add-animal')
  }
}

// 輔助函數
const getSpeciesLabel = (species) => {
  const labels = {
    'DOG': '🐕 狗',
    'CAT': '🐱 貓',
    'BIRD': '🐦 鳥',
    'RABBIT': '🐰 兔',
    'OTHER': '🐾 其他'
  }
  return labels[species] || '🐾 未知'
}

const getSpeciesClass = (species) => {
  const classes = {
    'DOG': 'bg-blue-100 text-blue-800',
    'CAT': 'bg-purple-100 text-purple-800',
    'BIRD': 'bg-green-100 text-green-800',
    'RABBIT': 'bg-yellow-100 text-yellow-800',
    'OTHER': 'bg-gray-100 text-gray-800'
  }
  return classes[species] || 'bg-gray-100 text-gray-800'
}

const getStatusLabel = (status) => {
  const labels = {
    'AVAILABLE': '可領養',
    'ADOPTED': '已領養',
    'RESERVED': '預約中',
    'MEDICAL': '醫療中',
    'UNAVAILABLE': '不可領養'
  }
  return labels[status] || status
}

const getStatusClass = (status) => {
  const classes = {
    'AVAILABLE': 'bg-green-100 text-green-800',
    'ADOPTED': 'bg-blue-100 text-blue-800',
    'RESERVED': 'bg-yellow-100 text-yellow-800',
    'MEDICAL': 'bg-red-100 text-red-800',
    'UNAVAILABLE': 'bg-gray-100 text-gray-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getRecordTypeLabel = (type) => {
  const labels = {
    'VACCINE': '💉 疫苗接種',
    'TREATMENT': '💊 治療',
    'SURGERY': '🏥 手術',
    'CHECKUP': '🩺 健康檢查',
    'OTHER': '📋 其他'
  }
  return labels[type] || type
}

const getRecordTypeClass = (type) => {
  const classes = {
    'VACCINE': 'bg-green-100 text-green-800',
    'TREATMENT': 'bg-blue-100 text-blue-800',
    'SURGERY': 'bg-red-100 text-red-800',
    'CHECKUP': 'bg-purple-100 text-purple-800',
    'OTHER': 'bg-gray-100 text-gray-800'
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('zh-TW')
}

const formatDateTime = (datetime) => {
  return new Date(datetime).toLocaleString('zh-TW')
}

// 初始化
onMounted(() => {
  loadAnimals()
})
</script>
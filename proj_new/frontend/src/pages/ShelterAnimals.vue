<template>
  <div class="shelter-animals-page min-h-screen bg-gray-50 py-8">
    <div class="container mx-auto px-4 max-w-7xl">
      <!-- Header -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 mb-2">收容所動物管理</h1>
          <p class="text-gray-600">管理收容所的所有動物，支援批次狀態操作</p>
          <p class="text-sm text-blue-600 mt-1"> 此處管理的是收容所機構的動物，如需單次送養請前往「我的送養」</p>
        </div>
        <div class="flex gap-2">
          <button
            @click="router.push('/my-rehomes')"
            class="px-4 py-2 text-sm font-medium text-blue-700 bg-blue-50 border border-blue-300 rounded-md hover:bg-blue-100 transition"
          >
             單次送養
          </button>
          <button
            @click="router.push('/shelter/dashboard')"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition"
          >
             返回收容所管理
          </button>
        </div>
      </div>

      <!-- 篩選和批次操作區域 -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-8">
        <!-- 篩選區 -->
        <div class="grid md:grid-cols-4 gap-4 mb-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">狀態篩選</label>
            <select
              v-model="filters.status"
              @change="loadAnimals"
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">全部狀態</option>
              <option value="DRAFT">📝 草稿</option>
              <option value="SUBMITTED">📋 已提交</option>
              <option value="PUBLISHED">✅ 已發布</option>
              <option value="ADOPTED">🏠 已領養</option>
              <option value="RETIRED">❌ 已下架</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">物種篩選</label>
            <select
              v-model="filters.species"
              @change="loadAnimals"
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">全部物種</option>
              <option value="CAT"> 貓</option>
              <option value="DOG"> 狗</option>
            </select>
          </div>
          
          <div class="md:col-span-2 flex items-end gap-2">
            <button
              @click="loadAnimals"
              class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
            >
               搜尋
            </button>
            <button
              @click="resetFilters"
              class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition"
            >
              清除篩選
            </button>
          </div>
        </div>

        <!-- 批次操作區 -->
        <div v-if="selectedAnimals.length > 0" class="border-t pt-4 bg-blue-50 rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-4">
              <div class="flex items-center gap-2">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  已選擇 {{ selectedAnimals.length }} 隻動物
                </span>
              </div>
              <div class="flex gap-2">
                <button
                  @click="clearSelection"
                  class="text-xs text-gray-600 hover:text-red-600 underline transition"
                >
                  清除選擇
                </button>
                <button
                  @click="toggleSelectAll"
                  class="text-xs text-blue-600 hover:text-blue-700 underline transition"
                >
                  {{ isAllSelected ? '取消全選' : '全選本頁' }}
                </button>
              </div>
            </div>
            
            <div class="relative">
              <!-- 批次操作選單按鈕 -->
              <button
                @click="showBatchMenu = !showBatchMenu"
                :disabled="batchUpdating"
                class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition shadow-sm"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
                </svg>
                <span>{{ batchUpdating ? '處理中...' : '批次操作' }}</span>
                <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <!-- 批次操作下拉選單 -->
              <div v-if="showBatchMenu" class="absolute right-0 top-full mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
                <div class="py-2">
                  <!-- 提交審核 -->
                  <button
                    @click="batchUpdateStatus('submit')"
                    :disabled="batchUpdating || !canBatchSubmit"
                    class="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                  >
                    <svg class="w-4 h-4 mr-3 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div>
                      <div class="font-medium">提交審核</div>
                      <div class="text-xs text-gray-500">將草稿狀態動物提交給管理員審核</div>
                    </div>
                  </button>

                  <!-- 發布上架 -->
                  <button
                    @click="batchUpdateStatus('publish')"
                    :disabled="batchUpdating || !canBatchPublish"
                    class="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                  >
                    <svg class="w-4 h-4 mr-3 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <div>
                      <div class="font-medium">發布上架</div>
                      <div class="text-xs text-gray-500">直接發布已提交的動物</div>
                    </div>
                  </button>

                  <!-- 下架 -->
                  <button
                    @click="batchUpdateStatus('retire')"
                    :disabled="batchUpdating || !canBatchRetire"
                    class="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                  >
                    <svg class="w-4 h-4 mr-3 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    <div>
                      <div class="font-medium">下架</div>
                      <div class="text-xs text-gray-500">將已發布的動物下架</div>
                    </div>
                  </button>

                  <!-- 分隔線 -->
                  <div class="border-t border-gray-100 my-1"></div>

                  <!-- 批次刪除 (僅草稿) -->
                  <button
                    @click="batchDeleteAnimals"
                    :disabled="batchUpdating || !canBatchDelete"
                    class="w-full px-4 py-2 text-left text-sm hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                    :class="{ 'text-red-600': canBatchDelete, 'text-gray-400': !canBatchDelete }"
                  >
                    <svg class="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    <div>
                      <div class="font-medium">刪除</div>
                      <div class="text-xs text-gray-500">
                        {{ canBatchDelete ? '永久刪除草稿狀態的動物' : '只能刪除草稿狀態的動物' }}
                      </div>
                    </div>
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 選中動物預覽 -->
          <div v-if="selectedAnimals.length > 0 && selectedAnimals.length <= 6" class="mt-3">
            <div class="text-xs text-gray-600 mb-2">已選中的動物：</div>
            <div class="flex flex-wrap gap-2">
              <div
                v-for="animalId in selectedAnimals.slice(0, 6)"
                :key="animalId"
                class="inline-flex items-center px-2 py-1 bg-white border border-blue-200 rounded text-xs"
              >
                <span class="text-blue-600 mr-1">🐾</span>
                {{ getAnimalName(animalId) }}
                <button
                  @click="toggleAnimal(animalId)"
                  class="ml-2 text-gray-400 hover:text-red-500 transition"
                >
                  ×
                </button>
              </div>
              <div v-if="selectedAnimals.length > 6" class="inline-flex items-center px-2 py-1 bg-gray-100 rounded text-xs text-gray-600">
                還有 {{ selectedAnimals.length - 6 }} 隻...
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading 狀態 -->
      <div v-if="isLoading && !animals.length" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-gray-600">載入中...</p>
      </div>

      <!-- 錯誤訊息 -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-8">
        {{ error }}
      </div>

      <!-- 動物列表 -->
      <div v-else-if="animals.length > 0">
        <!-- 結果摘要 -->
        <div class="mb-4 text-sm text-gray-600 flex justify-between items-center">
          <span>找到 {{ pagination.total }} 隻動物，顯示第 {{ pagination.page }} 頁 (共 {{ pagination.pages }} 頁)</span>
          <div class="flex items-center gap-4">
            <!-- 選擇統計 -->
            <div v-if="selectedAnimals.length > 0" class="text-blue-600 font-medium">
              已選 {{ selectedAnimals.length }}/{{ animals.length }}
            </div>
            <!-- 全選控制 -->
            <div class="flex items-center gap-2">
              <input
                type="checkbox"
                :checked="isAllSelected"
                :indeterminate="selectedAnimals.length > 0 && !isAllSelected"
                @change="toggleSelectAll"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
              />
              <label class="text-sm cursor-pointer select-none" @click="toggleSelectAll">
                {{ isAllSelected ? '取消全選' : selectedAnimals.length > 0 ? '全選本頁' : '全選' }}
              </label>
            </div>
          </div>
        </div>

        <!-- 批次操作指引 -->
        <div 
          v-if="animals.length > 0 && selectedAnimals.length === 0" 
          class="mb-6 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4"
        >
          <div class="flex items-start gap-3">
            <div class="flex-shrink-0 mt-0.5">
              <svg class="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
              </svg>
            </div>
            <div>
              <h3 class="text-sm font-medium text-blue-800 mb-1">批次提交指引</h3>
              <div class="text-sm text-blue-700 space-y-1">
                <p>💡 <strong>快速選擇：</strong>點擊動物卡片的空白區域來選取動物</p>
                <p>☑️ <strong>勾選框：</strong>直接勾選左上角的選擇框</p>
                <p>📋 <strong>全選功能：</strong>使用上方的全選框一次選取所有動物</p>
                <p>⚡ <strong>提交審核：</strong>選取動物後，點擊「提交審核」送交管理員審核</p>
                <p class="text-xs text-blue-600">💡 提示：按鈕區域不會觸發選擇，只會執行對應功能</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 動物卡片網格 -->
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-8">
          <div
            v-for="animal in animals"
            :key="animal.animal_id"
            class="bg-white rounded-lg shadow-md overflow-hidden transition-all duration-200 cursor-pointer group relative"
            :class="{ 
              'ring-2 ring-blue-500 shadow-lg transform scale-[1.02]': selectedAnimals.includes(animal.animal_id),
              'hover:shadow-lg hover:scale-[1.01]': !selectedAnimals.includes(animal.animal_id)
            }"
            @click="toggleAnimal(animal.animal_id)"
          >
            <!-- 點擊提示覆蓋層 -->
            <div 
              v-if="!selectedAnimals.includes(animal.animal_id)"
              class="absolute inset-0 bg-blue-500 bg-opacity-0 group-hover:bg-opacity-5 transition-all duration-200 z-0 pointer-events-none"
            ></div>
            
            <!-- 選擇框和選中標示 -->
            <div class="absolute top-3 left-3 z-10 flex items-center gap-2">
              <div class="relative">
                <input
                  type="checkbox"
                  :checked="selectedAnimals.includes(animal.animal_id)"
                  @click.stop=""
                  @change="toggleAnimal(animal.animal_id)"
                  class="rounded border-gray-300 text-blue-600 focus:ring-blue-500 bg-white shadow-sm cursor-pointer w-5 h-5"
                />
                <!-- 選中時的額外視覺標示 -->
                <div 
                  v-if="selectedAnimals.includes(animal.animal_id)"
                  class="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full flex items-center justify-center"
                >
                  <svg class="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
              <!-- 選中提示文字 -->
              <div 
                v-if="selectedAnimals.includes(animal.animal_id)"
                class="bg-blue-500 text-white text-xs px-2 py-1 rounded-full font-medium shadow-sm"
              >
                已選
              </div>
            </div>

            <!-- 動物圖片 -->
            <div class="relative h-48 bg-gray-200">
              <img
                v-if="getFirstImageUrl(animal) && !imageErrors[animal.animal_id]"
                :src="getFirstImageUrl(animal)"
                :alt="animal.name"
                class="w-full h-full object-cover"
                @error="imageErrors[animal.animal_id] = true"
                @load="imageErrors[animal.animal_id] = false"
              />
              <div 
                v-else
                class="flex items-center justify-center h-full text-gray-400"
              >
                <div class="text-center">
                  <span class="text-6xl block mb-2">{{ animal.species === 'CAT' ? '🐱' : '🐶' }}</span>
                  <span v-if="imageErrors[animal.animal_id]" class="text-xs">圖片載入失敗</span>
                  <span v-else class="text-xs">無圖片</span>
                </div>
              </div>
              
              <!-- 狀態標籤 -->
              <div class="absolute top-3 right-3">
                <span
                  :class="{
                    'bg-gray-100 text-gray-800': animal.status === 'DRAFT',
                    'bg-blue-100 text-blue-800': animal.status === 'SUBMITTED',
                    'bg-green-100 text-green-800': animal.status === 'PUBLISHED',
                    'bg-purple-100 text-purple-800': animal.status === 'ADOPTED',
                    'bg-red-100 text-red-800': animal.status === 'RETIRED'
                  }"
                  class="px-2 py-1 rounded text-xs font-medium"
                >
                  {{ getStatusText(animal.status) }}
                </span>
              </div>
            </div>

            <!-- 動物資訊 -->
            <div class="p-4">
              <div class="flex items-start justify-between mb-2">
                <h3 class="text-lg font-semibold text-gray-900 truncate">{{ animal.name || '未命名' }}</h3>
                <span class="text-2xl ml-2">{{ animal.species === 'CAT' ? '' : '' }}</span>
              </div>
              
              <div class="space-y-1 text-sm text-gray-600 mb-3">
                <p><span class="font-medium">品種:</span> {{ animal.breed || '未知' }}</p>
                <p><span class="font-medium">性別:</span> {{ animal.sex === 'MALE' ? ' 公' : animal.sex === 'FEMALE' ? ' 母' : '未知' }}</p>
                <p><span class="font-medium">顏色:</span> {{ animal.color || '未知' }}</p>
                <p v-if="animal.dob"><span class="font-medium">年齡:</span> {{ calculateAge(animal.dob) }}</p>
              </div>

              <div class="flex gap-2">
                <button
                  @click.stop="router.push(`/animals/${animal.animal_id}?from=shelter-animals`)"
                  class="flex-1 px-3 py-2 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition"
                >
                  查看詳情
                </button>
                <button
                  v-if="canEditAnimal(animal)"
                  @click.stop="editAnimal(animal)"
                  class="flex-1 px-3 py-2 text-xs bg-gray-600 text-white rounded hover:bg-gray-700 transition"
                >
                  編輯
                </button>
                <span 
                  v-else
                  class="flex-1 px-3 py-2 text-xs bg-gray-300 text-gray-500 rounded text-center"
                >
                  {{ getEditDisabledReason(animal) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 分頁 -->
        <div class="flex justify-center items-center space-x-2">
          <button
            @click="goToPage(pagination.page - 1)"
            :disabled="pagination.page === 1"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            上一頁
          </button>

          <span class="text-sm text-gray-600">
            第 {{ pagination.page }} / {{ pagination.pages }} 頁
          </span>

          <button
            @click="goToPage(pagination.page + 1)"
            :disabled="pagination.page >= pagination.pages"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一頁
          </button>
        </div>
      </div>

      <!-- 無結果 -->
      <div v-else class="text-center py-16">
        <div class="max-w-md mx-auto">
          <!-- 空狀態圖示 -->
          <div class="w-20 h-20 mx-auto mb-6 bg-gray-100 rounded-full flex items-center justify-center">
            <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
            </svg>
          </div>
          
          <!-- 主要訊息 -->
          <h3 class="text-xl font-semibold text-gray-800 mb-2">尚無動物資料</h3>
          <p class="text-gray-600 mb-6">目前沒有符合篩選條件的動物資料</p>
          
          <!-- 建議操作 -->
          <div class="space-y-3">
            <p class="text-sm text-gray-500">您可以：</p>
            <div class="flex flex-col sm:flex-row gap-3 justify-center">
              <button
                @click="clearFilters"
                class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition text-sm"
              >
                清除篩選條件
              </button>
              <button
                @click="router.push('/shelter/dashboard')"
                class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition text-sm"
              >
                匯入動物資料
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 編輯動物模態窗 -->
    <div v-if="editingAnimal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-screen overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold text-gray-900">編輯動物資料</h2>
            <button
              @click="closeEditModal"
              class="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>

          <div class="grid lg:grid-cols-2 gap-6">
            <!-- 左側：基本資料 -->
            <div>
              <h3 class="text-lg font-semibold text-gray-800 mb-4">基本資料</h3>
              <form @submit.prevent="saveAnimal" class="space-y-4">
                <!-- 基本資訊 -->
                <div class="grid md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">動物名稱 *</label>
                    <input
                      v-model="editForm.name"
                      type="text"
                      required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">物種 *</label>
                    <select
                      v-model="editForm.species"
                      required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="CAT">貓</option>
                      <option value="DOG">狗</option>
                    </select>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">品種</label>
                    <input
                      v-model="editForm.breed"
                      type="text"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">性別 *</label>
                    <select
                      v-model="editForm.sex"
                      required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="MALE">公</option>
                      <option value="FEMALE">母</option>
                      <option value="UNKNOWN">未知</option>
                    </select>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">顏色</label>
                    <input
                      v-model="editForm.color"
                      type="text"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">出生日期</label>
                    <input
                      v-model="editForm.dob"
                      type="date"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">描述</label>
                  <textarea
                    v-model="editForm.description"
                    rows="4"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  ></textarea>
                </div>

                <!-- 狀態 -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">狀態</label>
                  <select
                    v-model="editForm.status"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="DRAFT">草稿</option>
                    <option value="SUBMITTED">已提交</option>
                    <option value="PUBLISHED">已發布</option>
                    <option value="ADOPTED">已領養</option>
                    <option value="RETIRED">已下架</option>
                  </select>
                </div>

                <!-- 按鈕 -->
                <div class="flex gap-3 pt-4">
                  <button
                    type="button"
                    @click="closeEditModal"
                    class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition"
                  >
                    取消
                  </button>
                  <button
                    type="submit"
                    :disabled="saving"
                    class="flex-1 inline-flex items-center justify-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition shadow-sm"
                  >
                    <svg v-if="!saving" class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <svg v-else class="w-4 h-4 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    {{ saving ? '儲存中...' : '儲存' }}
                  </button>
                </div>
              </form>
            </div>

            <!-- 右側：照片和醫療記錄 -->
            <div>
              <!-- 照片管理 -->
              <div class="mb-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">照片管理</h3>
                
                <!-- 現有照片 -->
                <div v-if="hasImages(editingAnimal)" class="grid grid-cols-2 gap-2 mb-4">
                  <div
                    v-for="(image, index) in getAnimalImages(editingAnimal)"
                    :key="getImageId(image, index)"
                    class="relative group"
                  >
                    <img
                      :src="getImageUrl(image)"
                      :alt="`照片 ${index + 1}`"
                      class="w-full h-24 object-cover rounded border"
                      @error="onImageError"
                    />
                    <button
                      @click="removeImage(index)"
                      class="absolute top-1 right-1 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition"
                    >
                      ×
                    </button>
                    <div class="absolute bottom-1 left-1 bg-black bg-opacity-50 text-white text-xs px-1 rounded">
                      順序 {{ getImageOrder(image, index) }}
                    </div>
                  </div>
                </div>
                
                <!-- 上傳新照片 (美化按鈕) -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">上傳新照片</label>
                  
                  <!-- 隱藏的原生檔案輸入 -->
                  <input
                    ref="imageInput"
                    type="file"
                    multiple
                    accept="image/*"
                    @change="handleImageUpload"
                    :disabled="uploading"
                    class="hidden"
                  />

                  <!-- 美化的上傳按鈕 -->
                  <button
                    type="button"
                    @click="!uploading && imageInput && imageInput.click()"
                    :disabled="uploading"
                    class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <svg v-if="!uploading" class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <svg v-else class="w-4 h-4 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    {{ uploading ? '正在上傳...' : '選擇照片' }}
                  </button>

                  <p v-if="uploading" class="text-xs text-blue-600 mt-2">📤 正在上傳圖片...</p>
                  <p v-else class="text-xs text-gray-500 mt-2">支援 JPG、PNG 格式，最多5張</p>
                </div>
              </div>

              <!-- 醫療記錄 -->
              <div>
                <h3 class="text-lg font-semibold text-gray-800 mb-4">醫療記錄</h3>
                
                <!-- 現有醫療記錄 -->
                <div v-if="medicalRecords.length > 0" class="space-y-2 mb-4 max-h-32 overflow-y-auto">
                  <div
                    v-for="(record, index) in medicalRecords"
                    :key="`medical-${index}`"
                    class="p-2 bg-gray-50 rounded border text-sm"
                  >
                    <div class="flex justify-between items-start">
                      <div>
                        <span class="font-medium">{{ getMedicalTypeText(record.record_type) }}</span>
                        <span class="text-gray-500 ml-2">{{ formatDate(record.date) }}</span>
                      </div>
                      <button
                        @click="removeMedicalRecord(index)"
                        class="text-red-500 hover:text-red-700 text-xs"
                      >
                        刪除
                      </button>
                    </div>
                    <div v-if="record.provider" class="text-gray-600">提供者: {{ record.provider }}</div>
                    <div v-if="record.details" class="text-gray-600">{{ record.details }}</div>
                    
                    <!-- 醫療記錄附件顯示 -->
                    <div v-if="record.attachments && record.attachments.length > 0" class="mt-3 pt-3 border-t border-gray-100">
                      <div class="text-xs font-medium text-gray-500 mb-2 flex items-center">
                        <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                        </svg>
                        醫療證明 ({{ record.attachments.length }})
                      </div>
                      <div class="grid grid-cols-1 gap-2">
                        <a
                          v-for="(attachment, attIndex) in record.attachments"
                          :key="attIndex"
                          :href="attachment.url"
                          target="_blank"
                          class="flex items-center p-2 bg-blue-50 hover:bg-blue-100 rounded border border-blue-200 transition-colors"
                        >
                          <svg class="w-4 h-4 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          <span class="text-sm text-blue-700 truncate">{{ attachment.filename || attachment.name || '醫療證明文件' }}</span>
                          <svg class="w-3 h-3 text-blue-500 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 無醫療記錄時的提示 -->
                <div v-else class="text-gray-500 text-sm text-center py-4 border border-dashed border-gray-300 rounded mb-4">
                  🏥 目前沒有醫療記錄
                </div>

                <!-- 新增醫療記錄 -->
                <div class="space-y-3">
                  <div class="grid grid-cols-2 gap-2">
                    <div>
                      <label class="block text-xs text-gray-600 mb-1">類型</label>
                      <select
                        v-model="newMedicalRecord.record_type"
                        class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                      >
                        <option value="CHECKUP">健檢</option>
                        <option value="TREATMENT">治療</option>
                        <option value="VACCINE">疫苗</option>
                        <option value="SURGERY">手術</option>
                        <option value="OTHER">其他</option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-xs text-gray-600 mb-1">日期</label>
                      <input
                        v-model="newMedicalRecord.date"
                        type="date"
                        class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                  <div>
                    <label class="block text-xs text-gray-600 mb-1">提供者</label>
                    <input
                      v-model="newMedicalRecord.provider"
                      type="text"
                      placeholder="獸醫院/醫師名稱"
                      class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label class="block text-xs text-gray-600 mb-1">詳細說明</label>
                    <textarea
                      v-model="newMedicalRecord.details"
                      rows="2"
                      placeholder="醫療記錄詳細內容"
                      class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                    ></textarea>
                  </div>
                  
                  <!-- 醫療證明檔案上傳 (美化按鈕) -->
                  <div>
                    <label class="block text-xs text-gray-600 mb-1">醫療證明</label>

                    <!-- 隱藏的原生檔案輸入，保留 ref 與事件處理 -->
                    <input
                      ref="medicalFileInput"
                      type="file"
                      multiple
                      accept=".pdf,.jpg,.jpeg,.png"
                      @change="handleMedicalFileSelect"
                      class="hidden"
                    />

                    <!-- 美化按鈕與已選檔案數顯示 -->
                    <div class="flex items-center gap-3">
                      <button
                        type="button"
                        @click="medicalFileInput && medicalFileInput.click()"
                        class="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition shadow-sm"
                      >
                        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7a2 2 0 012-2h10a2 2 0 012 2v10a2 2 0 01-2 2H6a2 2 0 01-2-2V7zM8 11l3 3 5-5" />
                        </svg>
                        上傳醫療證明
                      </button>

                      <div v-if="selectedMedicalFiles.length > 0" class="text-sm text-gray-700">
                        已選 {{ selectedMedicalFiles.length }} 個檔案
                      </div>
                    </div>

                    <p class="text-xs text-gray-500 mt-2">支援 PDF、JPG、PNG 格式，最大單檔請依系統限制</p>

                    <!-- 顯示選擇的檔案（預覽列表） -->
                    <div v-if="selectedMedicalFiles.length > 0" class="mt-3 space-y-2">
                      <div
                        v-for="(file, index) in selectedMedicalFiles"
                        :key="index"
                        class="flex justify-between items-center p-2 bg-blue-50 border border-blue-200 rounded-md"
                      >
                        <div class="flex items-center">
                          <svg class="w-4 h-4 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                          </svg>
                          <span class="text-sm text-blue-700 truncate">{{ file.name }}</span>
                        </div>
                        <button
                          @click="removeSelectedMedicalFile(index)"
                          class="text-red-500 hover:text-red-700 transition-colors p-1"
                          title="移除檔案"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
                  <button
                    @click="addMedicalRecord"
                    type="button"
                    class="w-full px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 transition"
                  >
                    ➕ 新增醫療記錄
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getShelterAnimals, batchUpdateAnimalStatus, getAnimalMedicalRecords, type ShelterAnimalsFilters } from '@/api/shelters'
import type { Animal } from '@/api/animals'
import { useUpload } from '@/composables/useUpload'

const router = useRouter()
const authStore = useAuthStore()

const animals = ref<Animal[]>([])
const isLoading = ref(false)
const error = ref('')
const batchUpdating = ref(false)
const selectedAnimals = ref<number[]>([])
const showBatchMenu = ref(false)

// 編輯相關
const editingAnimal = ref<Animal | null>(null)
const saving = ref(false)
const uploading = ref(false)
const imageErrors = ref<Record<number, boolean>>({})
const medicalRecords = ref<Array<{
  medical_record_id?: number
  record_type: string
  date: string
  provider: string
  details: string
  attachments?: Array<{
    url: string
    filename?: string
    name?: string
    storage_key?: string
    mime_type?: string
  }>
}>>([])

const newMedicalRecord = reactive({
  record_type: 'CHECKUP',
  date: '',
  provider: '',
  details: ''
})

// 醫療證明檔案上傳相關
const selectedMedicalFiles = ref<File[]>([])
const medicalFileInput = ref<HTMLInputElement | null>(null)

const editForm = reactive({
  name: '',
  species: 'CAT' as 'CAT' | 'DOG',
  breed: '',
  sex: 'UNKNOWN' as 'MALE' | 'FEMALE' | 'UNKNOWN',
  color: '',
  dob: '',
  description: '',
  status: 'DRAFT' as 'DRAFT' | 'SUBMITTED' | 'PUBLISHED' | 'ADOPTED' | 'RETIRED'
})

const filters = reactive<ShelterAnimalsFilters>({
  status: undefined,
  species: undefined,
  page: 1,
  per_page: 12
})

const pagination = reactive({
  page: 1,
  per_page: 12,
  total: 0,
  pages: 1,
  has_prev: false,
  has_next: false
})

// 計算屬性
const isAllSelected = computed(() => {
  return animals.value.length > 0 && selectedAnimals.value.length === animals.value.length
})

// 批次操作權限計算
const selectedAnimalStatuses = computed(() => {
  return selectedAnimals.value.map(id => {
    const animal = animals.value.find(a => a.animal_id === id)
    return animal?.status || 'UNKNOWN'
  })
})

const canBatchSubmit = computed(() => {
  if (selectedAnimals.value.length === 0) return false
  return selectedAnimalStatuses.value.every(status => status === 'DRAFT')
})

const canBatchPublish = computed(() => {
  if (selectedAnimals.value.length === 0) return false
  return selectedAnimalStatuses.value.every(status => status === 'SUBMITTED')
})

const canBatchRetire = computed(() => {
  if (selectedAnimals.value.length === 0) return false
  return selectedAnimalStatuses.value.every(status => status === 'PUBLISHED')
})

const canBatchDelete = computed(() => {
  if (selectedAnimals.value.length === 0) return false
  return selectedAnimalStatuses.value.every(status => status === 'DRAFT')
})

onMounted(() => {
  loadAnimals()
  // 添加點擊外部關閉選單的事件監聽
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// 點擊外部關閉批次選單
function handleClickOutside(event: Event) {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    showBatchMenu.value = false
  }
}

// 清除篩選條件
function clearFilters() {
  Object.assign(filters, {
    species: '',
    status: '',
    name: '',
    chip_id: '',
    medical_status: ''
  })
  loadAnimals()
}

// 根據動物ID獲取動物名稱
function getAnimalName(animalId: number): string {
  const animal = animals.value.find(a => a.animal_id === animalId)
  return animal?.name || `動物 #${animalId}`
}

// 載入動物列表
async function loadAnimals() {
  if (!authStore.user?.primary_shelter_id) {
    error.value = '您不是收容所會員'
    return
  }

  isLoading.value = true
  error.value = ''

  // 強制測試模式檢查 (在開發者工具 console 輸入 window.FORCE_TEST_MODE = true)
  if ((window as any).FORCE_TEST_MODE) {
    animals.value = createTestAnimals()
    pagination.total = animals.value.length
    pagination.pages = 1
    pagination.page = 1
    isLoading.value = false
    return
  }

  try {
    const response = await getShelterAnimals(authStore.user.primary_shelter_id, filters)
    
    animals.value = response.animals
    
    pagination.page = response.page
    pagination.per_page = response.per_page
    pagination.total = response.total
    pagination.pages = response.pages
    pagination.has_prev = response.has_prev
    pagination.has_next = response.has_next
    
    // 清除已選擇的動物（如果不在當前頁）
    const currentAnimalIds = animals.value.map(a => a.animal_id)
    selectedAnimals.value = selectedAnimals.value.filter(id => currentAnimalIds.includes(id))
    
  } catch (err: any) {
    console.error('❌ Load animals API error:', err)
    
    // 如果 API 失敗，創建測試數據
    animals.value = createTestAnimals()
    pagination.total = animals.value.length
    pagination.pages = 1
    pagination.page = 1
    
    error.value = err.response?.data?.message || '載入失敗（使用測試數據）'
  } finally {
    isLoading.value = false
  }
}

// 重置篩選
function resetFilters() {
  filters.status = undefined
  filters.species = undefined
  filters.page = 1
  loadAnimals()
}

// 切換頁面
function goToPage(page: number) {
  if (page < 1 || page > pagination.pages) return
  filters.page = page
  loadAnimals()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 動物選擇
function toggleAnimal(animalId: number) {
  const index = selectedAnimals.value.indexOf(animalId)
  if (index > -1) {
    selectedAnimals.value.splice(index, 1)
  } else {
    selectedAnimals.value.push(animalId)
  }
}

function toggleSelectAll() {
  if (isAllSelected.value) {
    selectedAnimals.value = []
  } else {
    selectedAnimals.value = animals.value.map(a => a.animal_id)
  }
}

function clearSelection() {
  selectedAnimals.value = []
}

// 批次刪除動物（僅草稿狀態）
async function batchDeleteAnimals() {
  if (selectedAnimals.value.length === 0) {
    alert('請先選擇要刪除的動物')
    return
  }

  if (!authStore.user?.primary_shelter_id) {
    error.value = '您不是收容所會員'
    return
  }

  // 檢查是否所有選中的動物都是草稿狀態
  const nonDraftAnimals = selectedAnimals.value.filter(id => {
    const animal = animals.value.find(a => a.animal_id === id)
    return animal?.status !== 'DRAFT'
  })

  if (nonDraftAnimals.length > 0) {
    alert('只能刪除草稿狀態的動物！\n\n請取消選擇非草稿狀態的動物後再試。')
    return
  }

  const selectedAnimalNames = selectedAnimals.value.map(id => getAnimalName(id)).join('、')
  
  if (!confirm(`⚠️ 警告：此操作將永久刪除以下動物資料，無法恢復！\n\n${selectedAnimalNames}\n\n總共 ${selectedAnimals.value.length} 隻動物\n\n確定要繼續嗎？`)) {
    return
  }

  // 二次確認
  if (!confirm(`🚨 最後確認\n\n您即將永久刪除 ${selectedAnimals.value.length} 隻動物的所有資料，包括：\n• 基本資料\n• 照片\n• 醫療記錄\n• 相關申請\n\n此操作無法復原，請再次確認是否繼續？`)) {
    return
  }

  showBatchMenu.value = false
  batchUpdating.value = true

  try {
    let successCount = 0
    let failedCount = 0
    const errors: string[] = []
    
    for (const animalId of selectedAnimals.value) {
      try {
        const { deleteAnimal } = await import('@/api/animals')
        await deleteAnimal(animalId)
        successCount++
        
        // 從本地列表移除
        const animalIndex = animals.value.findIndex(a => a.animal_id === animalId)
        if (animalIndex > -1) {
          animals.value.splice(animalIndex, 1)
        }
        
      } catch (err: any) {
        failedCount++
        const errorMsg = err.response?.data?.message || err.message || '未知錯誤'
        errors.push(`${getAnimalName(animalId)}: ${errorMsg}`)
        console.error(`❌ 刪除動物 ${animalId} 失敗:`, err)
      }
    }

    // 顯示結果
    let message = `批次刪除完成！\n✅ 成功: ${successCount} 隻\n❌ 失敗: ${failedCount} 隻`
    if (errors.length > 0) {
      message += `\n\n錯誤詳情:\n${errors.slice(0, 3).join('\n')}`
      if (errors.length > 3) {
        message += `\n... 還有 ${errors.length - 3} 個錯誤`
      }
    }
    alert(message)

    selectedAnimals.value = []
    
    // 重新載入數據以更新統計
    await loadAnimals()

  } catch (err: any) {
    console.error('❌ 批次刪除錯誤:', err)
    error.value = '批次刪除失敗: ' + err.message
  } finally {
    batchUpdating.value = false
  }
}

// 批次狀態更新
async function batchUpdateStatus(action: 'draft' | 'submit' | 'publish' | 'retire') {
  if (selectedAnimals.value.length === 0) {
    alert('請先選擇要操作的動物')
    return
  }

  if (!authStore.user?.primary_shelter_id) {
    error.value = '您不是收容所會員'
    return
  }

  const actionNames = {
    draft: '變更為草稿',
    submit: '提交審核', 
    publish: '發布',
    retire: '下架'
  }

  if (!confirm(`確定要將 ${selectedAnimals.value.length} 隻動物${actionNames[action]}嗎？`)) {
    return
  }

  showBatchMenu.value = false
  batchUpdating.value = true

  try {
    const response = await batchUpdateAnimalStatus(authStore.user.primary_shelter_id, {
      animal_ids: selectedAnimals.value,
      action
    })

    alert(`批次${actionNames[action]}完成！\n成功: ${response.success_count} 隻\n失敗: ${response.failed_count} 隻`)

    // 清除選擇並重新載入
    selectedAnimals.value = []
    await loadAnimals()

  } catch (err: any) {
    console.error('Batch update error:', err)
    error.value = err.response?.data?.message || `批次${actionNames[action]}失敗`
  } finally {
    batchUpdating.value = false
  }
}

// 批次標記為已領養
async function batchMarkAdopted() {
  if (selectedAnimals.value.length === 0) {
    alert('請先選擇要操作的動物')
    return
  }

  if (!authStore.user?.primary_shelter_id) {
    error.value = '您不是收容所會員'
    return
  }

  if (!confirm(`確定要將 ${selectedAnimals.value.length} 隻動物標記為已領養嗎？\n\n注意：此操作會將動物狀態變更為已領養，無法透過一般流程恢復。`)) {
    return
  }

  showBatchMenu.value = false
  batchUpdating.value = true

  try {
    // 使用真實的批次更新 API，但我們需要逐一更新每隻動物的狀態為 ADOPTED
    // 因為 batchUpdateAnimalStatus 不支援 'adopted' action，我們需要使用個別更新
    let successCount = 0
    let failedCount = 0
    const errors: string[] = []
    
    for (const animalId of selectedAnimals.value) {
      try {
        const { updateAnimal } = await import('@/api/animals')
        await updateAnimal(animalId, { status: 'ADOPTED' })
        successCount++
        
        // 更新本地狀態
        const animal = animals.value.find(a => a.animal_id === animalId)
        if (animal) {
          animal.status = 'ADOPTED'
        }
        
      } catch (err: any) {
        failedCount++
        const errorMsg = err.response?.data?.message || err.message || '未知錯誤'
        errors.push(`動物 ID ${animalId}: ${errorMsg}`)
        console.error(`❌ 標記動物 ${animalId} 為已領養失敗:`, err)
      }
    }

    // 顯示結果
    if (successCount > 0 || failedCount > 0) {
      let message = `批次標記已領養完成！\n成功: ${successCount} 隻\n失敗: ${failedCount} 隻`
      if (errors.length > 0) {
        message += `\n\n錯誤詳情:\n${errors.slice(0, 3).join('\n')}`
        if (errors.length > 3) {
          message += `\n... 還有 ${errors.length - 3} 個錯誤`
        }
      }
      alert(message)
    }
    
    selectedAnimals.value = []

  } catch (err: any) {
    console.error('❌ Batch mark adopted error:', err)
    error.value = '批次標記已領養失敗'
  } finally {
    batchUpdating.value = false
  }
}

// 工具函數
function getStatusText(status: string): string {
  const statusMap: Record<string, string> = {
    'DRAFT': '📝 草稿',
    'SUBMITTED': '📋 已提交',
    'PUBLISHED': '✅ 已發布',
    'ADOPTED': '🏠 已領養',
    'RETIRED': '❌ 已下架'
  }
  return statusMap[status] || status
}

function calculateAge(dob: string): string {
  const birthDate = new Date(dob)
  const now = new Date()
  const months = Math.floor((now.getTime() - birthDate.getTime()) / (1000 * 60 * 60 * 24 * 30.44))
  
  if (months < 12) {
    return `${months} 個月`
  } else {
    const years = Math.floor(months / 12)
    const remainingMonths = months % 12
    return remainingMonths > 0 ? `${years} 歲 ${remainingMonths} 個月` : `${years} 歲`
  }
}

// 照片相關輔助函數
function getFirstImageUrl(animal: Animal): string | null {
  // 確保 images 是陣列且不為空
  if (!animal.images || !Array.isArray(animal.images) || animal.images.length === 0) {
    return null
  }
  
  const firstImage = animal.images[0]
  
  // 處理字串格式的圖片 URL
  if (typeof firstImage === 'string') {
    const url = validateAndFixImageUrl(firstImage)
    return url
  }
  
  // 處理物件格式的圖片數據
  if (firstImage && typeof firstImage === 'object') {
    const possibleUrls = [
      firstImage.url,
      firstImage.image_url, 
      firstImage.path,
      firstImage.storage_key
    ]
    
    for (let i = 0; i < possibleUrls.length; i++) {
      const url = possibleUrls[i]
      if (url && typeof url === 'string') {
        const fixedUrl = validateAndFixImageUrl(url)
        return fixedUrl
      }
    }
  }
  
  return null
}

function validateAndFixImageUrl(url: string): string | null {
  if (!url) {
    return null
  }
  
  // 如果是完整的 HTTP URL，直接返回
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  
  // 如果是相對路徑，轉換為完整 URL
  if (url.startsWith('/')) {
    const fixedUrl = `http://localhost:5000${url}`
    return fixedUrl
  }
  
  // 如果是 MinIO storage key，轉換為完整 URL
  if (url.includes('animals/') || url.includes('images/')) {
    const fixedUrl = `http://localhost:9000/pet-adoption/${url}`
    return fixedUrl
  }
  
  // 如果包含檔案副檔名，假設是儲存路徑
  if (url.match(/\.(jpg|jpeg|png|gif|webp)$/i)) {
    const fixedUrl = `http://localhost:9000/pet-adoption/${url}`
    return fixedUrl
  }
  
  // 其他情況，嘗試作為相對路徑處理
  const fixedUrl = `http://localhost:5000/${url}`
  return fixedUrl
}

function hasImages(animal: Animal | null): boolean {
  if (!animal) return false
  // 確保 images 存在且是陣列且有內容
  return animal.images && Array.isArray(animal.images) && animal.images.length > 0
}

function getAnimalImages(animal: Animal | null): any[] {
  if (!animal || !animal.images || !Array.isArray(animal.images)) return []
  return animal.images
}

function getImageUrl(image: any): string {
  if (typeof image === 'string') {
    return validateAndFixImageUrl(image) || '/placeholder-animal.jpg'
  }
  
  if (image && typeof image === 'object') {
    const possibleUrls = [
      image.url,
      image.image_url,
      image.path,
      image.storage_key
    ]
    
    for (const url of possibleUrls) {
      if (url && typeof url === 'string') {
        const validatedUrl = validateAndFixImageUrl(url)
        if (validatedUrl) return validatedUrl
      }
    }
  }
  
  return '/placeholder-animal.jpg'
}

function getImageId(image: any, index: number): string | number {
  if (image && typeof image === 'object') {
    return image.animal_image_id || image.id || `temp-${index}`
  }
  return `image-${index}`
}

function getImageOrder(image: any, index: number): number {
  if (image && typeof image === 'object' && image.order) {
    return image.order
  }
  return index + 1
}

function onImageError(event: Event) {
  const img = event.target as HTMLImageElement
  const originalSrc = img.src
  
  // 嘗試不同的備用 URL
  if (img.src.includes('localhost:9000')) {
    // 如果 MinIO URL 失敗，嘗試後端 URL
    const newSrc = originalSrc.replace('localhost:9000/pet-adoption/', 'localhost:5000/api/images/')
    img.src = newSrc
  } else if (img.src.includes('localhost:5000')) {
    // 如果後端 URL 也失敗，使用佔位圖
    img.src = '/placeholder-animal.jpg'
  } else {
    // 最後的備用方案 - Base64 SVG
    img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPuaaguWcluacrOmHt+eJhzwvdGV4dD48L3N2Zz4='
  }
}

// 編輯權限檢查
function canEditAnimal(animal: Animal): boolean {
  // 只有草稿狀態的動物可以編輯
  return animal.status === 'DRAFT'
}

function getEditDisabledReason(animal: Animal): string {
  switch (animal.status) {
    case 'SUBMITTED':
      return '審核中'
    case 'PUBLISHED':
      return '已發布'
    case 'ADOPTED':
      return '已領養'
    case 'RETIRED':
      return '已下架'
    default:
      return '無法編輯'
  }
}

// 測試數據生成（用於除錯照片顯示問題）
function createTestAnimals(): Animal[] {
  return [
    {
      animal_id: 1,
      name: '測試貓咪1 (相對路徑)',
      species: 'CAT',
      breed: '橘貓',
      sex: 'MALE',
      color: '橘色',
      dob: '2023-01-15',
      status: 'DRAFT',
      created_by: 1,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      images: [
        {
          animal_image_id: 1,
          storage_key: 'animals/cat1.jpg',
          url: '/api/animals/1/images/1',
          mime_type: 'image/jpeg',
          order: 1
        }
      ]
    },
    {
      animal_id: 2,
      name: '測試狗狗1 (MinIO路徑)',
      species: 'DOG',
      breed: '柴犬',
      sex: 'FEMALE',
      color: '黃色',
      dob: '2022-08-20',
      status: 'SUBMITTED',
      created_by: 1,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      images: [
        {
          animal_image_id: 2,
          storage_key: 'animals/images/dog1.png',
          url: 'animals/images/dog1.png',
          mime_type: 'image/png',
          order: 1
        }
      ]
    },
    {
      animal_id: 3,
      name: '測試貓咪2 (完整URL)',
      species: 'CAT',
      breed: '三花貓',
      sex: 'FEMALE',
      color: '三花',
      status: 'PUBLISHED',
      created_by: 1,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      images: [
        {
          animal_image_id: 3,
          storage_key: 'pet-adoption/animals/cat2.webp',
          url: 'http://localhost:9000/pet-adoption/animals/cat2.webp',
          mime_type: 'image/webp',
          order: 1
        }
      ]
    },
    {
      animal_id: 4,
      name: '測試動物 (字串URL)',
      species: 'DOG',
      breed: '混種',
      sex: 'UNKNOWN',
      color: '棕色',
      status: 'DRAFT',
      created_by: 1,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      images: ['dog2.jpg']  // 測試字串格式
    },
    {
      animal_id: 5,
      name: '無照片動物',
      species: 'CAT',
      breed: '黑貓',
      sex: 'FEMALE',
      color: '黑色',
      status: 'DRAFT',
      created_by: 1,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      images: []
    }
  ]
}

// 編輯功能
async function editAnimal(animal: Animal) {
  // 檢查編輯權限
  if (!canEditAnimal(animal)) {
    alert(`無法編輯：${getEditDisabledReason(animal)}`)
    return
  }
  
  try {
    // 重新載入動物的最新數據（包括圖片）
    const { getAnimal } = await import('@/api/animals')
    const latestAnimal = await getAnimal(animal.animal_id)
    
    editingAnimal.value = latestAnimal
    
    // 填充表單
    editForm.name = latestAnimal.name || ''
    editForm.species = latestAnimal.species || 'CAT'
    editForm.breed = latestAnimal.breed || ''
    editForm.sex = latestAnimal.sex || 'UNKNOWN'
    editForm.color = latestAnimal.color || ''
    editForm.dob = latestAnimal.dob || ''
    editForm.description = latestAnimal.description || ''
    editForm.status = latestAnimal.status || 'DRAFT'
    
  } catch (error) {
    console.error('載入動物數據失敗:', error)
    // 如果載入失敗，使用傳入的動物數據
    editingAnimal.value = animal
    editForm.name = animal.name || ''
    editForm.species = animal.species || 'CAT'
    editForm.breed = animal.breed || ''
    editForm.sex = animal.sex || 'UNKNOWN'
    editForm.color = animal.color || ''
    editForm.dob = animal.dob || ''
    editForm.description = animal.description || ''
    editForm.status = animal.status || 'DRAFT'
  }
  
  // 載入真實的醫療記錄
  try {
    const records = await getAnimalMedicalRecords(editingAnimal.value.animal_id)
    
    if (records && Array.isArray(records)) {
      medicalRecords.value = records.map(record => ({
        medical_record_id: record.medical_record_id,
        record_type: record.record_type || 'OTHER',
        date: record.date || '',
        provider: record.provider || '',
        details: record.details || '',
        attachments: record.attachments || []
      }))
    } else {
      console.warn('醫療記錄格式不正確:', records)
      medicalRecords.value = []
    }
  } catch (error) {
    console.error('載入醫療記錄失敗:', error)
    medicalRecords.value = []
    // 不顯示錯誤給用戶，因為這不是致命錯誤
  }
}

function closeEditModal() {
  editingAnimal.value = null
  medicalRecords.value = []
  // 重置表單
  Object.assign(editForm, {
    name: '',
    species: 'CAT',
    breed: '',
    sex: 'UNKNOWN',
    color: '',
    dob: '',
    description: '',
    status: 'DRAFT'
  })
  // 重置醫療記錄表單
  Object.assign(newMedicalRecord, {
    record_type: 'CHECKUP',
    date: '',
    provider: '',
    details: ''
  })
  // 重置醫療證明檔案選擇
  selectedMedicalFiles.value = []
  if (medicalFileInput.value) {
    medicalFileInput.value.value = ''
  }
}

// 醫療證明檔案處理
function handleMedicalFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files) {
    selectedMedicalFiles.value = Array.from(input.files)
  }
}

function removeSelectedMedicalFile(index: number) {
  selectedMedicalFiles.value.splice(index, 1)
  // 更新 input 的檔案列表
  if (medicalFileInput.value) {
    const dt = new DataTransfer()
    selectedMedicalFiles.value.forEach(file => dt.items.add(file))
    medicalFileInput.value.files = dt.files
  }
}

// 醫療記錄管理
function getMedicalTypeText(type: string): string {
  const typeMap: Record<string, string> = {
    'CHECKUP': '🔍 健檢',
    'TREATMENT': '💊 治療',
    'VACCINE': '💉 疫苗',
    'SURGERY': '🏥 手術',
    'OTHER': '📝 其他'
  }
  return typeMap[type] || type
}

function formatDate(dateString: string): string {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  } catch (error) {
    return dateString // 如果日期格式無效，直接返回原始字串
  }
}

async function addMedicalRecord() {
  if (!newMedicalRecord.record_type || !newMedicalRecord.date) {
    alert('請填寫類型和日期')
    return
  }
  
  if (!editingAnimal.value) {
    alert('沒有選中的動物')
    return
  }
  
  try {
    // 準備醫療記錄數據
    let medicalData: any = {
      record_type: newMedicalRecord.record_type,
      date: newMedicalRecord.date,
      provider: newMedicalRecord.provider || '',
      details: newMedicalRecord.details || ''
    }
    
    // 如果有選擇檔案，先上傳檔案
    if (selectedMedicalFiles.value.length > 0) {
      const { uploadMultiple } = useUpload()
      
      try {
        const uploadResults = await uploadMultiple(
          selectedMedicalFiles.value,
          'MEDICAL_RECORD',
          editingAnimal.value.animal_id
        )
        
        // 將上傳結果轉換為附件格式
        medicalData.attachments = uploadResults.map(result => ({
          url: result.url,
          storage_key: result.storage_key,
          filename: result.filename,
          mime_type: result.mime_type,
          size: result.size
        }))
      } catch (uploadError) {
        console.error('檔案上傳失敗:', uploadError)
        alert('檔案上傳失敗，請重試')
        return
      }
    }
    
    // 調用 API 創建醫療記錄
    const { createMedicalRecord } = await import('@/api/medicalRecords')
    const response = await createMedicalRecord(editingAnimal.value.animal_id, medicalData)
    
    // 添加到本地列表，包含從 API 返回的 ID
    medicalRecords.value.push({
      medical_record_id: response.medical_record?.medical_record_id,
      record_type: newMedicalRecord.record_type,
      date: newMedicalRecord.date,
      provider: newMedicalRecord.provider,
      details: newMedicalRecord.details,
      attachments: medicalData.attachments || []
    })
    
    // 重置表單
    Object.assign(newMedicalRecord, {
      record_type: 'CHECKUP',
      date: '',
      provider: '',
      details: ''
    })
    
    // 重置檔案選擇
    selectedMedicalFiles.value = []
    if (medicalFileInput.value) {
      medicalFileInput.value.value = ''
    }
    
    alert('✅ 醫療記錄已新增')
    
  } catch (err: any) {
    console.error('❌ Create medical record error:', err)
    const errorMessage = err.response?.data?.message || err.message || '未知錯誤'
    alert('❌ 新增醫療記錄失敗：' + errorMessage)
  }
}

async function removeMedicalRecord(index: number) {
  if (!confirm('確定要刪除這筆醫療記錄嗎？')) {
    return
  }
  
  const record = medicalRecords.value[index]
  
  // 如果是已保存的醫療記錄（有 medical_record_id），說明不支援刪除
  if (record.medical_record_id) {
    alert('⚠️ 已保存的醫療記錄無法刪除\n\n如需修改，請聯繫管理員或創建新的記錄來更正資訊。')
    return
  }
  
  // 如果是本地新增但尚未保存的記錄，可以從列表移除
  medicalRecords.value.splice(index, 1)
}

// 照片管理
async function removeImage(index: number) {
  if (!editingAnimal.value) return
  
  if (!editingAnimal.value.images || editingAnimal.value.images.length === 0) {
    console.warn('沒有照片可以刪除')
    return
  }
  
  if (index < 0 || index >= editingAnimal.value.images.length) {
    console.warn('照片索引無效')
    return
  }
  
  if (!confirm('確定要刪除這張照片嗎？')) {
    return
  }
  
  const imageToDelete = editingAnimal.value.images[index]
  
  try {
    // 調用 API 刪除圖片
    const { deleteAnimalImage } = await import('@/api/animals')
    await deleteAnimalImage(editingAnimal.value.animal_id, imageToDelete.animal_image_id)
    
    // 從本地列表移除
    editingAnimal.value.images.splice(index, 1)
    
    alert('✅ 圖片已刪除')
    
  } catch (error: any) {
    console.error(`❌ 圖片刪除失敗:`, error)
    const errorMessage = error.response?.data?.message || error.message || '未知錯誤'
    alert(`❌ 圖片刪除失敗：${errorMessage}`)
  }
}

async function handleImageUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files || !editingAnimal.value) return
  
  const files = Array.from(input.files)
  if (files.length === 0) return
  
  // 檢查數量限制
  const currentImageCount = editingAnimal.value.images?.length || 0
  if (currentImageCount + files.length > 5) {
    alert('最多只能上傳5張照片')
    return
  }
  
  uploading.value = true
  
  try {
    // 真正的照片上傳
    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      if (!file.type.startsWith('image/')) {
        console.warn(`跳過非圖片文件: ${file.name}`)
        continue
      }
      
      try {
        // 轉換為 base64 用於上傳
        const base64 = await fileToBase64(file)
        
        // 調用 API 上傳圖片
        const { addAnimalImage } = await import('@/api/animals')
        const response = await addAnimalImage(editingAnimal.value.animal_id, {
          image_url: base64,
          storage_key: `animals/${editingAnimal.value.animal_id}/${Date.now()}_${file.name}`,
          mime_type: file.type,
          description: `上傳的圖片: ${file.name}`
        })
        
        // 重新載入動物的最新數據來顯示新圖片
        try {
          const { getAnimal } = await import('@/api/animals')
          const latestAnimal = await getAnimal(editingAnimal.value.animal_id)
          editingAnimal.value = latestAnimal
        } catch (reloadError) {
          console.warn('重新載入動物數據失敗:', reloadError)
        }
        
      } catch (error: any) {
        console.error(`❌ 圖片上傳失敗 (${file.name}):`, error)
        const errorMessage = error.response?.data?.message || error.message || '未知錯誤'
        alert(`❌ 圖片上傳失敗 (${file.name})：${errorMessage}`)
      }
    }
    
    alert(`✅ 圖片上傳完成！`)
    
  } finally {
    uploading.value = false
    // 清空input
    input.value = ''
  }
}

// 輔助函數：將文件轉換為 base64
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        resolve(reader.result)
      } else {
        reject(new Error('Failed to read file as base64'))
      }
    }
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(file)
  })
}

async function saveAnimal() {
  if (!editingAnimal.value) return
  
  saving.value = true
  try {
    // 調用真正的 API 更新動物資料
    
    // 準備更新數據
    const updateData = {
      name: editForm.name,
      species: editForm.species,
      breed: editForm.breed,
      sex: editForm.sex,
      color: editForm.color,
      dob: editForm.dob,
      description: editForm.description,
      status: editForm.status
    }
    
    // 調用 updateAnimal API
    const { updateAnimal } = await import('@/api/animals')
    const response = await updateAnimal(editingAnimal.value.animal_id, updateData)
    
    // 更新本地數據
    const animalIndex = animals.value.findIndex(a => a.animal_id === editingAnimal.value!.animal_id)
    if (animalIndex > -1) {
      animals.value[animalIndex] = {
        ...animals.value[animalIndex],
        ...updateData
      }
    }
    
    alert('✅ 動物資料已更新')
    closeEditModal()
    
    // 重新載入動物列表以確保數據同步
    await loadAnimals()
    
  } catch (err: any) {
    console.error('❌ Save animal error:', err)
    const errorMessage = err.response?.data?.message || err.message || '未知錯誤'
    alert('❌ 儲存失敗：' + errorMessage)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
/* 確保選擇框在圖片上層 */
.relative {
  position: relative;
}

.absolute {
  position: absolute;
}

/* 選中狀態的視覺效果 */
.ring-2 {
  box-shadow: 0 0 0 2px rgb(59 130 246);
}
</style>

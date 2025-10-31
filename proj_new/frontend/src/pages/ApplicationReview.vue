<template>
  <div class="application-review-page">
    <div class="container">
      <!-- 頁面標題 -->
      <div class="page-header">
        <h1 class="page-title">領養申請管理</h1>
        <p class="page-description" v-if="authStore.user?.role === 'ADMIN'">查看與管理所有領養申請</p>
        <p class="page-description" v-else-if="authStore.user?.role === 'SHELTER_MEMBER'">查看與審核收容所動物的領養申請</p>
        <p class="page-description" v-else>查看與審核您送養動物的領養申請</p>
        <div v-if="route.query.animal_id" class="filter-notice">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>正在顯示特定動物的申請</span>
          <button @click="clearAnimalFilter" class="clear-filter-btn">清除篩選</button>
        </div>
      </div>

      <!-- 統計卡片 -->
      <div class="stats-grid">
        <div class="stat-card pending">
          <div class="stat-icon">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.pending }}</div>
            <div class="stat-label">待審核</div>
          </div>
        </div>

        <div class="stat-card under-review">
          <div class="stat-icon">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.underReview }}</div>
            <div class="stat-label">審核中</div>
          </div>
        </div>

        <div class="stat-card approved">
          <div class="stat-icon">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.approved }}</div>
            <div class="stat-label">已通過</div>
          </div>
        </div>

        <div class="stat-card rejected">
          <div class="stat-icon">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.rejected }}</div>
            <div class="stat-label">已拒絕</div>
          </div>
        </div>
      </div>

      <!-- 篩選標籤 -->
      <div class="filter-tabs">
        <button
          v-for="tab in filterTabs"
          :key="tab.value"
          :class="['filter-tab', { active: currentFilter === tab.value }]"
          @click="changeFilter(tab.value)"
        >
          {{ tab.label }}
          <span class="tab-count">{{ getTabCount(tab.value) }}</span>
        </button>
      </div>

      <!-- 批次操作區 -->
      <div v-if="canShowBatchOperations" class="batch-operations">
        <div class="batch-header">
          <div class="batch-info">
            <span class="selected-count">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              已選擇 {{ selectedApplications.length }} 個申請
            </span>
            <div class="batch-controls">
              <button @click="clearSelection" class="clear-btn">清除選擇</button>
              <button @click="toggleSelectAll" class="select-all-btn">
                {{ isAllSelected ? '取消全選' : '全選可審核' }}
              </button>
            </div>
          </div>
          
          <div class="batch-actions">
            <div class="relative">
              <button
                @click="showBatchMenu = !showBatchMenu"
                :disabled="batchUpdating"
                class="batch-btn"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{{ batchUpdating ? '處理中...' : '批次審核' }}</span>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <!-- 批次操作選單 -->
              <div v-if="showBatchMenu" class="batch-menu">
                <div class="menu-header">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  選擇批次操作
                </div>
                
                <div class="menu-actions">
                  <button
                    @click="batchReview('approve')"
                    :disabled="batchUpdating"
                    class="menu-item approve"
                  >
                    <span class="item-icon">✅</span>
                    <div>
                      <div class="item-title">批次通過</div>
                      <div class="item-desc">通過選中的所有申請</div>
                    </div>
                  </button>
                  
                  <button
                    @click="batchReview('reject')"
                    :disabled="batchUpdating"
                    class="menu-item reject"
                  >
                    <span class="item-icon">❌</span>
                    <div>
                      <div class="item-title">批次拒絕</div>
                      <div class="item-desc">拒絕選中的所有申請</div>
                    </div>
                  </button>
                </div>
                
                <div class="menu-footer">
                  <button @click="showBatchMenu = false" class="cancel-btn">取消</button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 已選申請預覽 -->
        <div v-if="selectedApplications.length > 0 && selectedApplications.length <= 5" class="selected-preview">
          <div class="preview-title">已選中的申請：</div>
          <div class="preview-items">
            <div
              v-for="appId in selectedApplications.slice(0, 5)"
              :key="appId"
              class="preview-item"
            >
              <span class="item-icon">📋</span>
              {{ getApplicationName(appId) }}
              <button @click="toggleApplication(appId)" class="remove-btn">×</button>
            </div>
            <div v-if="selectedApplications.length > 5" class="more-items">
              還有 {{ selectedApplications.length - 5 }} 個...
            </div>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-container">
        <div class="spinner"></div>
        <p>載入中...</p>
      </div>

      <!-- 申請列表 -->
      <div v-else-if="applications.length > 0" class="applications-list">
        <!-- 列表標題和全選控制 -->
        <div class="list-header">
          <div class="list-controls">
            <div class="select-all-control">
              <input
                type="checkbox"
                :checked="isAllSelected"
                :indeterminate="selectedApplications.length > 0 && !isAllSelected"
                @change="toggleSelectAll"
                class="select-checkbox"
              />
              <label @click="toggleSelectAll" class="select-label">
                {{ isAllSelected ? '取消全選' : selectedApplications.length > 0 ? '全選可審核' : '全選' }}
              </label>
            </div>
            <div v-if="selectedApplications.length > 0" class="selection-info">
              已選 {{ selectedApplications.length }}/{{ applications.filter(app => canReview(app)).length }}
            </div>
          </div>
        </div>

        <div
          v-for="application in applications"
          :key="application.application_id"
          class="application-card"
          :class="{ 'selected': selectedApplications.includes(application.application_id) }"
        >
          <!-- 選擇框 -->
          <div v-if="canReview(application)" class="selection-checkbox">
            <input
              type="checkbox"
              :checked="selectedApplications.includes(application.application_id)"
              @change="toggleApplication(application.application_id)"
              class="select-checkbox"
            />
          </div>

          <!-- 卡片頭部 -->
          <div class="card-header">
            <div class="applicant-info">
              <div class="applicant-avatar">
                <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                </svg>
              </div>
              <div>
                <div class="applicant-name">
                  {{ application.applicant?.username || application.applicant?.email }}
                </div>
                <div class="application-date">
                  申請時間: {{ formatDate(application.submitted_at) }}
                </div>
              </div>
            </div>
            <div :class="['status-badge', application.status.toLowerCase()]">
              {{ getStatusText(application.status) }}
            </div>
          </div>

          <!-- 動物資訊 -->
          <div class="animal-info">
            <div v-if="application.animal?.images?.[0]" class="animal-image">
              <img :src="application.animal.images[0].url" :alt="application.animal.name" />
            </div>
            <div v-else class="animal-image-placeholder">
              <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="animal-details">
              <h3 class="animal-name">{{ application.animal?.name || '未命名' }}</h3>
              
              <!-- 動物標籤 -->
              <div class="animal-badges">
                <span class="badge badge-species">
                  {{ getSpeciesText(application.animal?.species) }}
                </span>
                <span v-if="application.animal?.breed" class="badge badge-breed">
                  {{ application.animal.breed }}
                </span>
                <span v-if="application.animal?.sex" class="badge badge-sex">
                  {{ getSexText(application.animal?.sex) }}
                </span>
                <span v-if="application.animal?.color" class="badge badge-color">
                  {{ application.animal.color }}
                </span>
                <span v-if="application.animal?.age !== null && application.animal?.age !== undefined" class="badge badge-age">
                  {{ application.animal.age }} 歲
                </span>
              </div>
              
              <!-- 動物詳細資訊 -->
              <div class="animal-extra-info">
                <div v-if="application.animal?.dob" class="info-item">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span>出生: {{ formatDateOnly(application.animal.dob) }}</span>
                </div>
                <div class="info-item">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                  <span>ID: {{ application.animal_id }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 申請人資訊 -->
          <div class="applicant-details">
            <h4 class="details-title">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              申請人資訊
            </h4>
            <div class="details-grid">
              <div v-if="application.contact_phone" class="detail-item">
                <span class="detail-label">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  聯絡電話
                </span>
                <span class="detail-value">{{ application.contact_phone }}</span>
              </div>
              <div v-if="application.occupation" class="detail-item">
                <span class="detail-label">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  職業
                </span>
                <span class="detail-value">{{ application.occupation }}</span>
              </div>
              <div v-if="application.housing_type" class="detail-item">
                <span class="detail-label">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                  </svg>
                  居住環境
                </span>
                <span class="detail-value">{{ application.housing_type }}</span>
              </div>
              <div v-if="application.has_experience !== undefined" class="detail-item">
                <span class="detail-label">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  飼養經驗
                </span>
                <span class="detail-value">{{ application.has_experience ? '✓ 有經驗' : '✗ 無經驗' }}</span>
              </div>
            </div>
            <div v-if="application.contact_address" class="detail-item full-width">
              <span class="detail-label">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                聯絡地址
              </span>
              <span class="detail-value">{{ application.contact_address }}</span>
            </div>
            <div v-if="application.reason" class="detail-item full-width">
              <span class="detail-label">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                領養原因
              </span>
              <p class="detail-text">{{ application.reason }}</p>
            </div>
            <div v-if="application.notes" class="detail-item full-width">
              <span class="detail-label">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                其他備註
              </span>
              <p class="detail-text">{{ application.notes }}</p>
            </div>
          </div>

          <!-- 審核資訊 -->
          <div v-if="application.assignee" class="reviewer-info">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span>審核者: {{ application.assignee.username || application.assignee.email }}</span>
          </div>

          <div v-if="application.review_notes" class="review-notes">
            <strong>審核備註:</strong> {{ application.review_notes }}
          </div>

          <!-- 操作按鈕 -->
          <div class="card-actions">
            <button class="btn-view" @click="viewAnimalDetail(application.animal_id)">
              查看動物
            </button>
            <button
              v-if="canReview(application)"
              class="btn-approve"
              @click="openReviewModal(application, 'approve')"
            >
              通過
            </button>
            <button
              v-if="canReview(application)"
              class="btn-reject"
              @click="openReviewModal(application, 'reject')"
            >
              拒絕
            </button>
          </div>
        </div>
      </div>

      <!-- 空狀態 -->
      <div v-else class="empty-state">
        <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3>目前沒有{{ getFilterText() }}的申請</h3>
        <p v-if="authStore.user?.role === 'SHELTER_MEMBER'">
          當有人申請您收容所的動物時，將會顯示在這裡
        </p>
        <p v-else>
          當有人申請您送養的動物時，將會顯示在這裡
        </p>
      </div>

      <!-- 分頁 -->
      <div v-if="pagination.pages > 1" class="pagination">
        <button
          :disabled="pagination.page === 1"
          class="pagination-btn"
          @click="changePage(pagination.page - 1)"
        >
          上一頁
        </button>
        <span class="pagination-info">
          第 {{ pagination.page }} 頁，共 {{ pagination.pages }} 頁
        </span>
        <button
          :disabled="pagination.page === pagination.pages"
          class="pagination-btn"
          @click="changePage(pagination.page + 1)"
        >
          下一頁
        </button>
      </div>
    </div>

    <!-- 審核 Modal -->
    <Teleport to="body">
      <div v-if="showReviewModal" class="modal-overlay" @click="closeReviewModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h2 class="modal-title">
              {{ reviewAction === 'approve' ? '通過申請' : '拒絕申請' }}
            </h2>
            <button class="modal-close" @click="closeReviewModal">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <div v-if="selectedApplication" class="review-summary">
              <!-- 提示區塊 -->
              <div class="info-notice">
                <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-sm text-blue-800">
                  <template v-if="selectedApplication.animal?.owner_id === authStore.user?.user_id">
                    送養人資訊: 您就是送養人,這是別人對您動物的領養申請
                  </template>
                  <template v-else-if="selectedApplication.animal?.shelter_id && authStore.user?.role === 'SHELTER_MEMBER'">
                    收容所資訊: 您是收容所成員,這是對您收容所動物的領養申請
                  </template>
                  <template v-else>
                    審核權限: 您正在審核此領養申請
                  </template>
                </span>
              </div>

              <div class="summary-section">
                <h3 class="summary-title">申請人資訊</h3>
                <div class="summary-item">
                  <strong>姓名/帳號:</strong> {{ selectedApplication.applicant?.username || selectedApplication.applicant?.email }}
                </div>
                <div v-if="selectedApplication.contact_phone" class="summary-item">
                  <strong>聯絡電話:</strong> {{ selectedApplication.contact_phone }}
                </div>
                <div v-if="selectedApplication.contact_address" class="summary-item">
                  <strong>聯絡地址:</strong> {{ selectedApplication.contact_address }}
                </div>
                <div v-if="selectedApplication.occupation" class="summary-item">
                  <strong>職業:</strong> {{ selectedApplication.occupation }}
                </div>
                <div v-if="selectedApplication.housing_type" class="summary-item">
                  <strong>居住環境:</strong> {{ selectedApplication.housing_type }}
                </div>
                <div v-if="selectedApplication.has_experience !== undefined" class="summary-item">
                  <strong>飼養經驗:</strong> {{ selectedApplication.has_experience ? '有' : '無' }}
                </div>
                <div v-if="selectedApplication.reason" class="summary-item">
                  <strong>領養原因:</strong> 
                  <p class="summary-text">{{ selectedApplication.reason }}</p>
                </div>
                <div v-if="selectedApplication.notes" class="summary-item">
                  <strong>其他備註:</strong>
                  <p class="summary-text">{{ selectedApplication.notes }}</p>
                </div>
              </div>

              <div class="summary-section">
                <h3 class="summary-title">動物資訊</h3>
                <div class="summary-item">
                  <strong>名稱:</strong> {{ selectedApplication.animal?.name || '未命名' }}
                </div>
                <div class="summary-item">
                  <strong>物種:</strong> {{ getSpeciesText(selectedApplication.animal?.species) }}
                </div>
                <div v-if="selectedApplication.animal?.breed" class="summary-item">
                  <strong>品種:</strong> {{ selectedApplication.animal?.breed }}
                </div>
                <div v-if="selectedApplication.animal?.sex" class="summary-item">
                  <strong>性別:</strong> {{ getSexText(selectedApplication.animal?.sex) }}
                </div>
                <div v-if="selectedApplication.animal?.age" class="summary-item">
                  <strong>年齡:</strong> {{ selectedApplication.animal?.age }} 歲
                </div>
              </div>
            </div>

            <div class="form-group">
              <label>審核備註</label>
              <textarea
                v-model="reviewNotes"
                rows="4"
                :placeholder="reviewAction === 'approve' ? '請輸入通過的原因或注意事項' : '請輸入拒絕的原因'"
                class="form-textarea"
              ></textarea>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-cancel" @click="closeReviewModal">取消</button>
            <button
              :class="['btn-confirm', reviewAction === 'approve' ? 'approve' : 'reject']"
              @click="submitReview"
              :disabled="submitting"
            >
              {{ submitting ? '處理中...' : (reviewAction === 'approve' ? '確認通過' : '確認拒絕') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  getApplications,
  reviewApplication,
  type Application
} from '@/api/applications'
import { useAuthStore } from '@/stores/auth'
import { formatDistanceToNow } from 'date-fns'
import { zhTW } from 'date-fns/locale'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 狀態
const loading = ref(false)
const submitting = ref(false)
const applications = ref<Application[]>([])
const currentFilter = ref<string>('all')
const selectedApplications = ref<number[]>([])
const showBatchMenu = ref(false)
const batchUpdating = ref(false)
const pagination = ref({
  page: 1,
  per_page: 10,
  total: 0,
  pages: 0
})

// Modal 狀態
const showReviewModal = ref(false)
const selectedApplication = ref<Application | null>(null)
const reviewAction = ref<'approve' | 'reject'>('approve')
const reviewNotes = ref('')

// 篩選標籤
const filterTabs = [
  { label: '全部', value: 'all' },
  { label: '待審核', value: 'PENDING' },
  { label: '審核中', value: 'UNDER_REVIEW' },
  { label: '已通過', value: 'APPROVED' },
  { label: '已拒絕', value: 'REJECTED' }
]

// 統計數據
const stats = computed(() => {
  return {
    pending: applications.value.filter(a => a.status === 'PENDING').length,
    underReview: applications.value.filter(a => a.status === 'UNDER_REVIEW').length,
    approved: applications.value.filter(a => a.status === 'APPROVED').length,
    rejected: applications.value.filter(a => a.status === 'REJECTED').length
  }
})

// 批次選擇相關
const isAllSelected = computed(() => {
  const reviewableApps = applications.value.filter(app => canReview(app))
  return reviewableApps.length > 0 && selectedApplications.value.length === reviewableApps.length
})

const canShowBatchOperations = computed(() => {
  return selectedApplications.value.length > 0 && 
         selectedApplications.value.some(id => {
           const app = applications.value.find(a => a.application_id === id)
           return app && canReview(app)
         })
})

// 批次選擇功能
const toggleApplication = (applicationId: number) => {
  const index = selectedApplications.value.indexOf(applicationId)
  if (index > -1) {
    selectedApplications.value.splice(index, 1)
  } else {
    selectedApplications.value.push(applicationId)
  }
}

const toggleSelectAll = () => {
  const reviewableApps = applications.value.filter(app => canReview(app))
  if (isAllSelected.value) {
    selectedApplications.value = []
  } else {
    selectedApplications.value = reviewableApps.map(app => app.application_id)
  }
}

const clearSelection = () => {
  selectedApplications.value = []
}

const getApplicationName = (applicationId: number): string => {
  const app = applications.value.find(a => a.application_id === applicationId)
  if (!app) return `申請 #${applicationId}`
  
  const animalName = app.animal?.name || '未命名動物'
  const applicantName = app.applicant?.username || app.applicant?.email || '未知申請人'
  return `${animalName} - ${applicantName}`
}

// 批次審核功能
const batchReview = async (action: 'approve' | 'reject') => {
  if (selectedApplications.value.length === 0) {
    alert('請先選擇要操作的申請')
    return
  }

  const actionText = action === 'approve' ? '通過' : '拒絕'
  const confirmText = `確定要批次${actionText} ${selectedApplications.value.length} 個申請嗎？`
  
  if (!confirm(confirmText)) {
    return
  }

  showBatchMenu.value = false
  batchUpdating.value = true

  try {
    let successCount = 0
    let failedCount = 0
    const errors: string[] = []

    for (const applicationId of selectedApplications.value) {
      try {
        const application = applications.value.find(a => a.application_id === applicationId)
        if (!application) continue

        await reviewApplication(applicationId, {
          action,
          review_notes: `批次${actionText}`,
          version: application.version
        })
        
        successCount++
        
        // 更新本地狀態
        const appIndex = applications.value.findIndex(a => a.application_id === applicationId)
        if (appIndex > -1) {
          applications.value[appIndex].status = action === 'approve' ? 'APPROVED' : 'REJECTED'
          applications.value[appIndex].review_notes = `批次${actionText}`
        }
        
      } catch (error: any) {
        failedCount++
        const errorMsg = error.response?.data?.message || error.message || '未知錯誤'
        errors.push(`申請 ID ${applicationId}: ${errorMsg}`)
        console.error(`❌ 批次${actionText}申請 ${applicationId} 失敗:`, error)
      }
    }

    // 顯示結果
    let message = `批次${actionText}完成！\n成功: ${successCount} 個\n失敗: ${failedCount} 個`
    if (errors.length > 0) {
      message += `\n\n錯誤詳情:\n${errors.slice(0, 3).join('\n')}`
      if (errors.length > 3) {
        message += `\n... 還有 ${errors.length - 3} 個錯誤`
      }
    }
    alert(message)

    selectedApplications.value = []
    
    // 重新載入數據以確保同步
    await fetchApplications()

  } catch (error: any) {
    console.error(`❌ 批次${actionText}錯誤:`, error)
    alert(`批次${actionText}失敗: ${error.message}`)
  } finally {
    batchUpdating.value = false
  }
}

// 獲取申請列表
const fetchApplications = async () => {
  loading.value = true
  try {
    const filters: any = {
      mode: 'review',  // 使用審核模式，只顯示別人對自己動物的申請
      page: pagination.value.page,
      per_page: pagination.value.per_page
    }
    
    if (currentFilter.value !== 'all') {
      filters.status = currentFilter.value
    }
    
    // 支援從 URL 參數篩選特定動物的申請
    const animalId = route.query.animal_id
    if (animalId) {
      filters.animal_id = Number(animalId)
    }
    
    const response = await getApplications(filters)
    applications.value = response.items
    pagination.value = {
      page: response.page,
      per_page: response.per_page,
      total: response.total,
      pages: response.pages
    }
    
    // 清除不在當前頁的選擇
    const currentAppIds = applications.value.map(a => a.application_id)
    selectedApplications.value = selectedApplications.value.filter(id => currentAppIds.includes(id))
    
  } catch (error) {
    console.error('Failed to fetch applications:', error)
  } finally {
    loading.value = false
  }
}

// 切換篩選
const changeFilter = (filter: string) => {
  currentFilter.value = filter
  pagination.value.page = 1
  fetchApplications()
}

// 清除動物篩選
const clearAnimalFilter = () => {
  router.push('/admin/applications')
}

// 切換頁面
const changePage = (page: number) => {
  pagination.value.page = page
  fetchApplications()
}

// 獲取標籤數量
const getTabCount = (filter: string) => {
  if (filter === 'all') return pagination.value.total
  const statusMap: Record<string, keyof typeof stats.value> = {
    'PENDING': 'pending',
    'UNDER_REVIEW': 'underReview',
    'APPROVED': 'approved',
    'REJECTED': 'rejected'
  }
  return stats.value[statusMap[filter]] || 0
}

// 獲取篩選文字
const getFilterText = () => {
  const tab = filterTabs.find(t => t.value === currentFilter.value)
  return tab ? tab.label : ''
}

// 獲取狀態文字
const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    'PENDING': '待審核',
    'UNDER_REVIEW': '審核中',
    'APPROVED': '已通過',
    'REJECTED': '已拒絕',
    'WITHDRAWN': '已撤回'
  }
  return map[status] || status
}

// 格式化日期
const formatDate = (dateString?: string) => {
  if (!dateString) return '-'
  try {
    return formatDistanceToNow(new Date(dateString), {
      addSuffix: true,
      locale: zhTW
    })
  } catch {
    return dateString
  }
}

// 格式化日期(僅日期)
const formatDateOnly = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit'
  })
}

// 物種中文轉換
const getSpeciesText = (species?: string) => {
  const map: Record<string, string> = {
    'CAT': '貓',
    'DOG': '狗'
  }
  return species ? map[species] || species : '-'
}

// 性別中文轉換
const getSexText = (sex?: string) => {
  const map: Record<string, string> = {
    'MALE': '公',
    'FEMALE': '母',
    'UNKNOWN': '未知'
  }
  return sex ? map[sex] || sex : '-'
}

// 權限檢查 - 送養人或收容所成員可以審核
const canReview = (application: Application) => {
  // 檢查申請狀態
  if (application.status !== 'PENDING' && application.status !== 'UNDER_REVIEW') {
    return false
  }
  
  // 檢查是否為動物的送養人(擁有者)或收容所成員
  if (!application.animal || !authStore.user) {
    return false
  }
  
  // 1. 個人送養動物：只有動物擁有者可以審核申請
  if (application.animal.owner_id && application.animal.owner_id === authStore.user.user_id) {
    return true
  }
  
  // 2. 收容所動物：該收容所成員可以審核申請
  if (application.animal.shelter_id && 
      authStore.user.role === 'SHELTER_MEMBER' && 
      authStore.user.primary_shelter_id === application.animal.shelter_id) {
    return true
  }
  
  return false
}

// 查看申請詳情
const viewAnimalDetail = (animalId: number) => {
  router.push(`/animals/${animalId}`)
}

// 打開審核 Modal
const openReviewModal = (application: Application, action: 'approve' | 'reject') => {
  selectedApplication.value = application
  reviewAction.value = action
  reviewNotes.value = ''
  showReviewModal.value = true
}

// 關閉審核 Modal
const closeReviewModal = () => {
  showReviewModal.value = false
  selectedApplication.value = null
  reviewNotes.value = ''
}

// 提交審核
const submitReview = async () => {
  if (!selectedApplication.value) return
  
  submitting.value = true
  try {
    await reviewApplication(selectedApplication.value.application_id, {
      action: reviewAction.value,
      review_notes: reviewNotes.value,
      version: selectedApplication.value.version
    })
    
    alert(`申請${reviewAction.value === 'approve' ? '通過' : '拒絕'}成功！`)
    closeReviewModal()
    fetchApplications()
  } catch (error: any) {
    if (error.response?.status === 409) {
      alert('申請已被其他人修改，請重新載入頁面')
    } else {
      alert('操作失敗: ' + (error.response?.data?.message || error.message))
    }
  } finally {
    submitting.value = false
  }
}

// 初始化
onMounted(() => {
  fetchApplications()
  // 添加點擊外部關閉選單的事件監聽
  document.addEventListener('click', handleClickOutside)
})

// 清理事件監聽
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// 點擊外部關閉批次選單
function handleClickOutside(event: Event) {
  const target = event.target as HTMLElement
  if (!target.closest('.batch-actions')) {
    showBatchMenu.value = false
  }
}
</script>

<style scoped>
.application-review-page {
  min-height: 100vh;
  background: #f7fafc;
  padding: 2rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* 頁面標題 */
.page-header {
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.page-description {
  color: #718096;
}

.filter-notice {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background-color: #dbeafe;
  border: 1px solid #93c5fd;
  border-radius: 0.375rem;
  color: #1e40af;
  font-size: 0.875rem;
}

.clear-filter-btn {
  margin-left: auto;
  padding: 0.25rem 0.75rem;
  background-color: white;
  border: 1px solid #93c5fd;
  border-radius: 0.25rem;
  color: #1e40af;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.clear-filter-btn:hover {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

/* 統計卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  flex-shrink: 0;
  width: 3rem;
  height: 3rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-card.pending .stat-icon {
  background: #fef5e7;
  color: #f39c12;
}

.stat-card.under-review .stat-icon {
  background: #e8f4fd;
  color: #3498db;
}

.stat-card.approved .stat-icon {
  background: #e8f8f5;
  color: #27ae60;
}

.stat-card.rejected .stat-icon {
  background: #fadbd8;
  color: #e74c3c;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1a202c;
}

.stat-label {
  color: #718096;
  font-size: 0.875rem;
}

/* 篩選標籤 */
.filter-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid #e2e8f0;
  overflow-x: auto;
}

/* 批次操作區域 */
.batch-operations {
  background: #f0f9ff;
  border: 1px solid #0ea5e9;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 2rem;
}

.batch-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.batch-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.selected-count {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #0c4a6e;
}

.batch-controls {
  display: flex;
  gap: 0.5rem;
}

.clear-btn,
.select-all-btn {
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
  border: 1px solid #0ea5e9;
  background: white;
  color: #0c4a6e;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
}

.clear-btn:hover,
.select-all-btn:hover {
  background: #0ea5e9;
  color: white;
}

.batch-actions {
  position: relative;
}

.batch-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #0ea5e9;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.batch-btn:hover {
  background: #0284c7;
}

.batch-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.batch-menu {
  position: absolute;
  right: 0;
  top: 100%;
  margin-top: 0.5rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  min-width: 250px;
  z-index: 50;
  overflow: hidden;
}

.menu-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.menu-actions {
  padding: 0.5rem 0;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  border: none;
  background: none;
  cursor: pointer;
  transition: background-color 0.2s;
  text-align: left;
}

.menu-item:hover {
  background: #f1f5f9;
}

.menu-item.approve:hover {
  background: #f0fdf4;
}

.menu-item.reject:hover {
  background: #fef2f2;
}

.menu-item:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.item-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.item-title {
  font-weight: 500;
  color: #1f2937;
  font-size: 0.875rem;
}

.item-desc {
  color: #6b7280;
  font-size: 0.75rem;
}

.menu-footer {
  padding: 0.5rem 1rem;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
}

.cancel-btn {
  width: 100%;
  padding: 0.5rem;
  background: #f3f4f6;
  border: none;
  border-radius: 0.25rem;
  color: #374151;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s;
}

.cancel-btn:hover {
  background: #e5e7eb;
}

.selected-preview {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #bae6fd;
}

.preview-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #0c4a6e;
  margin-bottom: 0.5rem;
}

.preview-items {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.preview-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  background: white;
  border: 1px solid #0ea5e9;
  border-radius: 1rem;
  font-size: 0.75rem;
  color: #0c4a6e;
}

.remove-btn {
  margin-left: 0.25rem;
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  padding: 0;
}

.remove-btn:hover {
  color: #ef4444;
}

.more-items {
  padding: 0.25rem 0.75rem;
  background: #e2e8f0;
  color: #64748b;
  border-radius: 1rem;
  font-size: 0.75rem;
}

/* 列表控制 */
.list-header {
  margin-bottom: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.list-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.select-all-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.select-checkbox {
  width: 1rem;
  height: 1rem;
  border-radius: 0.25rem;
  border: 1px solid #d1d5db;
  cursor: pointer;
  accent-color: #3b82f6;
}

.select-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  user-select: none;
}

.selection-info {
  font-size: 0.875rem;
  color: #3b82f6;
  font-weight: 500;
}

/* 申請卡片選擇狀態 */
.application-card {
  position: relative;
  background: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
  border: 2px solid transparent;
}

.application-card.selected {
  border-color: #3b82f6;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  background: #fafbff;
}

.application-card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.selection-checkbox {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 10;
}

.filter-tab {
  padding: 0.75rem 1.5rem;
  border: none;
  background: none;
  color: #718096;
  font-weight: 500;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  white-space: nowrap;
  transition: all 0.2s;
}

.filter-tab:hover {
  color: #2d3748;
}

.filter-tab.active {
  color: #3182ce;
  border-bottom-color: #3182ce;
}

.tab-count {
  margin-left: 0.5rem;
  padding: 0.125rem 0.5rem;
  background: #edf2f7;
  border-radius: 1rem;
  font-size: 0.875rem;
}

.filter-tab.active .tab-count {
  background: #bee3f8;
  color: #2c5282;
}

.applications-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.applicant-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.applicant-avatar {
  width: 2.5rem;
  height: 2.5rem;
  background: #edf2f7;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #718096;
}

.applicant-name {
  font-weight: 600;
  color: #1a202c;
}

.application-date {
  font-size: 0.875rem;
  color: #718096;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-badge.pending {
  background: #fef5e7;
  color: #f39c12;
}

.status-badge.under_review {
  background: #e8f4fd;
  color: #3498db;
}

.status-badge.approved {
  background: #e8f8f5;
  color: #27ae60;
}

.status-badge.rejected {
  background: #fadbd8;
  color: #e74c3c;
}

/* 動物資訊 */
.animal-info {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.animal-image,
.animal-image-placeholder {
  width: 6rem;
  height: 6rem;
  border-radius: 0.5rem;
  overflow: hidden;
  flex-shrink: 0;
}

.animal-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.animal-image-placeholder {
  background: #edf2f7;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #cbd5e0;
}

.animal-details {
  flex: 1;
}

.animal-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.animal-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
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

.animal-extra-info {
  display: flex;
  gap: 1rem;
  font-size: 0.813rem;
  color: #718096;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.animal-meta {
  display: flex;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #718096;
}

/* 審核資訊 */
.reviewer-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #718096;
  margin-bottom: 0.5rem;
}

.review-notes {
  padding: 0.75rem;
  background: #f7fafc;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  color: #4a5568;
  margin-bottom: 1rem;
}

/* 申請人詳細資訊 */
.applicant-details {
  background: #f7fafc;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.details-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.75rem;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-label {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: #718096;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.detail-value {
  font-size: 0.875rem;
  color: #1a202c;
  font-weight: 500;
}

.detail-text {
  font-size: 0.875rem;
  color: #2d3748;
  line-height: 1.5;
  padding: 0.5rem;
  background: white;
  border-radius: 0.25rem;
  white-space: pre-wrap;
  margin-top: 0.25rem;
}

/* 操作按鈕 */
.card-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.card-actions button,
.card-actions a {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-view {
  background: #edf2f7;
  color: #2d3748;
  border: none;
}

.btn-view:hover {
  background: #e2e8f0;
}

.btn-assign {
  background: #e8f4fd;
  color: #2c5282;
  border: none;
}

.btn-assign:hover {
  background: #bee3f8;
}

.btn-approve {
  background: #27ae60;
  color: white;
  border: none;
}

.btn-approve:hover {
  background: #229954;
}

.btn-reject {
  background: #e74c3c;
  color: white;
  border: none;
}

.btn-reject:hover {
  background: #c0392b;
}

/* Loading */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 0;
}

.spinner {
  width: 3rem;
  height: 3rem;
  border: 4px solid #e2e8f0;
  border-top-color: #3182ce;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 空狀態 */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  color: #cbd5e0;
  margin: 0 auto 1rem;
}

.empty-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #718096;
}

/* 分頁 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  color: #2d3748;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background: #f7fafc;
  border-color: #cbd5e0;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  color: #718096;
  font-size: 0.875rem;
}

/* Modal */
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
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 0.5rem;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
}

.modal-close {
  background: none;
  border: none;
  color: #718096;
  cursor: pointer;
  padding: 0.25rem;
}

.modal-body {
  padding: 1.5rem;
}

.review-summary {
  margin-bottom: 1rem;
  background: #f7fafc;
  border-radius: 0.375rem;
  max-height: 400px;
  overflow-y: auto;
}

.summary-section {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.summary-section:last-child {
  border-bottom: none;
}

.summary-title {
  font-size: 1rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.75rem;
}

.summary-item {
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
}

.summary-item:last-child {
  margin-bottom: 0;
}

.summary-item strong {
  color: #4a5568;
  display: inline-block;
  min-width: 100px;
}

.summary-text {
  margin-top: 0.25rem;
  padding: 0.5rem;
  background: white;
  border-radius: 0.25rem;
  color: #2d3748;
  white-space: pre-wrap;
  line-height: 1.5;
}

.review-summary p {
  margin-bottom: 0.5rem;
}

.info-notice {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #EBF8FF;
  border: 1px solid #BEE3F8;
  border-radius: 0.375rem;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.form-textarea,
.form-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: #3182ce;
  box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.btn-cancel,
.btn-confirm {
  padding: 0.625rem 1.25rem;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: #edf2f7;
  border: none;
  color: #2d3748;
}

.btn-cancel:hover {
  background: #e2e8f0;
}

.btn-confirm {
  background: #3182ce;
  border: none;
  color: white;
}

.btn-confirm.approve {
  background: #27ae60;
}

.btn-confirm.reject {
  background: #e74c3c;
}

.btn-confirm:hover {
  opacity: 0.9;
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 響應式 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .batch-header {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
  
  .batch-info {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .batch-controls {
    justify-content: space-between;
  }
  
  .list-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .batch-menu {
    left: 0;
    right: 0;
    min-width: auto;
  }
  
  .animal-info {
    flex-direction: column;
  }
  
  .animal-image,
  .animal-image-placeholder {
    width: 100%;
    height: 12rem;
  }
  
  .card-actions {
    flex-direction: column;
  }
  
  .card-actions button,
  .card-actions a {
    width: 100%;
  }
  
  .selection-checkbox {
    top: 0.5rem;
    right: 0.5rem;
  }
  
  .application-card.selected {
    margin: 0 0.25rem;
  }
}
</style>

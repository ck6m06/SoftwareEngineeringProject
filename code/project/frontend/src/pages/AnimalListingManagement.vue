<template>
  <div class="listing-management-page">
    <div class="container">
      <!-- 頁面標題 -->
      <div class="page-header">
        <h1 class="page-title">動物刊登管理</h1>
        <p class="page-description">管理平台上所有動物的刊登狀態與審核</p>
      </div>

      <!-- 統計卡片 -->
      <div class="stats-grid">
        <div class="stat-card submitted">
          <div class="stat-icon">⏳</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.submitted }}</div>
            <div class="stat-label">待審核</div>
          </div>
        </div>

        <div class="stat-card published">
          <div class="stat-icon">✅</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.published }}</div>
            <div class="stat-label">已發布</div>
          </div>
        </div>

        <div class="stat-card draft">
          <div class="stat-icon">📝</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.draft }}</div>
            <div class="stat-label">草稿</div>
          </div>
        </div>

        <div class="stat-card retired">
          <div class="stat-icon">📦</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.retired }}</div>
            <div class="stat-label">已下架</div>
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
          {{ tab.icon }} {{ tab.label }}
          <span class="tab-count">{{ getTabCount(tab.value) }}</span>
        </button>
      </div>

      <!-- 提示訊息 -->
      <div class="info-banner">
        <div class="info-content">
          <div class="info-icon">💡</div>
          <div class="info-text">
            <strong>刊登管理說明：</strong>
            這裡是管理所有動物刊登的地方。您可以審核待審核的動物、管理已發布的內容，以及處理草稿和下架的刊登。
          </div>
        </div>
      </div>

      <!-- 空狀態 -->
      <div class="empty-state">
        <div class="empty-icon">🔧</div>
        <h3>動物刊登管理功能開發中</h3>
        <p>此功能正在開發中，敬請期待！</p>
        <p class="mt-4 text-sm">將包含以下功能：</p>
        <ul class="feature-list">
          <li>📋 查看所有動物刊登</li>
          <li>⏳ 審核待審核的刊登</li>
          <li>✅ 批次發布動物刊登</li>
          <li>📝 管理草稿狀態</li>
          <li>📦 下架不適當的刊登</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// 狀態
const currentFilter = ref<string>('all')

// 篩選標籤
const filterTabs = [
  { label: '全部', value: 'all', icon: '📋' },
  { label: '待審核', value: 'SUBMITTED', icon: '⏳' },
  { label: '已發布', value: 'PUBLISHED', icon: '✅' },
  { label: '草稿', value: 'DRAFT', icon: '📝' },
  { label: '已下架', value: 'RETIRED', icon: '📦' }
]

// 模擬統計數據
const stats = computed(() => {
  return {
    submitted: 12,
    published: 156,
    draft: 8,
    retired: 23
  }
})

// 切換篩選
const changeFilter = (filter: string) => {
  currentFilter.value = filter
  // 這裡之後會實現實際的篩選邏輯
}

// 獲取標籤數量
const getTabCount = (filter: string) => {
  const statusMap: Record<string, keyof typeof stats.value> = {
    'all': 'published', // 暫時用已發布的數量作為全部
    'SUBMITTED': 'submitted',
    'PUBLISHED': 'published',
    'DRAFT': 'draft',
    'RETIRED': 'retired'
  }
  return stats.value[statusMap[filter]] || 0
}
</script>

<style scoped>
.listing-management-page {
  min-height: 100vh;
  background: #f7fafc;
  padding: 2rem 0;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* 頁面標題 */
.page-header {
  margin-bottom: 2rem;
  text-align: center;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.page-description {
  color: #718096;
  font-size: 1.125rem;
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
  padding: 2rem;
  border-radius: 0.75rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1.5rem;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 4rem;
  height: 4rem;
  border-radius: 0.75rem;
  flex-shrink: 0;
}

.stat-card.submitted .stat-icon {
  background: #fef5e7;
}

.stat-card.published .stat-icon {
  background: #e8f8f5;
}

.stat-card.draft .stat-icon {
  background: #e8f4fd;
}

.stat-card.retired .stat-icon {
  background: #f3f4f6;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 0.25rem;
}

.stat-label {
  color: #718096;
  font-size: 1rem;
  font-weight: 500;
}

/* 篩選標籤 */
.filter-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid #e2e8f0;
  overflow-x: auto;
  justify-content: center;
}

.filter-tab {
  padding: 1rem 2rem;
  border: none;
  background: none;
  color: #718096;
  font-weight: 500;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
  white-space: nowrap;
  transition: all 0.2s;
  font-size: 1rem;
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
  padding: 0.25rem 0.75rem;
  background: #edf2f7;
  border-radius: 1rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.filter-tab.active .tab-count {
  background: #bee3f8;
  color: #2c5282;
}

/* 提示訊息 */
.info-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
  color: white;
}

.info-content {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.info-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.info-text {
  flex: 1;
  line-height: 1.6;
}

/* 空狀態 */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #718096;
  font-size: 1.125rem;
  margin-bottom: 0.5rem;
}

.feature-list {
  display: inline-block;
  text-align: left;
  margin-top: 1rem;
}

.feature-list li {
  color: #4a5568;
  padding: 0.5rem 0;
  font-size: 1rem;
}

/* 響應式 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-tabs {
    justify-content: flex-start;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .stat-card {
    padding: 1.5rem;
  }
  
  .stat-value {
    font-size: 2rem;
  }
  
  .info-content {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
}
</style>
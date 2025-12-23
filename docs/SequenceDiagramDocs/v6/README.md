# SequenceDiagrams v6 - 個人送養與申請審核流程

本目錄包含兩個主要使用案例的詳細循序圖，專注於描述各 User 與各 Vue 檔案、Python 檔案之間的互動關係。

## 檔案列表

### 1. sequence-personal-rehome.puml
**使用案例1: 個人送養發佈 (BP-REHOME-002)**

描述一般會員如何建立個人送養資料的完整流程。

#### 涉及的前端組件
- `RehomeForm.vue` - 送養表單主頁面
- `FileUploader.vue` - 檔案上傳元件
- `animals.ts` - 動物 API 服務
- `medicalRecords.ts` - 醫療記錄 API 服務
- `uploads API` - 檔案上傳 API 服務

#### 涉及的後端組件
- `animals.py` - 動物 Blueprint (路由層)
- `animal_service.py` - 動物業務邏輯服務
- `Animal Model` - 動物資料模型
- `notification_service.py` - 通知服務
- PostgreSQL 資料庫
- MinIO/S3 物件儲存

#### 主要流程步驟
1. **進入表單頁面** - 檢查登入狀態、載入草稿
2. **填寫基本資訊** - 必填欄位驗證、草稿自動儲存
3. **上傳動物圖片** - 至少1張，格式與大小驗證
4. **新增醫療記錄** - 選填，支援文件上傳
5. **確認並提交** - 驗證完整性
6. **建立動物記錄** - 後端判斷歸屬（個人/收容所）
7. **上傳圖片** - 使用預簽章 URL，批次上傳
8. **建立醫療記錄** - 包含附件上傳
9. **提交審核** - 狀態由 DRAFT → SUBMITTED
10. **完成** - 清除草稿，顯示成功訊息

#### 商業邏輯重點
- **動物歸屬判斷**: 
  - 一般會員 → owner_id (個人送養)
  - 收容所會員 → shelter_id (收容所動物)
- **互斥條件**: owner_id 與 shelter_id 不能同時存在
- **狀態流轉**: DRAFT → SUBMITTED → (待管理員審核) → PUBLISHED
- **草稿機制**: 使用 localStorage 自動儲存，防止資料遺失
- **檔案上傳**: 先建立記錄，再上傳檔案，失敗時提示稍後補傳

#### 後置條件
- 動物記錄已建立 (status = SUBMITTED)
- 圖片已上傳並關聯
- 醫療記錄已建立 (如有)
- 草稿已清除
- 等待管理員審核

---

### 2. sequence-application-review.puml
**使用案例3.2: 申請審核作業 (BP-APPLICATION-005)**

描述送養者（一般會員或收容所會員）如何審核領養申請的完整流程。

#### 涉及的前端組件
- `ApplicationReview.vue` - 申請審核頁面

#### 涉及的前端 API 服務
- `applications.ts` - 申請 API 服務

#### 涉及的後端組件
- `applications.py` - 申請 Blueprint (路由層)
- `application_service.py` - 申請業務邏輯服務
- `permission_service.py` - 權限驗證服務
- `notification_service.py` - 通知服務
- `audit_service.py` - 審計日誌服務
- `animal_service.py` - 動物服務
- `Application Model` - 申請資料模型
- `Animal Model` - 動物資料模型
- PostgreSQL 資料庫

#### 主要流程步驟
1. **進入審核頁面** - 載入申請列表
2. **權限過濾** - 根據角色過濾可見申請
3. **顯示申請列表** - 統計資料、申請卡片
4. **選擇並檢視申請** - 顯示詳細資訊
5. **送養者評估** - 檢視申請人背景資料
6. **選擇審核結果** - 通過或拒絕
7. **填寫審核意見** - 必填的審核備註
8. **提交審核結果** - 含樂觀鎖版本號
9. **權限驗證** - 檢查審核資格
10. **狀態與樂觀鎖驗證** - 防止並發衝突
11. **更新申請狀態** - APPROVED 或 REJECTED
12. **更新動物狀態** - 核准時設為 ADOPTED
13. **記錄審計日誌** - 完整操作記錄
14. **通知申請人** - 站內通知與 Email
15. **更新前端顯示** - 刷新統計與狀態

#### 商業邏輯重點
- **權限控制**:
  - **管理員不能審核申請**（重要限制）
  - 只有送養人（動物擁有者或收容所成員）可以審核
  - 個人送養: owner_id 匹配
  - 收容所動物: primary_shelter_id 匹配

- **查詢模式**:
  - `mode=all`: 自己提交的 + 針對自己動物的申請
  - `mode=review`: 只顯示針對自己動物的申請
  - `mode=my`: 只顯示自己提交的申請

- **樂觀鎖機制**:
  - 使用 `version` 欄位防止並發更新
  - 前端傳送 `expected_version`
  - 後端檢查版本號，不匹配則回傳 409 Conflict

- **狀態流轉**:
  - 核准: PENDING/UNDER_REVIEW → APPROVED
  - 拒絕: PENDING/UNDER_REVIEW → REJECTED
  - 核准後動物: PUBLISHED → ADOPTED

- **連動效果**:
  - 申請核准 → 動物狀態變為 ADOPTED
  - 動物變為 ADOPTED → 不再出現在公開清單
  - 審核記錄 → 審計日誌
  - 審核完成 → 申請人收到通知

#### 後置條件
- 申請狀態已更新 (APPROVED / REJECTED)
- 若核准，動物狀態變為 ADOPTED
- 審計日誌已記錄
- 申請人已收到通知
- 動物不再出現在公開清單 (如已核准)

---

## 技術架構說明

### 前端架構
- **框架**: Vue 3 + TypeScript + Vite
- **狀態管理**: Pinia (authStore)
- **路由**: Vue Router
- **API 客戶端**: Axios (在 client.ts 中配置)
- **本地儲存**: localStorage (草稿機制)

### 後端架構
- **框架**: Flask + Flask-Smorest
- **認證**: Flask-JWT-Extended
- **ORM**: SQLAlchemy
- **資料庫**: PostgreSQL
- **檔案儲存**: MinIO (S3 相容)

### 設計模式
1. **三層架構**:
   - Blueprint (路由層) - 處理 HTTP 請求
   - Service (業務邏輯層) - 處理商業邏輯
   - Model (資料存取層) - 資料庫操作

2. **關注點分離**:
   - `permission_service.py` - 專門處理權限檢查
   - `notification_service.py` - 專門處理通知
   - `audit_service.py` - 專門處理審計日誌

3. **錯誤處理**:
   - 自定義業務異常 (BusinessException)
   - 統一的錯誤回應格式

### 安全機制
- **JWT 認證**: 所有需要登入的操作都要驗證 Token
- **權限控制**: 細粒度的權限檢查
- **樂觀鎖**: 防止並發更新衝突
- **冪等性**: 申請建立支援 Idempotency-Key
- **輸入驗證**: 前後端雙重驗證
- **SQL 注入防護**: 使用 ORM 參數化查詢

### 資料一致性
- **交易管理**: 使用資料庫交易確保一致性
- **軟刪除**: deleted_at 欄位標記刪除
- **審計追蹤**: 記錄所有重要操作
- **版本控制**: version 欄位用於樂觀鎖

---

## 如何閱讀循序圖

### 圖例說明
- **actor (棒狀人形)**: 使用者
- **participant (方框)**: 系統組件 (前端頁面、API、服務、資料庫等)
- **activate/deactivate**: 組件的生命週期
- **箭頭 `->` **: 同步呼叫
- **箭頭 `-->` **: 回應
- **note**: 補充說明
- **alt/else/end**: 條件分支
- **loop**: 迴圈
- **== 區塊 ==**: 流程階段標記

### 閱讀順序
1. 從 actor (使用者) 的動作開始
2. 跟隨箭頭的方向看互動流程
3. 注意 activate/deactivate 了解組件的活躍時間
4. 閱讀 note 理解商業邏輯
5. 關注 alt/loop 等控制結構

---

## 使用 PlantUML 渲染

### 線上渲染
訪問 [PlantUML Online Editor](http://www.plantuml.com/plantuml/uml/)，貼上 .puml 檔案內容即可渲染。

### VS Code 插件
安裝 [PlantUML 插件](https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml)，可直接在編輯器中預覽。

### 本地渲染（需要 Java）
```bash
# 安裝 PlantUML
npm install -g node-plantuml

# 渲染為 PNG
puml generate sequence-personal-rehome.puml -o output.png

# 渲染為 SVG
puml generate sequence-application-review.puml -o output.svg
```

---

## 版本歷史

### v6 (2025-11-29)
- 建立個人送養發佈循序圖
- 建立申請審核作業循序圖
- 專注於 User、Vue 檔案、Python 檔案之間的互動
- 詳細標註商業邏輯與資料流
- 涵蓋完整的錯誤處理與邊界情況

---

## 相關文件
- [v5 使用案例圖](../v5/) - Use Case Diagrams
- [v4 申請審核循序圖](../v4/sequence-application-review.puml)
- [v4 個人送養循序圖](../v4/sequence-personal-rehome.puml)
- [設計模式說明](../DESIGN_PATTERNS.md)
- [開發指南](../development.md)

---

## 維護者
- 系統分析師
- 最後更新: 2025-11-29

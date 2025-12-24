# Feature Specification: 貓狗領養平台 — 規格更新

**Feature Branch**: `002-title-description-project`  
**Created**: 2025-10-09  
**Status**: Draft  
**Input**: 使用者提交之平台願景、任務、目標與功能需求（詳見提交內容）

## User Scenarios & Testing *(mandatory)*

此規格以「讓更多人以領養代替購買」為核心目標，優先支援會員瀏覽與提出領養申請、飼主發佈送養、以及管理員的審核流程。


### 角色與權限摘要

以下角色與其主要能力為平台核心授權模型，請在實作時以 RBAC 與最小權限原則為準：

- 訪客（Visitor）
    - 描述：未登入或未註冊的使用者。
    - 能力：可瀏覽平台上所有公開資訊（例如動物清單、照片、基本資料）；可使用搜尋與篩選。無法建立、修改或申請任何資料；若要進行領養或送養，需註冊為會員。

- 一般會員（General Member）
    - 描述：已註冊的個人會員，可作為領養者或個人送養者。
    - 能力：
        - 建立與編輯個人資料、偏好設定。
        - 刊登個人送養資訊（含上傳照片與描述）；送養刊登在審核前可修改，通過審核後僅可檢視或下架。
        - 提出領養申請（系統禁止對自己刊登的動物提出申請）。
        - 在平台內接收通知並查看申請進度（Notification Center，MVP）。

- 收容所會員（Shelter Member）
    - 描述：經平台審核通過的收容所帳號，由單一負責人或代理人操作（本版本不支援多成員管理）。
    - 能力：
        - 以機構身份批次刊登與管理所屬動物（CSV/JSON 匯入）。
        - 檢視並管理該收容所的領養申請、刊登狀態與報表（指派、批次狀態更新）。
        - 編輯、更新所屬收容所的動物資料與醫療紀錄（依權限與審核流程）。

- 管理員（Admin）
    - 描述：平台管理與稽核人員，具最高權限。
    - 能力：
        - 審核會員與收容所註冊申請；審核動物刊登、醫療紀錄與申請。
        - 管理領養紀錄、處理檢舉、封鎖帳號、發布公告與變更平台設定。
        - 擁有新增、編輯、刪除任何資料的權限（僅限授權管理員等級）。
        - 所有重要操作應寫入 AuditLog 以供稽核。

註：在資料模型上建議使用單一 `role` 欄位（enum，如 GENERAL_MEMBER | SHELTER_MEMBER | ADMIN）；若未來需支援收容所內多位 staff，可再引入 `shelter_memberships` 或獨立的組織/成員表以擴充權限。

### User Story 1 - 瀏覽列表並搜尋/篩選動物 (Priority: P1)

**描述**：任何訪客或已登入會員可以在「可領養動物」頁面瀏覽列表，套用篩選與排序（物種、年齡、性別、縣市、關鍵字），並使用分頁或無限滾動查看結果。

**Roles**: Visitor, General Member, Shelter Member, Admin — 所有角色皆可瀏覽公開列表；Admin、刊登者（General Member 或 Shelter Member）在登錄或經授權的情況下可查看未公開或待審核的自有刊登（以 RBAC 控制）。

**Why this priority**: 使用者尋找目標動物是平台的第一步，直接影響流量轉換與申請數量。

**Independent Test**: 未登入訪客或已登入會員在列表頁能夠使用至少 4 個不同篩選條件並得到符合條件的結果，分頁或滾動載入下一頁內容。

**Acceptance Scenarios**:

1. **Given**: 使用者進入列表頁， **When**: 選擇物種 = DOG 且 縣市 = Taipei， **Then**: 顯示所有符合條件的狗狗，且結果數量與分頁資訊正確。
2. **Given**: 使用者使用關鍵字搜尋（例如 "米克斯"）， **When**: 點選搜尋， **Then**: 顯示包含關鍵字的動物卡片，關鍵字高亮或在結果摘要中顯示。
3. **Given**: 使用者啟用排序（例如依上架時間）， **When**: 點選排序選單， **Then**: 清單以正確順序更新，且分頁正常運作。

**Edge cases**:
- 無符合條件結果時顯示友善提示與推薦（例如熱門動物）。
- 篩選參數組合過多或不合理時仍可回傳空結果但不崩潰。

---


### User Story 2 - 動物詳情檢視 (Priority: P1)

**描述**：使用者從清單進入個別動物詳情頁，頁面顯示多張圖片（圖片檢視器）、完整描述、近期醫療紀錄摘要，以及送養者（飼主或收容所）的非敏感公開資訊（例如縣市、收容所名稱、刊登者簡介）。頁面提供主要行動按鈕：「提出申請」。

**Roles**: Visitor, General Member, Shelter Member, Admin — 詳情頁的基本資訊對所有角色公開；互動行為「提出申請」僅在登入且 role = General Member 時啟用。刊登者（General Member 或 Shelter Member）對其所屬刊登看到額外控制（編輯、下架、查看該刊登的申請列表）；Admin 可查看並干預所有詳情與申請流程。


**Why this priority**: 動物詳情頁是使用者做出是否提出領養申請的關鍵接觸點，提供充分且可信的資訊（圖片、醫療摘要、刊登者信任指標）會顯著提升申請轉換率與平台信任，因此列為 P1。

**Independent Test**: 點開任一動物卡片，能看到圖片輪播（若存在 >=1 張）、基本欄位（名稱、年齡、性別、描述）、醫療紀錄摘要與「提出申請」按鈕；已登入 Member 點擊「提出申請」會顯示申請表單並能提交 Application（status: PENDING）。


**Acceptance Scenarios**:

1. **Given**: 動物存在醫療紀錄， **When**: 使用者進入詳情頁， **Then**: 顯示最近三筆醫療紀錄摘要並提供「查看全部醫療紀錄」連結（完整紀錄視權限顯示）。

2. **Given**: 動物為送養狀態 PUBLISHED， **When**: 已登入且 role = Member 的使用者點擊「提出申請」， **Then**: 顯示申請表單；提交後建立 Application（status: PENDING），並在平台通知中心產生通知給刊登者與管理員。

3. **Given**: 動物為送養狀態 PUBLISHED， **When**: 已登入且 role = Member 的使用者點擊「提出申請」後， **Then**: 申請出現於會員「我的申請」列表，且狀態為 PENDING（可在列表中查看提交時間與審核狀態）。

**Edge cases**:

- 圖片缺失時顯示預設占位圖與替代文字。
- 申請者重複提交或惡意大量申請：系統需在後端執行重複檢查與頻率限制（rate limit）。

---

### User Story 3 - 提出領養申請 (Priority: P1)

**描述**：已登入的會員能在動物詳情頁提交領養申請，填寫必要欄位（聯絡方式、申請理由、可到訪時間等），並立即在「我的申請」看到該筆申請（狀態 PENDING）。

**Roles**: General Member — 僅限角色為 General Member 的使用者可提交領養申請；刊登者（General Member 或 Shelter Member）不得對自己刊登的動物提出申請。API 與 UI 層需 enforce 此限制。

**Independent Test**: 已登入會員提交表單後系統回傳成功，並在 會員 -> 我的申請 列表看到新紀錄，狀態為 PENDING。

**Acceptance Scenarios**:

1. **Given**: 會員填寫完必填欄位， **When**: 點擊送出， **Then**: 申請建立（HTTP 201），並在平台「通知中心」產生通知給送養者與管理員。
2. **Given**: 欄位驗證失敗（缺少必填）， **When**: 點擊送出， **Then**: 表單顯示錯誤並阻止提交。

**Edge cases**:
- 使用者在提交期間網路中斷：系統應提供重試或草稿快取機制。
- 同一會員重複提交多次：系統應提示已有相似未審核申請。

---

### User Story 4 - 個人會員發佈/管理送養（Member Rehome）(Priority: P1)

**描述**：個人會員（Member，經系統驗證後）可建立單筆送養刊登，包含至少一張圖片、描述、健康與醫療摘要；在「我的刊登」頁可逐筆編輯或下架該刊登；管理員審核後刊登變為公開 PUBLISHED。

**Roles**: General Member, Admin — 個人 General Member 僅能建立/管理自己所屬的刊登；Admin 可審核或直接管理任何刊登（記錄操作者與變更）。

**Independent Test**: 個人 Member 建立送養後紀錄狀態為 SUBMITTED；管理員在後台批准後狀態變更為 PUBLISHED，且在前台可見。

**Acceptance Scenarios**:

1. **Given**: 個人 Member 完成發布且上傳圖片， **When**: 提交， **Then**: 產生 SUBMITTED 紀錄並在平台通知中心建立通知給管理員。
2. **Given**: Member 需要修改公開資訊， **When**: 在個人「我的刊登」列表選擇編輯， **Then**: 可更新文字與圖片（圖片需重新上傳或標記保留）。

**Edge cases**:

- 若送養被拒，Member 會在 Notification Center 看到拒絕理由並可重新提交。
- 若送養中已有正在審核的領養申請，Member 下架或刪除時需提示後續影響（例如通知已提交申請者）。

---

### User Story 5 - 收容所刊登與管理送養資訊（Shelter Rehome & Dashboard） (Priority: P1)

**描述**：收容所（Shelter）以機構身份由單一負責人操作，支援批次上傳、工作指派與報表匯出等功能（注意：本版本不支援收容所內的成員邀請或多帳號協作）。收容所刊登應與個人的刊登分開呈現並標記為機構來源（例如顯示收容所名稱與機構徽章）。

**Roles**: Shelter Member, Admin — Shelter Member 帳號由單一負責人操作，Admin 可查核與介入。

**Independent Test**: Shelter 帳號能夠透過 /shelters/{id}/animals/batch 上傳一個含 20 筆動物的 CSV，系統回傳 jobId（202 Accepted），背景工作完成後建立動物並更新 job 狀態與匯入統計；Shelter 操作者能在儀表板查看並處理該 shelter 的申請清單。

**Acceptance Scenarios**:

1. **Given**: Shelter 操作者上傳 CSV/JSON 到 POST /shelters/{id}/animals/batch， **When**: 上傳成功， **Then**: 系統回傳 jobId（202 Accepted），背景工作完成後建立動物並更新匯入統計。

2. **Given**: Shelter 操作者需要指派某申請給外部聯絡人或管理員， **When**: 在儀表板中標示 assignee 或發出通知， **Then**: 系統儲存指派紀錄並更新 Application.assigneeId（若為外部人員，則以該外部人員的帳號識別）。

3. **Given**: Shelter 帳號同時被多名人員共用（例如由不同人透過共同帳密或 SSO 存取）， **When**: 多人同時處理申請， **Then**: 系統應以 assignment/lock 機制避免同一申請被重複處理（建議在後端使用 optimistic locking 或 assignment workflow）。

**Edge cases**:

- 若 Shelter 尚未完成驗證或被暫停：其刊登可能設為限制可見或標記為待驗證，直至管理員核准。
- 批次匯入失敗部分紀錄：系統需提供錯誤報表與可重試的失敗清單。

---


### User Story 6 - 飼主 / 收容所 審核（收養者選擇）(Priority: P2)

**描述**：當會員對已刊登的動物提出領養申請時，負責該刊登的審核人（個人 GENERAL_MEMBER 或被授權的 Shelter / Shelter 操作者）可在管理頁檢視該動物的申請清單、查看申請者摘要與問卷內容，並對申請進行流程性標記（如 UNDER_REVIEW、ACCEPTED、REJECTED）。審核流程需支援「指派 (assign)」、「鎖定 (lock)」與「覆核 (escalation)」，以避免多人同時審核造成競爭狀態。

**Roles**: General Member, Shelter Member, Admin —

- General Member（個人飼主）: 對自己刊登的動物執行審核動作（查看申請詳情、標記 UNDER_REVIEW / ACCEPTED / REJECTED、提供審核備註）；不支援跨帳號指派多人處理。
- Shelter Member（收容所）: 以 Shelter 帳號（單一負責人）身份操作，支援指派申請給外部聯絡人或在儀表板中處理申請，並能批次更新狀態（視平台設定）。
- Admin（平台管理員）: 可介入或覆核任意申請、解除鎖定、查看完整 audit log，並在需要時強制更改狀態或停權異常帳號。

**Independent Test**: 審核人可在其管理介面將某筆申請標為 UNDER_REVIEW，該狀態立即反映於申請者的「我的申請」頁；Shelter 操作者可將申請指派給特定 staff（若適用），並在該 staff 的任務清單看到被指派的項目。

**Acceptance Scenarios**:

1. **Given**: 多筆申請存在， **When**: 審核人（GENERAL_MEMBER 或 Shelter / Shelter 操作者）選擇一筆標記為 UNDER_REVIEW， **Then**: 系統應記錄該操作者與時間，並將該筆申請狀態更新為 UNDER_REVIEW；系統應阻止其他人同時將另一筆設定為同一時段的 UNDER_REVIEW（可透過 assignment 或 business rule 實作）。

2. **Given**: Shelter 指派某申請給外部處理人或管理員， **When**: 被指派者在其任務清單處理， **Then**: Application.assigneeId = assignee.id，處理紀錄記錄 assignee 與處理時間；若 assignee 離線，指派者可重新指派。

3. **Given**: GENERAL_MEMBER 決定接受某位申請者， **When**: GENERAL_MEMBER 點選 ACCEPT 並填寫交接/面談備註， **Then**: 申請狀態變更為 APPROVED，系統於 Notification Center 建立通知給申請者與管理員並在 audit log 留存紀錄；同時其他候補申請應收到狀態更新（例如 REMAINING -> REJECTED 或 WAITLISTED，依平台政策）。

4. **Given**: 多名審核人同時嘗試操作同一申請， **When**: 其中一人先完成 ACCEPT， **Then**: 其他人的請求應回傳 409 或顯示已變更狀態，並提供差異說明（who/when）。

**API / Implementation Notes**:

- POST /applications/{id}/review {action: UNDER_REVIEW|ACCEPT|REJECT, notes?, assigneeId?, expectedVersion?} => 後端驗證 actor 對該 application/animal 的權限，採用 optimistic locking (version) 或資料庫鎖定來避免 race condition；回傳 200 + updated Application 或 409 on version conflict。
- POST /shelters/{id}/applications/{appId}/assign {assigneeId} => 只允許 Shelter 操作者或 Admin 操作，會在 application 記錄 assigneeId 與 assignedAt。
- GET /applications?ownerId=...&status=SUBMITTED|UNDER_REVIEW => 審核人與管理員用於列單的 API。
- Audit: 每次狀態變更都必須寫入 AuditLog {actorId, action, targetType: 'application', targetId, before, after, notes, timestamp, shelterId?}。

**Edge cases**:

- 飼主誤操作：提供確認對話框與短時間內撤銷 (soft undo) 機制，並可在 audit log 中標示回滾原因。
- 若申請者被停權或刪除帳號：若狀態需變更，審核人應收到警示且流程以手動介入為主（例如系統提示需聯絡管理員）。
- 若 assignee 帶離職或帳號停用：Manager 或 Admin 可重新指派或介入。

**Tests / QA checks**:

- Permission: 使用 Shelter 帳號嘗試修改非所屬 shelter 的 application -> 回傳 403。
- Concurrency: 同步發起兩次 POST /applications/{id}/review（expectedVersion 相同）-> 其中一個請求回傳 200，另一回傳 409 並附差異資訊。
- Audit: 對 5 次不同的狀態變更檢查 AuditLog 是否都包含 actorId、before/after、timestamp 與 notes（如有）。

---

### User Story 7 - 管理員後台審核與資料管理 (Priority: P1)

**描述**：管理員在後台可以全面查看並管理申請、動物、會員與收容所資料；可審核送養/領養申請（批准／拒絕／退回）、新增或編輯動物資料與醫療紀錄，並可對資源執行刪除或恢復（soft-delete）。

**Roles**: Admin — 僅限 Admin（含分級）可存取此後台操作；針對敏感操作應要求更高等級且記錄 actor 與時間。

**Independent Test**: 管理員能在後台將 SUBMITTED 的送養標為 PUBLISHED 並檢視變更日誌；能為動物新增醫療紀錄；能恢復被標為 soft-deleted 的動物。

**Acceptance Scenarios**:

1. **Given**: 一筆送養為 SUBMITTED， **When**: 管理員審核通過， **Then**: 變更為 PUBLISHED，並在 audit log 中記錄操作人與時間。
2. **Given**: 管理員刪除一筆動物， **When**: 刪除， **Then**: 標記為 soft-deleted，並能在一定期限內恢復。

**Edge cases**:
- 審核中同時有多位管理員操作：後端需使用適當鎖定或版本控制以避免 race condition。
- 對於敏感資訊的操作需有更高權限提示且紀錄審計。

---

### User Story 8 - 我的申請與資料管理（Member self-service）(Priority: P2)

**描述**：會員可在個人頁面查看與管理自己提交的領養與送養申請，編輯可編輯的草稿、查看審核歷程、下載申請表、以及接收與查看通知紀錄（平台內通知）。如需直接聯絡，使用者將透過已核准或公開的聯絡資訊進行聯繫；平台於 MVP 階段不提供即時站內聊天功能。

**Roles**: General Member, Shelter Member, Admin — General Member 可管理個人申請（編輯/撤回/下載）且僅能存取自己的申請；刊登者（General Member / Shelter Member）與 Admin 對其相關的申請可見摘要與執行審核權限（視權限）。

**Independent Test**: 會員登入後在「我的申請」看到所有歷史紀錄；可下載某筆申請的 PDF 摘要；Notification Center 顯示申請相關通知。

**Acceptance Scenarios**:

1. **Given**: 會員有多筆申請， **When**: 進入我的申請頁， **Then**: 列表按時間排序並可 filter（PENDING/APPROVED/REJECTED）。
2. **Given**: 某筆申請為 PENDING， **When**: 會員點選撤回， **Then**: 申請狀態變為 WITHDRAWN 並在 Notification Center 通知相關方。

**Edge cases**:
- 會員嘗試編輯已進入審核程序的申請：系統應阻止並提供替代操作（例如補件或聯絡送養者）。

---

### User Story 9 - 通知與通訊（Notification Center MVP, Priority: P2）

**描述**：系統在申請狀態變更、審核結果或管理員操作時建立平台內通知（Notification record），使用者可在 Notification Center 查看與管理通知。

**Roles**: All registered roles (General Member, Shelter Member, Admin) — 所有註冊使用者可在平台內查看通知；訪客不可設定偏好但在必要時可透過外部通路被聯絡（若提供）。

**Independent Test**: 當管理員在後台將申請標記為 APPROVED，申請者在 1 分鐘內於 Notification Center 收到對應通知。

**Acceptance Scenarios**:

1. **Given**: 申請狀態變更， **When**: 變更發生， **Then**: 系統在通知 queue 建立 Notification record 並顯示於受影響使用者的 Notification Center。

**Edge cases**:
- Notification queue 處理失敗或外部 provider 回傳錯誤：系統需有 retry 策略與失敗紀錄；並在 Notification Center 顯示錯誤狀態（例如「通知發送失敗，稍後重試」）。
- 通知頻率過高時應合併或節流（digest、batching）。

---

<!-- Note: In this revision in-app direct messaging (previously User Story 9) has been removed. Direct messaging will be evaluated in a future sprint. Notification delivery in MVP is via Notification Center; Email/SMS are deferred. -->
---

### User Story 10 - 動物醫療紀錄管理 (Priority: P1)

**描述**：管理員、收容所工作人員與飼主皆可為動物新增、編輯或附加醫療紀錄（recordType、date、provider、details、attachments），但所有新增或修改的紀錄初始為 unverified 狀態；系統須保留審核歷程（verified, verifiedBy, verifiedAt）與變更日誌，管理員可驗證 (verify) 或拒絕該紀錄。醫療紀錄的摘要會在動物詳情頁展示，完整紀錄僅顯示給有權限的使用者或在經過審核後公開。

**Roles**: General Member, Shelter Member, Admin — General Member 與 Shelter Member（收容所操作人）可新增/更新其所屬動物的醫療紀錄（狀態初為 unverified）；Admin 負責 verify/reject 並保留審計紀錄；公眾僅見已驗證摘要。

**Why this priority**：醫療紀錄直接影響領養者對動物健康與適配性的判斷，為配對可靠性與平台信任的關鍵要素。

**Independent Test**：

- A. 飼主新增一則醫療紀錄並上傳附件，紀錄於系統顯示為 unverified 且出現在該動物的「待驗證醫療紀錄」清單中；管理員登入後能看到待驗證項目並執行 Verify 操作，Verify 後該紀錄於動物詳情摘要顯示為已驗證，相關當事人在 Notification Center 看到審核結果通知（Email/SMS deferred）。

**Acceptance Scenarios**：

1. **Given**: 飼主為已驗證會員， **When**: 上傳某次疫苗紀錄並填寫 recordType、date、provider、details， **Then**: 系統建立 MedicalRecord (status: unverified)，並在 audit log 中記錄 actor 與 timestamp。
2. **Given**: 管理員在後台審核該紀錄， **When**: 點選 Verify， **Then**: 記錄變為 verified=true，verifiedBy=adminId，verifiedAt=時間，並在 Notification Center 建立通知給紀錄建立者（Email/SMS deferred）。
3. **Given**: 未經驗證的醫療紀錄， **When**: 一般公眾檢視動物詳情， **Then**: 只顯示醫療紀錄摘要或遮罩關鍵詳細資訊；經驗證後，則顯示更完整內容。
4. **Given**: 上傳的附件格式或大小不符， **When**: 使用者上傳， **Then**: 前端阻擋上傳並顯示錯誤（允許的格式與最大大小限制在規格中說明）。

**Edge cases**：

- 若多方（飼主與收容所）針對同一事件上傳不同版本的醫療紀錄，系統需保留來源與時間戳並允許管理員合併或選擇可信版本。
- 當醫療紀錄被標記為欺詐或不實，管理員可標示為 disputed，並將該紀錄隱藏或加入調查流程；同時保留審計記錄以供追溯。
- 若紀錄被刪除或修改，系統應採 soft-delete 與版本控制（保留歷史版本以遵守審計要求）。

Mapping to FRs：此 user story 直接對應 **FR-008**（醫療紀錄的新增、檢視、更新與審核）與 **FR-007/FR-010**（審核歷程與個資保護）。

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Authentication & Accounts (認證與帳號) — 系統 MUST 允許使用者註冊、登入與登出，並支援基本會員資料編輯。會員註冊後預設為角色 `GENERAL_MEMBER`（除非為經管理員審核之 `SHELTER_MEMBER` 或 `ADMIN`）。生日於首次註冊可選填，之後可補填。

- **FR-002**: Browse Animals (瀏覽動物) — 系統 MUST 允許任何使用者（包含 `Visitor`）瀏覽「可領養動物」清單，並支援基本篩選（物種、年齡範圍、性別、縣市）與分頁顯示。對於 `ADMIN` 與刊登者（`GENERAL_MEMBER` 或 `SHELTER_MEMBER`）可在授權下檢視非公開或待審核的自有刊登。

- **FR-003**: Animal Details (動物詳情) — 系統 MUST 在動物詳情頁顯示：名稱、物種、年齡、性別、描述、圖片集（支援多張）、收容所或刊登者資訊及醫療紀錄摘要（若有）。對部分資料僅在經驗證或具權限時顯示完整內容。

- **FR-004**: Submit Application (提出領養申請) — 系統 MUST 允許 `GENERAL_MEMBER` 提交領養申請；系統 MUST 阻止刊登者（不論其為 `GENERAL_MEMBER` 或 `SHELTER_MEMBER`）對自己刊登的動物提出申請（回傳 403）。所有申請會建立為 status = PENDING 並出現在申請者「我的申請」中。

- **FR-005**: Publish Rehome (發佈送養) — 系統 MUST 允許 `GENERAL_MEMBER` 與 `SHELTER_MEMBER` 發佈送養/刊登。`GENERAL_MEMBER` 的個人刊登由其個人帳號管理；`SHELTER_MEMBER` 的刊登以機構身份 (shelterId) 建立（本版本不支援 shelter 多成員管理）。發佈後狀態為 SUBMITTED，需由 `ADMIN` 審核或自動政策審查通過後變更為 PUBLISHED。

- **FR-006**: GENERAL_MEMBER / Shelter Review & Assignment (飼主 / 收容所 審核與指派) — 系統 MUST 允許刊登者（`GENERAL_MEMBER` 或 `SHELTER_MEMBER`）在其管理介面檢視申請並執行審核動作（UNDER_REVIEW / ACCEPT / REJECT），並支援指派 (assign)/鎖定 (lock) 機制以避免競爭處理。`ADMIN` 可介入或覆核任一申請。

- **FR-007**: Audit Trail (稽核歷程) — 對於每筆領養/審核相關操作，系統必須記錄完整的審核歷程（actorId、action、before、after、notes、timestamp）；AuditLog 不可被一般使用者刪除，且可供 `ADMIN` 查詢。

- **FR-008**: Medical Records (醫療紀錄) — 系統 MUST 支援動物之醫療紀錄的新增、檢視與更新（recordType、date、provider、details、attachments）。`GENERAL_MEMBER` 與 `SHELTER_MEMBER` 可為其所屬動物新增記錄（初始為 unverified），`ADMIN` 負責 verify/reject 並寫入審計紀錄；驗證後紀錄在詳情頁可見完整內容。

- **FR-009**: Notification Center (通知中心, MVP) — 系統 MUST 支援平台內通知機制（Notification record + Notification Center UI）。當申請或審核狀態變更時，系統應建立通知記錄並將其顯示於受影響使用者的 Notification Center；外部通道 (Email/SMS) 在 MVP 中為 deferred。

- **FR-010**: Data Privacy & Exports (個資保護與匯出) — 系統 MUST 對會員個資採取最低必要原則儲存，並提供受控的匯出/刪除流程（包含審核與 audit）；相關作業建議以 job-based 處理並提供查詢狀態。

*安全與隱私相關（非實作細節）*

- **FR-010 (補充)**: 系統必須對個資匯出與刪除流程進行驗證與稽核，並提供 job-based 處理與可查詢狀態。

### Key Entities (concise template)

- [Entity 1] User / Member: 使用者帳號
    - purpose: 平台使用者（申請者、刊登者、收容所負責人、管理員）
    - key attributes: id(UUID), role(enum), email(unique), displayName, phone(optional), verified(bool), createdAt, updatedAt
    - relations: hasMany(Application), hasMany(Notification), may belongTo(Shelter) via primaryShelterId

- [Entity 2] Animal: 項目紀錄
    - purpose: 表示可領養之動物
    - key attributes: id(UUID), name, species(enum), sex, ageApprox, description, status(enum), shelterId?, ownerId?, createdAt, updatedAt
    - relations: hasMany(MedicalRecord), hasMany(Attachment), hasMany(Application)

- [Entity 3] Application: 領養/送養申請
    - purpose: 申請流程紀錄
    - key attributes: id(UUID), applicantId, animalId, type(enum), status(enum), version(int), submittedAt, reviewedAt, assigneeId
    - relations: belongsTo(User), belongsTo(Animal)

- [Entity 4] MedicalRecord
    - purpose: 動物醫療紀錄與附件
    - key attributes: id(UUID), animalId, recordType, date, provider, details, attachments[], verified(bool), verifiedBy?, verifiedAt?
    - relations: belongsTo(Animal), hasMany(Attachment)

- [Entity 5] Shelter
    - purpose: 收容所/機構資料
    - key attributes: id(UUID), name, primaryShelterId, contact, address, verified(bool), createdAt, updatedAt
    - relations: hasMany(Animal), hasOne(User primaryAccount)

- [Entity 6] Notification
    - purpose: 平台內通知
    - key attributes: id(UUID), recipientId, actorId?, type, payload(json), read(bool), createdAt, deliveredAt?, externalDeliveryStatus?, lastError?
    - relations: belongsTo(User)

- [Entity 7] AuditLog
    - purpose: 追蹤重要狀態改變與審核歷程
    - key attributes: id(UUID), actorId, action, targetType, targetId, before(json)?, after(json)?, notes?, timestamp
    - relations: optional reference to User/Shelter/Animal/Application

## Success Criteria / 可衡量成功指標

以下為建議回填之科技無關、可衡量的成功指標（請根據業務目標調整數值）：

- **SC-001 (註冊流程效率)**: 使用者可在 2 分鐘內完成帳號註冊（包含 email 驗證流程的觸發），對至少 90% 的真實使用者有效。
- **SC-002 (系統可用量/負載)**: 在常態高峰期系統能同時承受 1,000 名並發活躍使用者（API 調用）且響應時間 95th percentile < 500ms（不含背景 Job 與大型匯入/匯出）。
- **SC-003 (任務成功率 / 使用者滿意度)**: 90% 的使用者在首次嘗試時成功完成其主要任務（例如：搜尋並提交申請），回饋調查滿意度平均分數 >= 4/5。
- **SC-004 (業務指標 - 支援負擔減少)**: 上線後 3 個月內，與領養申請流程相關的客服單數下降至少 50%（相較於上線前的基線或可比較期間）。
## Non-Functional Requirements / 非功能性需求

以下為建議的非功能性需求（NFR），每一項皆提供可量化的目標值與實作/監控建議：

- 性能（Performance）:
    - 目標：95th percentile API latency < 500ms（簡短查詢與 CRUD 操作，不含大型匯入/匯出或檔案處理）。
    - 負載：支援至少 1,000 並發活躍使用者，並在峰值期間保持可用性與可接受延遲。
    - 監控：使用 APM（Datadog / NewRelic / Prometheus + Grafana）監控 P50/P95/P99 latency、錯誤率與吞吐量。

- 可用性（Availability）:
    - 目標：服務可用率 >= 99.5%（月度），對於關鍵 API（認證、申請、通知查詢）建議 99.9% SLA。
    - 策略：多 AZ 部署、健康檢查、自動重啟與回退策略。

- 可伸縮性（Scalability）:
    - 目標：能在 15 分鐘內將後端實例水平擴充至少 3 倍以應對流量突發。
    - 設計：無狀態 API 層、工作者池分離（jobs/notifications）、具指標驅動的自動擴縮。

- 可觀察性（Observability）:
    - 指標：API latency、錯誤率、隊列長度（jobs/notifications）、job 成功/失敗率、AuditLog 寫入失敗率。
    - 日誌：結構化日誌（JSON）與追蹤（分散式 tracing），錯誤需包含 correlationId 以便追蹤。

- 安全（Security）:
    - 認證：使用 JWT/OAuth2，敏感操作需額外驗證或 MFA（管理員）。
    - 權限：RBAC 驗證，重要操作需記錄 AuditLog。
    - 資料保護：個資加密（at-rest 與 in-transit），最小必要原則，敏感欄位可透過 tokenization/加密處理。
    - 定期掃描：依 CI/CD 流程執行 SAST/Dependency scanning 與定期滲透測試。

- 隱私與合規（Privacy & Compliance）:
    - 個資匯出/刪除流程需審核並有可稽核記錄（job-based），保留與刪除策略依當地法規設定。

- 恢復與備援（Backup & Disaster Recovery）:
    - 目標：RPO <= 24 小時，RTO <= 4 小時（依業務等級調整）。
    - 策略：每日備份、跨區複寫、關鍵資料的快照與演練。

- 可存取性（Accessibility）:
    - 目標：主要頁面（動物清單、詳情、申請流程）滿足 WCAG 2.1 AA 基本要求。

- 運維與操作（Operational）:
    - 目標：系統警示在 5 分鐘內有人接收並開始處理（Pager duty/ops on-call）。
    - 建議：提供運維 runbooks、可重現的部署（IaC）、可觀察的控制面板。

- 國際化（I18n）與本地化（L10n）:
    - 目標：初期支援中文（繁體）與英文，文案應可由 CMS 或翻譯檔管理。

### 度量與驗證建議

- 在開發、測試與生產環境中建立負載與壓力測試（k6 / Gatling），並把結果納入發行決策。
- 監控 job queue 長度與 worker 成功率，將異常（持續錯誤或堆積）設為可觸發的警示。

- **SC-004 (業務指標 - 支援負擔減少)**: 上線後 3 個月內，與領養申請流程相關的客服單數下降至少 50%（相較於上線前的基線或可比較期間）。

### 備註（度量與監控）

- 為了衡量上述指標，建議在系統中啟用：API 請求與錯誤率監控（Prometheus / Datadog）、前端轉換漏斗追蹤（GA4 / Mixpanel）、Job 成功/失敗率儀表板、以及定期的使用者滿意度調查。


## Execution Flows for Functional Requirements（工程可執行版）

本節提供面向工程的執行流程：包含跨切面規範（cross-cutting rules）、標準回應格式與每一項 FR 的流程模板（前置條件、步驟、後置條件、錯誤處理、API 範例）。可直接作為 OpenAPI、測試案例與前後端合約的來源。

### 跨切面規範（Cross-cutting rules）

- 認證與授權：所有會改變狀態的 API 必須提供有效存取憑證（JWT 或 opaque token）。授權檢查依角色（GENERAL_MEMBER、SHELTER_MEMBER、ADMIN）與資源擁有權（animal.ownerId / animal.shelterId）執行。缺少或無效憑證回 401；權限不足回 403。
- ActingAs 與 Audit：所有狀態變更操作必須紀錄操作者 actorId 並寫入 AuditLog。Audit 可同步寫入或透過可靠隊列異步寫入；若寫入失敗，API 可回 202（Accepted）並排入重試。
- 幂等性（Idempotency）：會被重試的 create 類 endpoint（例如 POST /applications、POST /rehomes、批次匯入、資料匯出/刪除）應支援 Idempotency-Key header。相同 Idempotency-Key 在 TTL 期間內的重複請求應回傳原始結果或 409（並附已有資源位置）。
- 並發與版本控制（Concurrency & Versioning）：易發生 race 的更新（例如審核流程）須支援 optimistic locking（version 欄位或 If-Match/expectedVersion）。版本衝突回 409，並回傳目前版本與差異資訊。
- 長時間作業採 Job 模式：批次匯入、匯出與大型檔案處理應回 202 { jobId }，提供 GET /jobs/{jobId} 查詢進度與結果；Job 必須記錄 attempts、start/finish timestamp 與 resultSummary。
- 通知語意（Notification semantics）：所有需通知使用者的事件應先建立 Notification 一筆紀錄，然後 enqueue delivery task 由 worker 處理（Email/SMS 為 deferred，MVP 先以平台內通知為主）。前端 Notification Center 直接讀 Notification table。
- 重試與 backoff：背景 worker 必須實作指數退避與可配置的最大重試次數；超過次數後標示 FAILED 並將錯誤細節放入管理視窗以人工處理。
- 軟刪除與保留政策：預設採 soft-delete；個資匯出/刪除流程應紀錄申請人、審核與最終物理刪除排程以符合法規。

### 標準回應格式與錯誤碼

- 同步建立成功：201 Created { "id": "...", "resource": { ... } }
- 同步更新成功：200 OK { "resource": { ... } }
- 非同步接受：202 Accepted { "jobId": "...", "statusUrl": "/jobs/{jobId}" }
- 常用錯誤碼：400（Bad Request - 驗證錯誤）、401（Unauthorized）、403（Forbidden）、404（Not Found）、409（Conflict - 版本或重複）、422（Unprocessable Entity - 附件或 schema 約束）、413（Payload Too Large）、500（Internal Server Error）。
- 錯誤格式：{ "code": "ERROR_CODE", "message": "人類可讀訊息", "details": {...} }

### 各 FR 執行流程模板（精簡）

下列為 FR-001..FR-010 的工程化流程（保留 API 範例與錯誤處理規範）。開發時可直接轉為 OpenAPI 與測試案例。

FR-001：Authentication & Accounts（認證與帳號）
- 前置條件：註冊/登入無特殊前置，email 必須唯一
- 註冊流程：
    1) Client: POST /auth/register { email, password, username }
    2) Server: 驗證欄位（錯誤回 400）
    3) Server: 建立 user（role=GENERAL_MEMBER）、寫 AuditLog、產生驗證 token 並 enqueue 驗證信（外部傳送 deferred）
    4) 回應：201 Created { id, verificationSent: true }
- 驗證：GET /auth/verify?token=... -> mark verified、寫 AuditLog
- 登入/登出：POST /auth/login -> 200 + { accessToken, refreshToken }；POST /auth/logout -> 200 並使 refresh token 無效
- 錯誤處理：重複 email -> 409；憑證錯誤 -> 401

FR-002：Browse Animals（瀏覽動物）
- 前置條件：存在 status = PUBLISHED 的動物
- 流程：
    1) GET /animals?species=&city=&page=&size=&q=...
    2) Server: 驗證參數（限制最大 page size）、使用索引查詢、回傳分頁結果與 metadata
    3) 回應：200 { items:[], page, size, total }
- 錯誤處理：參數錯誤 -> 400；page size 過大 -> 413 或自動修正

FR-003：Animal Details（動物詳情）
- 前置條件：animalId 存在且可見性檢查通過
- 流程：
    1) GET /animals/{id}
    2) Server: 取回 animal、images（有限量）、medicalRecordSummaries（依 verified 與權限）
    3) 回應：200 { animal, images[], medicalSummaries[] }
- 錯誤處理：找不到 -> 404；存取被拒 -> 403

FR-004：Submit Application（提出領養申請）
- 前置條件：使用者已登入且 role = GENERAL_MEMBER；animal.status = PUBLISHED；申請人不得為刊登者
- 流程：
    1) Client: POST /applications (Header: Idempotency-Key 可選)
    2) Server: 若提供 Idempotency-Key，檢查是否已存在重複請求 -> 若重複回傳既有資源或 409
    3) Server: 建立 application { status:PENDING, version:1 }、寫 AuditLog、建立 Notification 紀錄、enqueue 外部傳送（deferred）
    4) 回應：201 Created { id, status: PENDING }
- 後置條件：申請出現在「我的申請」；刊登者/管理員收到通知
- 錯誤處理：欄位驗證失敗 -> 400；重複申請 -> 409；未授權 -> 401/403

FR-005：Publish Rehome（發佈送養）
- 前置條件：使用者已登入並驗證（GENERAL_MEMBER 或 SHELTER_MEMBER）
- 流程：
    1) Client: POST /rehomes（images 先上傳或以參考方式傳送）
    2) Server: 驗證 payload 與圖檔；建立 resource status=SUBMITTED、寫 AuditLog、通知管理員
    3) 回應：201 Created { id, status: SUBMITTED }
- 錯誤處理：圖檔問題 -> 422；缺少必填欄位 -> 400

FR-006：Owner / Shelter Review & Assignment（飼主 / 收容所 審核與指派）
- 前置條件：操作者為刊登者、收容所操作者或 Admin
- 流程（審核）：
    1) POST /applications/{id}/review { action, notes, expectedVersion? }
    2) Server: 檢查權限與 expectedVersion（optimistic locking）
    3) Server: 更新 application.status、版本 +1、寫 AuditLog、建立 Notifications，回傳更新後的 application
    4) 回應：200 OK { application }
- 錯誤處理：版本衝突 -> 409（回傳 currentVersion）；權限不足 -> 403

FR-007：Audit Trail（稽核歷程）
- 前置條件：所有會改變系統狀態的操作
- 流程：
    1) 在每次狀態改變時產生 AuditLog { actorId, action, targetType, targetId, before, after, notes, timestamp }
    2) 重要操作建議同步寫入；若寫入失敗可 enqueue 重試並回 202
    3) 提供查詢：GET /admin/audit?targetType=&targetId=&from=&to=&actorId=
- 後置條件：admin 可查詢且普通使用者不可刪除

FR-008：Medical Records（醫療紀錄）
- 前置條件：身份驗證且為被允許的角色（飼主/收容所/管理員）
- 流程：
    1) POST /animals/{id}/medical-records（含附件；若檔案會重試，建議使用 Idempotency-Key）
    2) Server: 建立 record status=unverified、寫 AuditLog、enqueue 通知給管理員以供驗證
    3) 管理員驗證：POST /medical-records/{id}/verify { verified:true|false, notes } -> 更新、寫 AuditLog、通知建立者
    4) 回應：建立 201，驗證 200
- 錯誤處理：附件上傳失敗 -> 422；未授權 -> 403

FR-009：Notification Center（通知中心，MVP）
- 前置條件：使用者存在且可選擇通知偏好
- 流程：
    1) 事件發生時建立 Notification 紀錄並建立外部傳送工作（若有）
    2) Client: GET /notifications?recipientId={me}&unreadOnly=true -> 回傳近期通知
    3) 標示已讀：POST /notifications/{id}/mark-read（寫入 AuditLog）
    4) 外部傳送 worker 更新 Notification.externalDeliveryStatus 與 retryCount
- 錯誤處理：傳送失敗資訊記錄於 Notification.lastError，UI 顯示狀態

FR-010：Data Privacy & Exports（個資保護與匯出）
- 前置條件：requester 為資料所有者或 admin，且通過授權驗證
- 匯出流程：
    1) POST /data/export { userId } -> Server 驗證並建立 Job(type=data:export)，回 202 { jobId }
    2) Background job：組合資料包、存入安全儲存、寫入 resultSummary 與短時效下載連結、更新 Job 狀態
    3) Client 可透過 GET /jobs/{jobId} 查詢或以 Notification 收到完成通知
- 刪除/匿名化流程：POST /data/delete { userId } -> 建立 Job(type=data:delete) 並依審核流程執行
- 錯誤處理：未授權 -> 403；長時間作業回 202 並回傳 jobId


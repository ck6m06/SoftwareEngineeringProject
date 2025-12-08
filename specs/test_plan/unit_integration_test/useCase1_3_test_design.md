# Use Case 1.3 — 動物詳情檢視：測試架構設計

檔案位置：`specs/test_plan/unit_integration_test/useCase1_3_test_design.md`

目的：為「動物詳情檢視（Use Case 1.3）」撰寫完整的三層測試架構設計，包含 Unit Tests、Controller Tests、Integration Tests，幫助後端開發/測試人員實作 pytest 測試。

前提：後端採用 NestJS + Prisma；專案已有測試配置與 PrismaService mock 可用於測試環境。

## 業務需求回顧

**使用案例1.3 動物詳情檢視**
- 填表人：系統分析師
- 商業流程編號：BP-ANIMAL-004
- 行為者：所有使用者
- 內容概述：本使用案例描述使用者如何檢視動物詳細資訊。
- 先決條件：使用者在「1.1 動物列表瀏覽」的作業中點選動物卡片。
- 後置條件：無。

**主要流程：**
1. 系統畫面初始時，載入該動物完整資料。
2. 系統顯示動物基本資料、圖片集、描述、醫療紀錄摘要。
3. 系統顯示送養者公開資訊與聯絡方式。
4. 已登入會員可看到「領養申請」按鈕。

**輔助說明：**
- 動物狀態為「其他使用者已提出領養申請」或「已領養」時，不顯示申請按鈕。
- 送養者為當前登入使用者時，顯示「編輯」動物資訊的選項。
- 醫療紀錄僅顯示已驗證的紀錄摘要。

## 測試架構分層

### Unit Tests（Service 單元測試）
- **測試範圍**：僅測試 `listings.service.ts` 中的動物詳情獲取業務邏輯
- **測試方法**：使用 Jest mock Prisma client，不依賴真實資料庫
- **檔案位置**：`backend/src/listings/listings.service.spec.ts`（新增測試案例）
- **測試重點**：
  - 動物基本資料載入邏輯
  - 圖片與附件關聯載入
  - 醫療紀錄摘要篩選（僅已驗證）
  - 擁有者資訊權限控制
  - 動物不存在處理

### Controller Tests（Route 控制器測試）
- **測試範圍**：僅測試 `/listings/{id}` route 的 HTTP 層處理
- **測試方法**：使用 Jest mock `ListingsService.findOne`，不依賴真實資料庫或 service 層
- **檔案位置**：`backend/src/listings/listings.controller.spec.ts`（新增測試案例）
- **測試重點**：
  - HTTP 狀態碼與回傳結構
  - 路徑參數驗證（UUID 格式）
  - JWT token 處理（可選驗證）
  - 404 錯誤處理
  - 權限差異回傳（訪客vs會員）

### Integration Tests（整合測試）
- **測試範圍**：測試完整的動物詳情檢視流程（route → service → Prisma → database）
- **測試方法**：建立真實測試資料，驗證端到端行為
- **檔案位置**：`backend/test/listings-detail.e2e-spec.ts`
- **測試重點**：
  - 完整資料載入與組裝
  - 不同使用者角色的資料可見性
  - 申請按鈕顯示邏輯
  - 醫療紀錄驗證狀態篩選
  - 效能與響應時間

## Unit Tests（Service 單元測試）詳細設計

### 測試目標
- **測試對象**：`ListingsService.findOne(id: string, currentUserId?: string)`
- **Mock 策略**：Mock Prisma client 及其查詢方法
- **業務邏輯重點**：資料組裝、權限控制、醫療紀錄篩選

### 核心測試案例

#### TC-U1.3-01: 基本動物資料載入測試
- **測試目的**：驗證動物基本資料正確載入
- **Use Case 對應**：主要流程步驟 1&2 - 載入完整資料
- **測試條件**：合法動物ID，無當前用戶
- **Mock 設定**：`prisma.animalListing.findUnique()` 回傳完整動物資料
- **驗證點**：
  - 返回動物基本資料（name, species, breed, age, description等）
  - 包含圖片陣列（photos JSON parse）
  - 包含位置資訊（location）

#### TC-U1.3-02: 擁有者資訊載入測試
- **測試目的**：驗證送養者公開資訊正確載入
- **Use Case 對應**：主要流程步驟 3 - 送養者資訊
- **測試條件**：動物資料包含擁有者關聯
- **Mock 設定**：include owner 資料結構
- **驗證點**：
  - 回傳擁有者公開資訊（name, email）
  - 隱藏敏感資訊（不包含password等）

#### TC-U1.3-03: 醫療紀錄摘要篩選測試
- **測試目的**：驗證只回傳已驗證的醫療紀錄摘要
- **Use Case 對應**：輔助說明 3 - 僅顯示已驗證紀錄
- **測試條件**：動物有多筆醫療紀錄，部分已驗證
- **Mock 設定**：醫療紀錄資料包含 verified 欄位
- **驗證點**：
  - 只回傳 verified=true 的醫療紀錄
  - 醫療紀錄格式正確（簡要摘要，非完整詳情）

#### TC-U1.3-04: 動物不存在處理測試
- **測試目的**：驗證無效動物ID的錯誤處理
- **測試條件**：不存在的動物ID
- **Mock 設定**：`findUnique` 回傳 null
- **驗證點**：拋出 `NotFoundException`

#### TC-U1.3-05: 會員vs訪客資料差異測試
- **測試目的**：驗證不同用戶角色看到的資料差異
- **Use Case 對應**：主要流程步驟 4 - 已登入會員差異
- **測試條件**：同一動物，分別以訪客和會員身份查詢
- **Mock 設定**：根據 currentUserId 調整回傳資料
- **驗證點**：
  - 會員能看到更詳細的聯絡資訊
  - 訪客看到的資料有適當隱藏

#### TC-U1.3-06: 擁有者查看自己動物測試
- **測試目的**：驗證動物擁有者查看自己動物的特殊權限
- **Use Case 對應**：輔助說明 2 - 送養者看到編輯選項
- **測試條件**：currentUserId 等於動物 ownerId
- **Mock 設定**：擁有者身份驗證
- **驗證點**：
  - 回傳包含編輯權限標示
  - 可看到所有資料（包含私人資訊）

#### TC-U1.3-07: 申請狀態判斷邏輯測試
- **測試目的**：驗證申請按鈕顯示邏輯
- **Use Case 對應**：輔助說明 1 - 申請按鈕顯示條件
- **測試條件**：動物處於不同狀態（AVAILABLE/PENDING/ADOPTED）
- **Mock 設定**：不同 status 的動物資料
- **驗證點**：
  - AVAILABLE狀態：可申請
  - PENDING/ADOPTED狀態：不可申請
  - 回傳正確的 canApply 標示

#### TC-U1.3-08: 圖片資料解析測試
- **測試目的**：驗證圖片JSON資料正確解析
- **Use Case 對應**：主要流程步驟 2 - 圖片集顯示
- **測試條件**：動物包含圖片JSON字串
- **Mock 設定**：photos欄位為JSON字串格式
- **驗證點**：
  - JSON正確解析為陣列
  - 圖片URL格式驗證
  - 空圖片情況處理

## Controller Tests（控制器測試）詳細設計

### 測試目標
- **測試對象**：`GET /listings/{id}` route handler
- **Mock 策略**：Mock `ListingsService.findOne()` method
- **HTTP 層重點**：狀態碼、JSON結構、參數驗證、錯誤處理

### 核心測試案例

#### TC-C1.3-01: 正常動物詳情回應測試
- **測試目的**：驗證正常情況下的HTTP回應
- **測試條件**：合法動物ID，service回傳正常資料
- **Mock 設定**：`listingsService.findOne` 回傳完整動物資料
- **驗證點**：
  - status_code = 200
  - 回傳JSON結構正確
  - Content-Type 為 application/json

#### TC-C1.3-02: 無效ID格式處理測試
- **測試目的**：驗證無效UUID格式的參數驗證
- **測試條件**：非UUID格式的ID參數
- **Mock 設定**：不調用service（參數驗證階段阻止）
- **驗證點**：
  - status_code = 400
  - 錯誤訊息指出無效ID格式

#### TC-C1.3-03: 動物不存在404處理測試
- **測試目的**：驗證動物不存在時的錯誤回應
- **測試條件**：合法ID但動物不存在
- **Mock 設定**：service拋出 NotFoundException
- **驗證點**：
  - status_code = 404
  - 錯誤訊息明確

#### TC-C1.3-04: JWT token處理測試
- **測試目的**：驗證可選JWT token的正確處理
- **測試條件**：包含/不包含 Authorization header
- **Mock 設定**：捕獲傳遞給service的currentUserId
- **驗證點**：
  - 有token：currentUserId正確傳遞
  - 無token：currentUserId為undefined

#### TC-C1.3-05: 服務層異常處理測試
- **測試目的**：驗證service層拋出異常的處理
- **測試條件**：service拋出非預期錯誤
- **Mock 設定**：service拋出RuntimeError
- **驗證點**：
  - status_code = 500
  - 錯誤回應結構正確

## Integration Tests（整合測試）詳細設計

### 測試目標
- **測試範圍**：完整的動物詳情檢視流程
- **資料庫**：測試資料庫（或in-memory）
- **資料準備**：建立真實關聯測試資料
- **端到端驗證**：業務邏輯正確性

### 核心測試案例

#### TC-I1.3-01: 完整動物資料載入測試
- **Use Case 對應**：主要流程完整驗證
- **測試條件**：建立完整的動物資料（包含圖片、醫療紀錄、擁有者）
- **驗證點**：
  - 動物基本資料完整載入
  - 圖片資料正確解析
  - 擁有者資訊正確顯示
  - 醫療紀錄摘要正確篩選

#### TC-I1.3-02: 訪客vs會員權限差異測試
- **Use Case 對應**：主要流程步驟 4 - 會員權限差異
- **測試條件**：同一動物，分別以訪客和已登入會員身份請求
- **驗證點**：
  - 訪客看到基本資料和公開聯絡資訊
  - 會員看到申請按鈕和更多詳情
  - 資料結構差異正確

#### TC-I1.3-03: 擁有者查看自己動物測試
- **Use Case 對應**：輔助說明 2 - 擁有者編輯權限
- **測試條件**：動物擁有者查看自己的動物
- **驗證點**：
  - 顯示編輯權限標示
  - 可看到所有私人資訊
  - 不顯示申請按鈕（自己不能申請自己的動物）

#### TC-I1.3-04: 申請按鈕顯示邏輯測試
- **Use Case 對應**：輔助說明 1 - 申請按鈕條件
- **測試條件**：建立不同狀態的動物
- **驗證點**：
  - AVAILABLE狀態：已登入會員看到申請按鈕
  - PENDING狀態：不顯示申請按鈕
  - ADOPTED狀態：不顯示申請按鈕
  - 訪客：不顯示申請按鈕

#### TC-I1.3-05: 醫療紀錄驗證狀態篩選測試
- **Use Case 對應**：輔助說明 3 - 僅顯示已驗證紀錄
- **測試條件**：建立動物包含已驗證和未驗證醫療紀錄
- **驗證點**：
  - 只回傳 verified=true 的紀錄
  - 紀錄內容為摘要格式
  - 敏感醫療資訊被適當隱藏

#### TC-I1.3-06: 複雜關聯資料載入測試
- **測試條件**：建立包含多種關聯資料的動物
- **驗證點**：
  - 所有關聯資料正確載入
  - 查詢效率合理（避免N+1問題）
  - 資料一致性保持

#### TC-I1.3-07: 大型圖片集處理測試
- **測試條件**：動物包含大量圖片
- **驗證點**：
  - 圖片資料正確載入
  - 響應時間在合理範圍
  - JSON解析無錯誤

#### TC-I1.3-08: 動物不存在處理測試
- **測試條件**：請求不存在的動物ID
- **驗證點**：
  - 回傳404錯誤
  - 錯誤訊息用戶友好
  - 不洩露系統內部資訊

## 測試資料準備策略

### 動物詳情測試資料工廠

```typescript
// 測試資料工廠範例
export const createTestAnimalWithDetails = async (prisma: PrismaService, options = {}) => {
  const defaultOptions = {
    withOwner: true,
    withMedicalRecords: true,
    withPhotos: true,
    status: 'AVAILABLE',
    verified: true,
    ...options
  };

  // 建立擁有者
  const owner = defaultOptions.withOwner ? await prisma.user.create({
    data: {
      name: '送養者小明',
      email: 'owner@test.com',
      role: 'OWNER'
    }
  }) : null;

  // 建立動物
  const animal = await prisma.animalListing.create({
    data: {
      species: 'dog',
      breed: '黃金獵犬',
      ageEstimate: 3,
      gender: 'male',
      description: '溫馴友善的狗狗，適合家庭飼養',
      location: '台北市中山區',
      healthStatus: '健康良好，已完成基礎疫苗',
      photos: defaultOptions.withPhotos ? JSON.stringify([
        'https://example.com/photo1.jpg',
        'https://example.com/photo2.jpg'
      ]) : null,
      status: defaultOptions.status,
      ownerId: owner?.id,
    },
    include: {
      owner: true,
      medicalRecords: true
    }
  });

  // 建立醫療紀錄
  if (defaultOptions.withMedicalRecords) {
    await prisma.medicalRecord.createMany({
      data: [
        {
          animalId: animal.id,
          recordType: 'VACCINE',
          date: new Date('2024-01-15'),
          provider: '台北動物醫院',
          details: '完成三合一疫苗接種',
          verified: defaultOptions.verified,
        },
        {
          animalId: animal.id,
          recordType: 'CHECKUP',
          date: new Date('2024-02-01'),
          provider: '中山獸醫診所',
          details: '健康檢查正常',
          verified: false, // 未驗證紀錄
        }
      ]
    });
  }

  return animal;
};
```

## Mock 策略詳細指南

### Unit Tests Mock 範例

```typescript
describe('ListingsService - findOne', () => {
  let service: ListingsService;
  let prisma: DeepMockProxy<PrismaService>;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        ListingsService,
        {
          provide: PrismaService,
          useValue: mockDeep<PrismaService>(),
        },
      ],
    }).compile();

    service = module.get(ListingsService);
    prisma = module.get(PrismaService);
  });

  it('should return animal details with owner info', async () => {
    // Mock data
    const mockAnimal = {
      id: 'uuid-123',
      species: 'dog',
      breed: '黃金獵犬',
      photos: JSON.stringify(['photo1.jpg', 'photo2.jpg']),
      owner: {
        id: 'owner-uuid',
        name: '送養者小明',
        email: 'owner@test.com'
      },
      medicalRecords: [
        {
          recordType: 'VACCINE',
          details: '疫苗接種',
          verified: true
        },
        {
          recordType: 'CHECKUP', 
          details: '未驗證紀錄',
          verified: false
        }
      ]
    };

    prisma.animalListing.findUnique.mockResolvedValue(mockAnimal);

    const result = await service.findOne('uuid-123');

    expect(result).toBeDefined();
    expect(result.owner.name).toBe('送養者小明');
    expect(result.medicalRecords).toHaveLength(1); // 只有已驗證紀錄
    expect(result.photos).toHaveLength(2);
  });
});
```

## 測試執行與覆蓋率

### 執行指令

```bash
# 執行所有 Use Case 1.3 相關測試
npm test -- --testNamePattern="useCase1_3|animal.*detail"

# 只執行 Unit Tests (Service 層)
npm test -- src/listings/listings.service.spec.ts

# 只執行 Controller Tests  
npm test -- src/listings/listings.controller.spec.ts

# 只執行 Integration Tests
npm test -- test/listings-detail.e2e-spec.ts

# 執行並顯示覆蓋率
npm test -- --coverage --testNamePattern="useCase1_3"
```

### 覆蓋率目標

- **Service 層動物詳情邏輯**: > 95%
- **Controller 層HTTP處理**: > 90% 
- **整合測試場景覆蓋**: > 85%

## 測試優先順序

### P0（核心功能）
- 完整動物資料載入 (TC-I1.3-01)
- 基本動物資料載入 (TC-U1.3-01) 
- 正常HTTP回應 (TC-C1.3-01)
- 動物不存在處理 (TC-U1.3-04, TC-C1.3-03)

### P1（重要功能）  
- 訪客vs會員權限差異 (TC-I1.3-02)
- 申請按鈕顯示邏輯 (TC-I1.3-04)
- 醫療紀錄驗證篩選 (TC-I1.3-05)
- JWT token處理 (TC-C1.3-04)

### P2（穩定性）
- 擁有者特殊權限 (TC-I1.3-03)
- 大型圖片集處理 (TC-I1.3-07)
- 無效ID格式處理 (TC-C1.3-02)
- 複雜關聯載入 (TC-I1.3-06)

## 效能測試考量

對於動物詳情檢視，建議加入效能測試：

```typescript
describe('Animal Detail Performance', () => {
  it('should load animal details within acceptable time', async () => {
    const startTime = Date.now();
    
    const response = await request(app.getHttpServer())
      .get('/listings/uuid-123')
      .expect(200);
    
    const endTime = Date.now();
    const responseTime = endTime - startTime;
    
    expect(responseTime).toBeLessThan(500); // 500ms內完成
    expect(response.body).toHaveProperty('id');
  });
});
```
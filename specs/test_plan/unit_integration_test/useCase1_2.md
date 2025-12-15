使用案例1.2 動物搜尋篩選
■ 填表人：系統分析師
■ 商業流程編號：BP-ANIMAL-003
■ 行為者：所有使用者
■ 內容概述：本使用案例描述使用者如何搜尋與篩選動物資料。
■ 先決條件：使用者在「1.1 動物列表瀏覽」頁面中。
■ 後置條件：當搜尋條件無符合結果，顯示「無符合條件的動物」訊息。
■ 主要流程：
畫面初始時，所有篩選條件為預設值。
使用者選擇篩選條件，包括物種、年齡、性別、縣市等。
使用者輸入關鍵字進行搜尋。
使用者按下「搜尋」按鈕。
系統依輸入條件的交集，將動物資料以清單方式呈現於螢幕畫面上。
系統顯示符合條件的動物數量。
■ 輔助說明：
關鍵字搜尋範圍包含動物名稱、品種、描述資訊。
多條件搜尋時，系統以AND邏輯處理。
搜尋結果最多顯示100筆，建議使用者縮小搜尋範圍。



整理一下縮減版的 function
def list_animals(filters: dict, current_user_id: int = None) -> dict:
    """
    獲取動物列表 
    """
    # 階段 1: 參數初始化與基礎查詢
    
    # 取得篩選參數，並設定分頁預設值 (1, 20)
    species = filters.get('species')
    sex = filters.get('sex')
    status = filters.get('status')
    # ... (其他參數獲取) ...
    page = filters.get('page', 1)
    per_page = min(filters.get('per_page', 20), 100)
    
    # 建立基礎查詢: 預設過濾掉已刪除的動物
    query = Animal.query.filter_by(deleted_at=None)
    

    # 階段 2: 權限與公開性處理 (Owner/Status 邏輯)
    if owner_id:
        if current_user_id == owner_id:
            # A. 查詢自己的動物：處理收容所成員的特殊權限 (個人 OR 收容所動物)
        elif current_user_id is None:
            # B. 未認證用戶：只能看已發布 (PUBLISHED)
        else:
            # C. 查詢其他用戶：只能看已發布 (PUBLISHED)
    else:
        # 無 owner_id 篩選時，預設只顯示已發布的動物
        
    # 階段 3: 核心篩選與 Enum 轉換
    # 狀態篩選: 將字串狀態轉換為 AnimalStatus Enum
    if status:
        # ... 轉換並套用 query = query.filter_by(status=status_enum)
        
    # 物種篩選: 將字串物種轉換為 Species Enum
    if species:
        # ... 轉換並套用 query = query.filter_by(species=species_enum)
        
    # 性別篩選: 將字串性別轉換為 Sex Enum
    if sex:
        # ... 轉換並套用 query = query.filter_by(sex=sex_enum)
        
    # 收容所篩選
    # 來源類型篩選 (shelter 或 personal)
    # 地區篩選    
    # 年齡篩選      
    # 關鍵字搜尋 (Keyword Search)
        
    # 階段 5: 排序、分頁與回傳   
    # 執行查詢，以創建時間降序排列並進行分頁
    pagination = query.order_by(Animal.created_at.desc()).paginate(
    )
    
    # 將結果轉換為字典並回傳分頁資訊
    return {
    }
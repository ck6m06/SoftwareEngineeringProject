#!/usr/bin/env python3
"""
測試批次上傳和狀態管理功能
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_batch_status_management():
    """測試批次狀態管理功能"""
    
    print("=== 批次狀態管理測試 ===")
    
    # 1. 先取得收容所動物列表
    print("\n1. 查詢收容所草稿動物...")
    response = requests.get(f"{BASE_URL}/animals?shelter_id=1&status=DRAFT&per_page=5")
    
    if response.status_code == 200:
        data = response.json()
        animals = data.get('animals', [])
        print(f"找到 {len(animals)} 隻草稿動物")
        
        if len(animals) >= 2:
            # 取前兩隻動物做測試
            animal_ids = [animals[0]['animal_id'], animals[1]['animal_id']]
            
            print(f"\n2. 測試批次提交審核...")
            print(f"動物 IDs: {animal_ids}")
            
            # 測試批次提交 (不需要 JWT token 做基本測試)
            batch_data = {
                "animal_ids": animal_ids,
                "action": "submit"
            }
            
            print(f"請求資料: {json.dumps(batch_data, indent=2)}")
            
            # 由於需要 JWT 認證，這裡只測試端點是否存在
            try:
                response = requests.patch(
                    f"{BASE_URL}/shelters/1/animals/batch/status", 
                    json=batch_data,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"狀態碼: {response.status_code}")
                print(f"回應: {response.text}")
                
                if response.status_code == 401:
                    print("✅ API 端點存在 (需要認證)")
                elif response.status_code == 200:
                    print("✅ 批次狀態更新成功")
                else:
                    print(f"❌ 未預期的狀態碼: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 請求失敗: {e}")
        else:
            print("❌ 草稿動物數量不足，無法測試批次操作")
    else:
        print(f"❌ 查詢動物失敗: {response.status_code}")

def test_batch_upload_csv_format():
    """測試 CSV 格式驗證"""
    
    print("\n=== CSV 格式測試 ===")
    
    # 創建測試 CSV 內容
    csv_content = """animal_code,name,species,breed,sex,dob,color,description
TEST001,測試小貓,CAT,米克斯,FEMALE,2023-01-01,橘色,很親人的小貓
TEST002,測試小狗,DOG,拉布拉多,MALE,2022-06-15,黑色,活潑好動的狗狗"""
    
    print("測試 CSV 內容:")
    print(csv_content)
    
    # 驗證 CSV 解析
    import io
    import csv
    
    try:
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        headers = csv_reader.fieldnames
        print(f"\n✅ CSV 標題: {headers}")
        
        required_headers = ['animal_code', 'name', 'species', 'breed', 'sex', 'dob', 'color', 'description']
        missing_headers = [h for h in required_headers if h not in headers]
        
        if missing_headers:
            print(f"❌ 缺少必要標題: {missing_headers}")
        else:
            print("✅ CSV 格式正確")
            
        # 讀取資料行
        rows = list(csv_reader)
        print(f"✅ 資料行數: {len(rows)}")
        
        for i, row in enumerate(rows):
            print(f"  行 {i+1}: {row['animal_code']} - {row['name']}")
            
    except Exception as e:
        print(f"❌ CSV 解析失敗: {e}")

if __name__ == "__main__":
    test_batch_upload_csv_format()
    test_batch_status_management()
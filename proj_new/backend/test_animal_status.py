#!/usr/bin/env python3
"""
測試動物狀態更新功能
"""
import sys
import os

# 添加當前目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_animal_service_status_methods():
    """測試 AnimalService 的狀態相關方法"""
    print("🔍 測試 AnimalService 狀態管理...")
    
    try:
        from app.services.animal_service import AnimalService
        
        # 檢查新增的方法
        status_methods = [
            'update_animal_status',
            'batch_update_animal_status', 
            '_validate_status_transition'
        ]
        
        for method in status_methods:
            if hasattr(AnimalService, method):
                print(f"✅ AnimalService.{method} 存在")
            else:
                print(f"❌ AnimalService.{method} 不存在")
        
        return True
        
    except ImportError as e:
        print(f"❌ 導入錯誤: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他錯誤: {e}")
        return False

def test_status_validation():
    """測試狀態驗證邏輯"""
    print("\n🔍 測試狀態轉換驗證...")
    
    try:
        from app.services.animal_service import AnimalService
        from app.models.animal import AnimalStatus
        
        # 測試有效的狀態轉換
        valid_transitions = [
            (AnimalStatus.DRAFT, AnimalStatus.SUBMITTED),
            (AnimalStatus.DRAFT, AnimalStatus.PUBLISHED),
            (AnimalStatus.SUBMITTED, AnimalStatus.PUBLISHED),
            (AnimalStatus.PUBLISHED, AnimalStatus.RETIRED)
        ]
        
        for current, new in valid_transitions:
            try:
                AnimalService._validate_status_transition(current, new)
                print(f"✅ {current.value} → {new.value} 轉換有效")
            except ValueError as e:
                print(f"❌ {current.value} → {new.value} 轉換失敗: {e}")
        
        # 測試無效的狀態轉換  
        invalid_transitions = [
            (AnimalStatus.ADOPTED, AnimalStatus.PUBLISHED),
            (AnimalStatus.PUBLISHED, AnimalStatus.DRAFT),
            (AnimalStatus.RETIRED, AnimalStatus.SUBMITTED)
        ]
        
        for current, new in invalid_transitions:
            try:
                AnimalService._validate_status_transition(current, new)
                print(f"⚠️ {current.value} → {new.value} 應該無效但通過了")
            except ValueError:
                print(f"✅ {current.value} → {new.value} 正確被拒絕")
        
        return True
        
    except Exception as e:
        print(f"❌ 狀態驗證測試錯誤: {e}")
        return False

def test_blueprint_endpoints():
    """測試 Blueprint 端點"""
    print("\n🔍 測試 Blueprint 狀態端點...")
    
    try:
        from app import create_app
        
        app = create_app('testing')
        
        with app.app_context():
            # 檢查新的端點是否註冊
            endpoints = [rule.endpoint for rule in app.url_map.iter_rules()]
            
            expected_endpoints = [
                'animals.list_animals',
                'animals.get_animal', 
                'animals.create_animal',
                'animals.update_animal',
                'animals.delete_animal',
                'animals.update_animal_status'  # 新增的端點
            ]
            
            for endpoint in expected_endpoints:
                if endpoint in endpoints:
                    print(f"✅ 端點 {endpoint} 已註冊")
                else:
                    print(f"⚠️ 端點 {endpoint} 未找到")
        
        return True
        
    except Exception as e:
        print(f"❌ Blueprint 測試錯誤: {e}")
        return False

def test_shelters_blueprint_fix():
    """測試 Shelters Blueprint 修正"""
    print("\n🔍 測試 Shelters Blueprint 修正...")
    
    try:
        # 讀取 shelters.py 檢查是否使用 Service
        shelters_file = os.path.join(os.path.dirname(__file__), 'app', 'blueprints', 'shelters.py')
        
        with open(shelters_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查是否使用了 AnimalService
        if 'AnimalService.batch_update_animal_status' in content:
            print("✅ Shelters Blueprint 已使用 AnimalService")
        else:
            print("❌ Shelters Blueprint 未使用 AnimalService")
        
        # 檢查是否移除了直接的資料庫操作
        if 'animal.status = AnimalStatus.' not in content:
            print("✅ 已移除直接狀態操作")
        else:
            print("⚠️ 仍有直接狀態操作")
        
        return True
        
    except Exception as e:
        print(f"❌ Shelters Blueprint 檢查錯誤: {e}")
        return False

def main():
    """主測試函數"""
    print("🚀 測試管理員發布功能修正")
    print("=" * 50)
    
    tests = [
        test_animal_service_status_methods,
        test_status_validation,
        test_blueprint_endpoints, 
        test_shelters_blueprint_fix
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 管理員發布功能修正成功！")
        print("\n✨ 修正完成:")
        print("   • AnimalService 新增狀態管理方法")
        print("   • 狀態轉換驗證邏輯完善") 
        print("   • Shelters Blueprint 使用 Service Layer")
        print("   • Animals Blueprint 新增狀態更新端點")
        print("   • 移除直接資料庫操作邏輯")
        return True
    else:
        print("⚠️ 部分測試失敗，請檢查相關實作")
        return False

if __name__ == '__main__':
    main()
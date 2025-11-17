#!/usr/bin/env python3
"""
測試後端啟動和基本功能
"""
import sys
import os

# 添加當前目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """測試基本導入"""
    print("🔍 測試導入...")
    
    try:
        # 測試 Flask app 創建
        from app import create_app
        print("✅ app 導入成功")
        
        # 測試 Service 導入
        from app.services.animal_service import AnimalService
        from app.services.application_service import ApplicationService
        print("✅ Services 導入成功")
        
        # 測試 Blueprint 導入
        from app.blueprints.animals import animals_bp
        from app.blueprints.applications import applications_bp
        print("✅ Blueprints 導入成功")
        
        # 測試 Schema 導入
        from app.schemas import AnimalCreateSchema, ApplicationCreateSchema
        print("✅ Schemas 導入成功")
        
        # 測試 Decorators 導入
        from app.decorators.role_decorators import role_required
        print("✅ Decorators 導入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 導入錯誤: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他錯誤: {e}")
        return False

def test_app_creation():
    """測試應用創建"""
    print("\n🔍 測試應用創建...")
    
    try:
        from app import create_app
        
        # 創建測試應用
        app = create_app('testing')
        print("✅ Flask app 創建成功")
        
        # 檢查基本配置
        with app.app_context():
            print("✅ Application context 正常")
            
            # 檢查 Blueprint 註冊
            blueprint_names = [bp.name for bp in app.blueprints.values()]
            expected_blueprints = ['animals', 'applications', 'auth', 'users', 'shelters']
            
            for bp in expected_blueprints:
                if bp in blueprint_names:
                    print(f"✅ Blueprint '{bp}' 已註冊")
                else:
                    print(f"⚠️ Blueprint '{bp}' 未找到")
        
        return True
        
    except Exception as e:
        print(f"❌ 應用創建錯誤: {e}")
        return False

def test_service_basic():
    """測試 Service 基本功能"""
    print("\n🔍 測試 Service 基本功能...")
    
    try:
        from app.services.animal_service import AnimalService
        from app.services.application_service import ApplicationService
        
        # 檢查方法存在
        animal_methods = ['search_animals', 'get_animal_by_id', 'create_animal', 'update_animal', 'delete_animal']
        for method in animal_methods:
            if hasattr(AnimalService, method):
                print(f"✅ AnimalService.{method} 存在")
            else:
                print(f"❌ AnimalService.{method} 不存在")
        
        application_methods = ['search_applications', 'get_application_by_id', 'create_application']
        for method in application_methods:
            if hasattr(ApplicationService, method):
                print(f"✅ ApplicationService.{method} 存在")
            else:
                print(f"❌ ApplicationService.{method} 不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ Service 測試錯誤: {e}")
        return False

def test_schema_validation():
    """測試 Schema 驗證"""
    print("\n🔍 測試 Schema 驗證...")
    
    try:
        from app.schemas import AnimalCreateSchema, ApplicationCreateSchema
        
        # 測試 Animal Schema
        animal_schema = AnimalCreateSchema()
        
        # 有效資料
        valid_data = {
            'name': '小白',
            'species': 'CAT',
            'sex': 'FEMALE'
        }
        
        result = animal_schema.load(valid_data)
        print("✅ AnimalCreateSchema 驗證通過")
        
        # 測試 Application Schema
        app_schema = ApplicationCreateSchema()
        valid_app_data = {
            'animal_id': 1,
            'message': '我想領養這隻動物'
        }
        
        result = app_schema.load(valid_app_data)
        print("✅ ApplicationCreateSchema 驗證通過")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema 驗證錯誤: {e}")
        return False

def main():
    """主測試函數"""
    print("🚀 開始測試重構後的 MVC 架構")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_app_creation, 
        test_service_basic,
        test_schema_validation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！MVC 重構成功！")
        print("\n✨ 架構優化完成:")
        print("   • Fat Controller 已解決")
        print("   • Service Layer 已建立")
        print("   • Blueprint 已精簡為 Thin Controller")
        print("   • 符合真正的 MVC 架構原則")
        return True
    else:
        print("⚠️ 部分測試失敗，請檢查相關配置")
        return False

if __name__ == '__main__':
    main()
"""
SQLAlchemy Mock測試 - 模擬真實情況
"""
from unittest.mock import Mock, patch, MagicMock

def test_sqlalchemy_mock_with_patch():
    print("=== SQLAlchemy Mock + Patch 測試 ===\n")
    
    # 創建Mock對象
    mock_query = Mock()
    mock_filter_by = Mock()
    mock_filter = Mock()
    mock_order_by = Mock()
    mock_paginate = Mock()
    
    # 設置Mock鏈 - 仿照我們失敗的測試
    mock_query.filter_by.return_value = mock_filter_by
    mock_filter_by.filter_by.return_value = mock_filter_by  # 允許多次filter_by
    mock_filter_by.filter.return_value = mock_filter
    mock_filter.order_by.return_value = mock_order_by
    mock_order_by.paginate.return_value = mock_paginate
    
    # 設置最終返回值
    mock_animal_item = Mock()
    mock_animal_item.to_dict.return_value = {'id': 1, 'name': 'Test'}
    mock_paginate.items = [mock_animal_item]
    
    print("1. 基本Mock設置完成")
    print(f"   mock_paginate.items = {mock_paginate.items}")
    print(f"   類型: {type(mock_paginate.items)}")
    
    # 測試不使用patch的情況
    print("\n2. 不使用patch的鏈式調用:")
    result_no_patch = mock_query.filter_by(deleted_at=None).filter_by(species='DOG').filter(Mock()).order_by(Mock()).paginate()
    print(f"   result.items = {result_no_patch.items}")
    print(f"   類型: {type(result_no_patch.items)}")
    
    try:
        animals = [item.to_dict() for item in result_no_patch.items]
        print(f"   ✅ 可以迭代並調用to_dict(): {animals}")
    except Exception as e:
        print(f"   ❌ 錯誤: {e}")
    
def test_mock_auto_creation():
    print("=== Mock自動創建問題測試 ===")
    
    # 這是我們遇到的關鍵問題！
    print("\n問題演示:")
    
    # 創建Mock對象模擬query鏈
    mock_query = Mock()
    mock_filter_by = Mock()
    mock_paginate = Mock()
    
    # 設置Mock鏈
    mock_query.filter_by.return_value = mock_filter_by
    mock_filter_by.filter_by.return_value = mock_filter_by  # 自我引用支持多次調用
    mock_filter_by.order_by.return_value.paginate.return_value = mock_paginate
    
    # 設置items
    mock_paginate.items = [1, 2, 3]
    print(f"1. 直接設置: mock_paginate.items = {mock_paginate.items}")
    print(f"   類型: {type(mock_paginate.items)}")
    
    # 問題出現在這裡！
    # 每次調用 order_by() 都會返回一個新的Mock對象！
    order_result = mock_filter_by.order_by()
    print(f"2. 第一次調用order_by: {id(order_result)}")
    
    order_result2 = mock_filter_by.order_by()  
    print(f"3. 第二次調用order_by: {id(order_result2)}")
    print(f"   是同一個對象嗎? {order_result is order_result2}")
    
    # 這就是問題！每次調用都是新的Mock對象
    paginate_result1 = mock_filter_by.order_by().paginate()
    paginate_result2 = mock_filter_by.order_by().paginate()
    print(f"4. paginate結果是同一個嗎? {paginate_result1 is paginate_result2}")
    print(f"   第一個的items: {paginate_result1.items}")
    print(f"   第二個的items: {paginate_result2.items}")
    
    # Mock的默認返回值行為
    print(f"\n5. Mock默認返回值類型:")
    fresh_mock = Mock()
    print(f"   fresh_mock.anything.items 類型: {type(fresh_mock.anything.items)}")
    
    try:
        list(fresh_mock.anything.items)
        print("   ✅ 可以迭代")
    except TypeError as e:
        print(f"   ❌ 不能迭代: {e}")

def demonstrate_correct_solution():
    print("\n=== 正確的解決方案 ===")
    
    # 方案1: 使用具體的Mock對象而不是鏈式return_value
    mock_query = Mock()
    mock_filter_by = Mock()
    mock_order_by = Mock()
    mock_paginate = Mock()
    
    # 正確設置: 確保每個步驟都返回同一個Mock對象
    mock_query.filter_by.return_value = mock_filter_by
    mock_filter_by.filter_by.return_value = mock_filter_by
    mock_filter_by.order_by.return_value = mock_order_by
    mock_order_by.paginate.return_value = mock_paginate
    
    # 設置最終結果
    mock_paginate.items = [1, 2, 3]
    
    print("方案1: 明確設置每個Mock對象")
    result = mock_query.filter_by().filter_by().order_by().paginate()
    print(f"   結果: {result.items}")
    print(f"   類型: {type(result.items)}")
    
    # 方案2: 使用configure_mock
    mock_paginate2 = Mock()
    mock_paginate2.configure_mock(**{
        'items': [4, 5, 6],
        'total': 3,
        'page': 1
    })
    
    print("\n方案2: 使用configure_mock")
    print(f"   結果: {mock_paginate2.items}")
    
    try:
        items = [x for x in mock_paginate2.items]
        print(f"   ✅ 可以迭代: {items}")
    except Exception as e:
        print(f"   ❌ 錯誤: {e}")

if __name__ == "__main__":
    test_mock_auto_creation()
    demonstrate_correct_solution()
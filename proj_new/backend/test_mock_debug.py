"""
Mock調試示例 - 展示為什麼Mock會失敗
"""
from unittest.mock import Mock, patch

def demonstrate_mock_issue():
    print("=== Mock問題示範 ===\n")
    
    # 1. 簡單Mock - 這會工作
    print("1. 簡單Mock情況:")
    simple_mock = Mock()
    simple_mock.items = [1, 2, 3]
    print(f"simple_mock.items = {simple_mock.items}")
    print(f"可以迭代: {[x for x in simple_mock.items]}")
    
    print()
    
    # 2. 鏈式調用Mock - 這裡開始有問題
    print("2. 鏈式調用Mock情況:")
    query_mock = Mock()
    filter_by_mock = Mock()
    filter_mock = Mock()
    paginate_mock = Mock()
    
    # 設置鏈式調用
    query_mock.filter_by.return_value = filter_by_mock
    filter_by_mock.filter.return_value = filter_mock  # 注意這裡
    filter_mock.order_by.return_value.paginate.return_value = paginate_mock
    
    # 設置最終結果
    paginate_mock.items = [1, 2, 3]
    print(f"設置前: paginate_mock.items = {paginate_mock.items}")
    
    # 模擬實際調用
    result = query_mock.filter_by(deleted_at=None).filter(Mock()).order_by(Mock()).paginate()
    print(f"鏈式調用後: result.items = {result.items}")
    print(f"result.items 類型: {type(result.items)}")
    
    try:
        items = [x for x in result.items]
        print(f"可以迭代: {items}")
    except TypeError as e:
        print(f"❌ 不能迭代: {e}")
    
    print()
    
    # 3. 更複雜的情況 - 多重filter_by調用
    print("3. 多重filter_by調用:")
    query_mock2 = Mock()
    
    # 錯誤的設置方式
    filter_by_result = Mock()
    query_mock2.filter_by.return_value = filter_by_result
    filter_by_result.filter_by.return_value = filter_by_result  # 自我引用
    filter_by_result.filter.return_value = filter_by_result
    filter_by_result.order_by.return_value.paginate.return_value.items = [1, 2, 3]
    
    # 實際調用路徑
    result2 = query_mock2.filter_by(deleted_at=None).filter_by(species='DOG').filter(Mock()).order_by(Mock()).paginate()
    print(f"複雜調用後: result2.items = {result2.items}")
    print(f"result2.items 類型: {type(result2.items)}")

if __name__ == "__main__":
    demonstrate_mock_issue()
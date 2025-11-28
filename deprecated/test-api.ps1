# ========== 寵物領養平台 API 測試腳本 ==========
Write-Host "
========== 開始 API 測試 ==========" -ForegroundColor Cyan

# 測試結果統計
$passed = 0
$failed = 0

function Test-Endpoint {
    param($name, $scriptBlock)
    Write-Host "
測試: $name" -ForegroundColor Yellow
    try {
        & $scriptBlock
        $script:passed++
        Write-Host "✓ 通過" -ForegroundColor Green
    } catch {
        $script:failed++
        Write-Host "✗ 失敗: $_" -ForegroundColor Red
    }
}

# 1. 測試公開端點 - 獲取動物列表
Test-Endpoint "GET /api/animals - 獲取動物列表" {
    $response = Invoke-WebRequest -Uri 'http://localhost:5000/api/animals?page=1&per_page=5' -Method GET -UseBasicParsing
    if ($response.StatusCode -ne 200) { throw "狀態碼錯誤: $($response.StatusCode)" }
    $data = $response.Content | ConvertFrom-Json
    Write-Host "  總數: $($data.total), 當前頁: $($data.items.Count) 筆"
}

# 2. 測試用戶註冊
Test-Endpoint "POST /api/auth/register - 用戶註冊" {
    $timestamp = [DateTimeOffset]::Now.ToUnixTimeSeconds()
    $body = @{
        username = "testuser$timestamp"
        password = 'TestPass123!'
        email = "test$timestamp@example.com"
        role = 'GENERAL_MEMBER'
    } | ConvertTo-Json
    $response = Invoke-WebRequest -Uri 'http://localhost:5000/api/auth/register' -Method POST -Body $body -ContentType 'application/json' -UseBasicParsing
    if ($response.StatusCode -ne 201) { throw "狀態碼錯誤: $($response.StatusCode)" }
    $data = $response.Content | ConvertFrom-Json
    $global:testEmail = $data.user.email
    $global:testPassword = 'TestPass123!'
    Write-Host "  註冊成功: $($data.user.username) ($($data.user.email))"
}

# 3. 測試用戶登入
Test-Endpoint "POST /api/auth/login - 用戶登入" {
    $body = @{
        email = $global:testEmail
        password = $global:testPassword
    } | ConvertTo-Json
    $response = Invoke-WebRequest -Uri 'http://localhost:5000/api/auth/login' -Method POST -Body $body -ContentType 'application/json' -UseBasicParsing
    if ($response.StatusCode -ne 200) { throw "狀態碼錯誤: $($response.StatusCode)" }
    $data = $response.Content | ConvertFrom-Json
    $global:accessToken = $data.access_token
    $global:userId = $data.user.user_id
    Write-Host "  登入成功: User ID $global:userId"
    Write-Host "  Token (前30字): $($global:accessToken.Substring(0,30))..."
}

# 4. 測試通知列表
Test-Endpoint "GET /api/notifications - 獲取通知列表" {
    $headers = @{Authorization = "Bearer $global:accessToken"}
    $response = Invoke-WebRequest -Uri 'http://localhost:5000/api/notifications?page=1&per_page=10' -Method GET -Headers $headers -UseBasicParsing
    if ($response.StatusCode -ne 200) { throw "狀態碼錯誤: $($response.StatusCode)" }
    $data = $response.Content | ConvertFrom-Json
    Write-Host "  通知總數: $($data.total), 當前頁: $($data.items.Count) 筆"
}

# 5. 測試未讀通知數量
Test-Endpoint "GET /api/notifications/unread-count - 獲取未讀通知數" {
    $headers = @{Authorization = "Bearer $global:accessToken"}
    $response = Invoke-WebRequest -Uri 'http://localhost:5000/api/notifications/unread-count' -Method GET -Headers $headers -UseBasicParsing
    if ($response.StatusCode -ne 200) { throw "狀態碼錯誤: $($response.StatusCode)" }
    $data = $response.Content | ConvertFrom-Json
    Write-Host "  未讀數量: $($data.unread_count)"
}

# 6. 測試申請列表
Test-Endpoint "GET /api/applications - 獲取申請列表" {
    $headers = @{Authorization = "Bearer $global:accessToken"}
    $response = Invoke-WebRequest -Uri 'http://localhost:5000/api/applications?page=1&per_page=10' -Method GET -Headers $headers -UseBasicParsing
    if ($response.StatusCode -ne 200) { throw "狀態碼錯誤: $($response.StatusCode)" }
    $data = $response.Content | ConvertFrom-Json
    Write-Host "  申請總數: $($data.total), 當前頁: $($data.items.Count) 筆"
}

# 測試結果摘要
Write-Host "
========== 測試結果摘要 ==========" -ForegroundColor Cyan
Write-Host "通過: $passed 個測試" -ForegroundColor Green
Write-Host "失敗: $failed 個測試" -ForegroundColor Red
Write-Host "總計: $($passed + $failed) 個測試"

if ($failed -eq 0) {
    Write-Host "
所有測試通過! ✓" -ForegroundColor Green
} else {
    Write-Host "
有 $failed 個測試失敗" -ForegroundColor Red
}

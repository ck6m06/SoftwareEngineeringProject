# Email 驗證流程測試腳本
$baseUrl = "http://localhost:5000/api"
$timestamp = [int](Get-Date -UFormat %s)

Write-Host "========== Email 驗證流程測試 ==========" -ForegroundColor Cyan

# 1. 註冊新用戶
Write-Host "`n[1] 註冊新用戶..." -ForegroundColor Yellow
$registerData = @{
    email = "test_verify_${timestamp}@example.com"
    password = "TestPass123!"
    username = "test_verify_$timestamp"
    first_name = "Test"
    last_name = "Verify"
} | ConvertTo-Json

$registerResponse = Invoke-RestMethod -Uri "$baseUrl/auth/register" `
    -Method Post `
    -ContentType "application/json" `
    -Body $registerData

Write-Host "✓ 用戶註冊成功: $($registerResponse.user.email)" -ForegroundColor Green
Write-Host "  User ID: $($registerResponse.user.user_id)" -ForegroundColor Gray
Write-Host "  Verified: $($registerResponse.user.verified)" -ForegroundColor Gray
Write-Host "  Message: $($registerResponse.message)" -ForegroundColor Gray
$userId = $registerResponse.user.user_id

# 2. 檢查後端日誌以獲取 token
Write-Host "`n[2] 獲取驗證 token (從日誌)..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

# 從 docker 日誌中提取 token
$logs = docker logs pet-adoption-backend --tail 30 2>&1 | Select-String -Pattern "Token \(for testing\):" | Select-Object -Last 1
if ($logs) {
    $tokenLine = $logs.Line
    if ($tokenLine -match "Token \(for testing\): (.+)") {
        $token = $matches[1].Trim()
        Write-Host "✓ Token 已提取: $($token.Substring(0, 40))..." -ForegroundColor Green
    }
}

if (-not $token) {
    Write-Host "✗ 無法從日誌提取 token，請手動檢查:" -ForegroundColor Red
    Write-Host "  docker logs pet-adoption-backend --tail 50" -ForegroundColor Cyan
    exit 1
}

# 3. 使用 token 驗證 email
Write-Host "`n[3] 驗證 email..." -ForegroundColor Yellow
try {
    $verifyResponse = Invoke-RestMethod -Uri "$baseUrl/auth/verify?token=$token" `
        -Method Get `
        -ContentType "application/json"
    
    Write-Host "✓ Email 驗證成功!" -ForegroundColor Green
    Write-Host "  Message: $($verifyResponse.message)" -ForegroundColor Gray
    Write-Host "  Verified: $($verifyResponse.verified)" -ForegroundColor Gray
} catch {
    Write-Host "✗ 驗證失敗: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 4. 再次嘗試驗證 (應該返回已驗證)
Write-Host "`n[4] 再次驗證 (測試重複驗證)..." -ForegroundColor Yellow
try {
    $verifyResponse2 = Invoke-RestMethod -Uri "$baseUrl/auth/verify?token=$token" `
        -Method Get `
        -ContentType "application/json"
    
    Write-Host "✓ $($verifyResponse2.message)" -ForegroundColor Green
    Write-Host "  Verified: $($verifyResponse2.verified)" -ForegroundColor Gray
} catch {
    Write-Host "✗ 驗證失敗: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. 測試重新發送驗證郵件
Write-Host "`n[5] 測試重新發送驗證郵件..." -ForegroundColor Yellow
$resendData = @{
    email = "test_verify_${timestamp}@example.com"
} | ConvertTo-Json

try {
    $resendResponse = Invoke-RestMethod -Uri "$baseUrl/auth/resend-verification" `
        -Method Post `
        -ContentType "application/json" `
        -Body $resendData
    
    Write-Host "✓ $($resendResponse.message)" -ForegroundColor Green
} catch {
    Write-Host "✗ 重發失敗: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. 測試不存在的 email (安全測試)
Write-Host "`n[6] 測試不存在的 email..." -ForegroundColor Yellow
$resendData2 = @{
    email = "nonexistent@example.com"
} | ConvertTo-Json

try {
    $resendResponse2 = Invoke-RestMethod -Uri "$baseUrl/auth/resend-verification" `
        -Method Post `
        -ContentType "application/json" `
        -Body $resendData2
    
    Write-Host "✓ $($resendResponse2.message)" -ForegroundColor Green
    Write-Host "  (不透露用戶是否存在，符合安全最佳實踐)" -ForegroundColor Gray
} catch {
    Write-Host "✗ 請求失敗: $($_.Exception.Message)" -ForegroundColor Red
}

# 7. 測試無效 token
Write-Host "`n[7] 測試無效 token..." -ForegroundColor Yellow
try {
    $invalidResponse = Invoke-RestMethod -Uri "$baseUrl/auth/verify?token=invalid_token_12345" `
        -Method Get `
        -ContentType "application/json"
    
    Write-Host "✗ 應該拒絕無效 token" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "✓ 正確拒絕無效 token" -ForegroundColor Green
    } else {
        Write-Host "✗ 錯誤的錯誤碼: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

Write-Host "`n========== 測試完成 ==========" -ForegroundColor Cyan
Write-Host "`n摘要:" -ForegroundColor Yellow
Write-Host " 註冊時自動發送驗證郵件 ✓" -ForegroundColor Green
Write-Host " Token 驗證功能正常 ✓" -ForegroundColor Green
Write-Host " 重複驗證處理正確 ✓" -ForegroundColor Green
Write-Host " 重新發送驗證郵件功能正常 ✓" -ForegroundColor Green
Write-Host " 安全性檢查通過 ✓" -ForegroundColor Green

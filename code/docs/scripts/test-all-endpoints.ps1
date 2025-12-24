# 全面API測試腳本
$baseUrl = "http://localhost:5000/api"
$passCount = 0
$failCount = 0

Write-Host "`n========== 後端API完整測試 ==========" -ForegroundColor Cyan

# 1. 健康檢查
Write-Host "`n[Health] 測試健康檢查端點" -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:5000/healthz"
    $ready = Invoke-RestMethod -Uri "http://localhost:5000/readyz"
    Write-Host "✓ Health: $($health.status), Ready: $($ready.status)" -ForegroundColor Green
    $passCount++
} catch {
    Write-Host "✗ 健康檢查失敗: $_" -ForegroundColor Red
    $failCount++
}

# 2. Metrics
Write-Host "`n[Metrics] 測試Prometheus端點" -ForegroundColor Yellow
try {
    $metrics = Invoke-RestMethod -Uri "http://localhost:5000/metrics"
    Write-Host "✓ Metrics端點正常 (${metrics.Length} bytes)" -ForegroundColor Green
    $passCount++
} catch {
    Write-Host "✗ Metrics失敗: $_" -ForegroundColor Red
    $failCount++
}

# 3. 註冊並登入
$timestamp = [DateTimeOffset]::Now.ToUnixTimeSeconds()
$testUser = @{
    username = "admin_$timestamp"
    email = "admin_$timestamp@test.com"
    password = "Password123!"
    role = "ADMIN"
}

Write-Host "`n[Auth] 測試認證系統" -ForegroundColor Yellow
try {
    $registerResponse = Invoke-RestMethod -Uri "$baseUrl/auth/register" -Method Post -Body ($testUser | ConvertTo-Json) -ContentType "application/json"
    Write-Host "✓ 管理員註冊成功: $($registerResponse.user.username)" -ForegroundColor Green
    $passCount++
} catch {
    Write-Host "✗ 註冊失敗: $_" -ForegroundColor Red
    $failCount++
}

try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post -Body (@{email=$testUser.email; password=$testUser.password} | ConvertTo-Json) -ContentType "application/json"
    $token = $loginResponse.access_token
    Write-Host "✓ 登入成功,獲得Token" -ForegroundColor Green
    $passCount++
} catch {
    Write-Host "✗ 登入失敗: $_" -ForegroundColor Red
    $failCount++
    exit
}

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# 4. Admin Stats
Write-Host "`n[Admin] 測試管理員統計API" -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "$baseUrl/admin/stats" -Headers $headers
    Write-Host "✓ 系統統計: $($stats.users.total) 用戶, $($stats.animals.total) 動物" -ForegroundColor Green
    $passCount++
} catch {
    Write-Host "✗ 統計失敗: $_" -ForegroundColor Red
    $failCount++
}

# 5. Shelters - 創建收容所
Write-Host "`n[Shelters] 測試收容所管理" -ForegroundColor Yellow
$shelterData = @{
    name = "測試收容所"
    contact_email = "shelter@test.com"
    contact_phone = "0912345678"
    address = @{
        street = "測試路123號"
        city = "台北市"
        county = "信義區"
        postal_code = "110"
    }
}

try {
    $shelter = Invoke-RestMethod -Uri "$baseUrl/shelters" -Method Post -Body ($shelterData | ConvertTo-Json) -Headers $headers
    $shelterId = $shelter.shelter.shelter_id
    Write-Host "✓ 收容所創建成功: ID=$shelterId" -ForegroundColor Green
    $passCount++
    
    # 驗證收容所
    $verifyData = @{ verified = $true } | ConvertTo-Json
    $verified = Invoke-RestMethod -Uri "$baseUrl/shelters/$shelterId/verify" -Method Post -Body $verifyData -Headers $headers
    Write-Host "✓ 收容所驗證成功" -ForegroundColor Green
    $passCount++
} catch {
    Write-Host "✗ 收容所操作失敗: $_" -ForegroundColor Red
    $failCount++
}

# 6. Jobs - 查詢任務
Write-Host "`n[Jobs] 測試任務管理" -ForegroundColor Yellow
try {
    $jobs = Invoke-RestMethod -Uri "$baseUrl/jobs?page=1&per_page=10" -Headers $headers
    Write-Host "✓ 任務列表查詢成功: $($jobs.total) 個任務" -ForegroundColor Green
    $passCount++
} catch {
    Write-Host "✗ 任務查詢失敗: $_" -ForegroundColor Red
    $failCount++
}

# 總結
Write-Host "`n========== 測試結果摘要 ==========" -ForegroundColor Cyan
Write-Host "通過: $passCount 個測試" -ForegroundColor Green
Write-Host "失敗: $failCount 個測試" -ForegroundColor Red
Write-Host "總計: $($passCount + $failCount) 個測試" -ForegroundColor White

if ($failCount -eq 0) {
    Write-Host "`n所有測試通過! ✓" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n有 $failCount 個測試失敗" -ForegroundColor Red
    exit 1
}

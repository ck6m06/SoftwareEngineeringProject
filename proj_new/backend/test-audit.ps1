# 審計日誌測試腳本
$baseUrl = "http://localhost:5000/api"

Write-Host "`n========== 審計日誌功能測試 ==========" -ForegroundColor Cyan

# 1. 註冊管理員並登入
$timestamp = [DateTimeOffset]::Now.ToUnixTimeSeconds()
$admin = @{
    username = "admin_audit_$timestamp"
    email = "admin_audit_$timestamp@test.com"
    password = "Password123!"
    role = "ADMIN"
}

$registerRes = Invoke-RestMethod -Uri "$baseUrl/auth/register" -Method Post -Body ($admin | ConvertTo-Json) -ContentType "application/json"
Write-Host "✓ 管理員註冊: $($registerRes.user.username)" -ForegroundColor Green

$loginRes = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post -Body (@{email=$admin.email; password=$admin.password} | ConvertTo-Json) -ContentType "application/json"
$token = $loginRes.access_token
Write-Host "✓ 登入成功,獲得Token" -ForegroundColor Green

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# 2. 執行一些會產生audit log的操作

# 2.1 創建收容所
Write-Host "`n[Shelters] 創建並驗證收容所" -ForegroundColor Yellow
$shelterData = @{
    name = "測試收容所_$timestamp"
    contact_email = "shelter_$timestamp@test.com"
    contact_phone = "0912345678"
    address = @{
        street = "測試路123號"
        city = "台北市"
        county = "信義區"
        postal_code = "110"
    }
}
$shelter = Invoke-RestMethod -Uri "$baseUrl/shelters" -Method Post -Body ($shelterData | ConvertTo-Json) -Headers $headers
$shelterId = $shelter.shelter.shelter_id
Write-Host "✓ 收容所創建成功: ID=$shelterId" -ForegroundColor Green

$verifyRes = Invoke-RestMethod -Uri "$baseUrl/shelters/$shelterId/verify" -Method Post -Body (@{verified=$true} | ConvertTo-Json) -Headers $headers
Write-Host "✓ 收容所驗證成功" -ForegroundColor Green

# 2.2 註冊一般用戶並封禁
Write-Host "`n[Users] 創建並封禁用戶" -ForegroundColor Yellow
$testUser = @{
    username = "user_test_$timestamp"
    email = "user_test_$timestamp@test.com"
    password = "Password123!"
}
$userRes = Invoke-RestMethod -Uri "$baseUrl/auth/register" -Method Post -Body ($testUser | ConvertTo-Json) -ContentType "application/json"
$targetUserId = $userRes.user.user_id
Write-Host "✓ 測試用戶創建: ID=$targetUserId" -ForegroundColor Green

$banRes = Invoke-RestMethod -Uri "$baseUrl/admin/users/$targetUserId/ban" -Method Post -Body (@{days=7;reason="測試封禁"} | ConvertTo-Json) -Headers $headers
Write-Host "✓ 用戶已封禁7天" -ForegroundColor Green

# 3. 查詢審計日誌
Write-Host "`n[Audit] 查詢審計日誌" -ForegroundColor Yellow
Start-Sleep -Seconds 1

try {
    $auditLogs = Invoke-RestMethod -Uri "$baseUrl/admin/audit?page=1&per_page=10" -Headers $headers
    Write-Host "✓ 審計日誌查詢成功" -ForegroundColor Green
    Write-Host "  總記錄數: $($auditLogs.total)" -ForegroundColor White
    
    if ($auditLogs.audit_logs.Count -gt 0) {
        Write-Host "`n最近的審計記錄:" -ForegroundColor Cyan
        foreach ($log in $auditLogs.audit_logs | Select-Object -First 5) {
            Write-Host "  - [$($log.action)] by User#$($log.actor_id) at $($log.timestamp)" -ForegroundColor Gray
            if ($log.target_type) {
                Write-Host "    Target: $($log.target_type)#$($log.target_id)" -ForegroundColor Gray
            }
        }
    }
} catch {
    Write-Host "✗ 審計日誌查詢失敗: $_" -ForegroundColor Red
}

# 4. 測試篩選功能
Write-Host "`n[Audit] 測試篩選 - 只查詢shelter相關操作" -ForegroundColor Yellow
try {
    $shelterAudit = Invoke-RestMethod -Uri "$baseUrl/admin/audit?target_type=shelter" -Headers $headers
    Write-Host "✓ 找到 $($shelterAudit.total) 筆收容所相關記錄" -ForegroundColor Green
} catch {
    Write-Host "✗ 篩選查詢失敗: $_" -ForegroundColor Red
}

Write-Host "`n========== 測試完成 ==========" -ForegroundColor Cyan

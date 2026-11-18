$ErrorActionPreference = 'Stop'
$baseUrl = if ($env:BASE_URL) { $env:BASE_URL } else { 'http://localhost:8000' }
$health = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
if ($health.status -ne 'ok' -or $health.model_loaded -ne $true) {
    throw "Health check failed: $($health | ConvertTo-Json -Compress)"
}
Write-Host "HEALTH PASS: $($health | ConvertTo-Json -Compress)"
$body = @{
    tenure_months = 12
    monthly_fee = 85.5
    support_calls = 3
    contract = 'month-to-month'
    internet_service = 'fiber'
} | ConvertTo-Json
$result = Invoke-RestMethod -Uri "$baseUrl/predict" -Method Post -ContentType 'application/json' -Body $body
if ($null -eq $result.churn_probability -or $result.churn_probability -lt 0 -or $result.churn_probability -gt 1) {
    throw "Prediction check failed: $($result | ConvertTo-Json -Compress)"
}
Write-Host "PREDICT PASS: $($result | ConvertTo-Json -Compress)"

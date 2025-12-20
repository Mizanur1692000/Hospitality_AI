# Quick Individual Tests for KPI Analysis
# Copy and paste these commands one at a time

$headers = @{"Content-Type"="application/json"}

# Test 1: High-Performing Restaurant
Write-Host "`nTest 1: High-Performing Restaurant" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
$body = @{
    total_sales = 25000
    labor_cost = 6250
    food_cost = 5000
    hours_worked = 200
    previous_sales = 24000
} | ConvertTo-Json

# Labor Cost Analysis
Write-Host "`nLabor Cost Analysis:"
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/kpi/labor-cost-analysis/" -Method POST -Headers $headers -Body $body
$response.Content | ConvertFrom-Json | Select-Object -ExpandProperty business_report

# Test 2: Struggling Restaurant
Write-Host "`nTest 2: Struggling Restaurant" -ForegroundColor Red
Write-Host "====================================" -ForegroundColor Red
$body = @{
    total_sales = 12000
    labor_cost = 4800
    food_cost = 4200
    hours_worked = 180
    previous_sales = 13000
} | ConvertTo-Json

# Prime Cost Analysis
Write-Host "`nPrime Cost Analysis:"
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/kpi/prime-cost-analysis/" -Method POST -Headers $headers -Body $body
$response.Content | ConvertFrom-Json | Select-Object -ExpandProperty business_report

# Test 3: Fast Casual Restaurant
Write-Host "`nTest 3: Fast Casual Restaurant" -ForegroundColor Blue
Write-Host "=====================================" -ForegroundColor Blue
$body = @{
    total_sales = 18000
    labor_cost = 3600
    food_cost = 5400
    hours_worked = 120
    previous_sales = 17500
} | ConvertTo-Json

# Sales Performance Analysis
Write-Host "`nSales Performance Analysis:"
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/kpi/sales-performance-analysis/" -Method POST -Headers $headers -Body $body
$response.Content | ConvertFrom-Json | Select-Object -ExpandProperty business_report

Write-Host "`nAll tests completed!" -ForegroundColor Green

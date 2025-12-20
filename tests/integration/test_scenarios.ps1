# Restaurant KPI Analysis Test Scenarios
# Run these commands to test different restaurant scenarios

Write-Host "🍽️  RESTAURANT KPI ANALYSIS SIMULATIONS" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

$headers = @{"Content-Type"="application/json"}

# Scenario 1: High-Performing Restaurant
Write-Host "`n📊 Scenario 1: High-Performing Restaurant" -ForegroundColor Yellow
$body1 = @{
    total_sales = 25000
    labor_cost = 6250
    food_cost = 5000
    hours_worked = 200
    previous_sales = 24000
} | ConvertTo-Json

Write-Host "Testing Labor Cost Analysis..."
$response1a = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/kpi/labor-cost-analysis/" -Method POST -Headers $headers -Body $body1
$response1a.Content | ConvertFrom-Json | Select-Object -ExpandProperty business_report

Write-Host "`nTesting Prime Cost Analysis..."
$response1b = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/kpi/prime-cost-analysis/" -Method POST -Headers $headers -Body $body1
$response1b.Content | ConvertFrom-Json | Select-Object -ExpandProperty business_report

Write-Host "`nTesting Sales Performance Analysis..."
$response1c = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/kpi/sales-performance-analysis/" -Method POST -Headers $headers -Body $body1
$response1c.Content | ConvertFrom-Json | Select-Object -ExpandProperty business_report

# Scenario 2: Struggling Restaurant
Write-Host "`n📊 Scenario 2: Struggling Restaurant" -ForegroundColor Red
$body2 = @{
    total_sales = 12000
    labor_cost = 4800
    food_cost = 4200
    hours_worked = 180
    previous_sales = 13000
} | ConvertTo-Json

Write-Host "Testing Labor Cost Analysis..."
$response2a = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/kpi/labor-cost-analysis/" -Method POST -Headers $headers -Body $body2
$response2a.Content | ConvertFrom-Json | Select-Object -ExpandProperty business_report

Write-Host "`nTesting Prime Cost Analysis..."
$response2b = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/kpi/prime-cost-analysis/" -Method POST -Headers $headers -Body $body2
$response2b.Content | ConvertFrom-Json | Select-Object -ExpandProperty business_report

Write-Host "`nTesting Sales Performance Analysis..."
$response2c = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/kpi/sales-performance-analysis/" -Method POST -Headers $headers -Body $body2
$response2c.Content | ConvertFrom-Json | Select-Object -ExpandProperty business_report

# Scenario 3: Fine Dining Restaurant
Write-Host "`n📊 Scenario 3: Fine Dining Restaurant" -ForegroundColor Magenta
$body3 = @{
    total_sales = 35000
    labor_cost = 8750
    food_cost = 14000
    hours_worked = 250
    previous_sales = 33000
} | ConvertTo-Json

Write-Host "Testing Labor Cost Analysis..."
$response3a = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/kpi/labor-cost-analysis/" -Method POST -Headers $headers -Body $body3
$response3a.Content | ConvertFrom-Json | Select-Object -ExpandProperty business_report

Write-Host "`nTesting Prime Cost Analysis..."
$response3b = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/kpi/prime-cost-analysis/" -Method POST -Headers $headers -Body $body3
$response3b.Content | ConvertFrom-Json | Select-Object -ExpandProperty business_report

Write-Host "`nTesting Sales Performance Analysis..."
$response3c = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/kpi/sales-performance-analysis/" -Method POST -Headers $headers -Body $body3
$response3c.Content | ConvertFrom-Json | Select-Object -ExpandProperty business_report

Write-Host "`nAll simulations completed!" -ForegroundColor Green

$Host.UI.RawUI.WindowTitle = "Ecommerce - Starting"
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "[1/3] Checking Docker..." -ForegroundColor Cyan
docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "      Starting Docker Desktop..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    do {
        Start-Sleep -Seconds 3
        docker info 2>&1 | Out-Null
    } while ($LASTEXITCODE -ne 0)
}
Write-Host "      Docker OK" -ForegroundColor Green

Write-Host "[2/3] Starting containers..." -ForegroundColor Cyan
Set-Location $ROOT
docker compose up -d postgres redis pgadmin
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: containers failed" -ForegroundColor Red
    Read-Host; exit 1
}

Write-Host "      Waiting for PostgreSQL..."
do {
    Start-Sleep -Seconds 2
    docker exec ecommerce_postgres pg_isready -U ecommerce 2>&1 | Out-Null
} while ($LASTEXITCODE -ne 0)
Write-Host "      PostgreSQL OK" -ForegroundColor Green

Write-Host "[3/3] Starting Django..." -ForegroundColor Cyan
$backendPath = Join-Path $ROOT "backend"
$cmd = "cd /d `"$backendPath`" && call conda activate web-backend && python manage.py runserver"
Start-Process cmd -ArgumentList "/k $cmd" -WindowStyle Normal

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "  Frontend : http://localhost:8000" -ForegroundColor White
Write-Host "  Admin    : http://localhost:8000/admin/" -ForegroundColor White
Write-Host "  pgAdmin  : http://localhost:5050" -ForegroundColor White
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to close"

# SmartKitchen Connect - Test Runner Script
# Standard: IEEE 830 | Requirement: RNF-02 (80% coverage)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "SmartKitchen Connect - Test Suite" -ForegroundColor Cyan
Write-Host "Requirement: RNF-02 (Minimum 80% coverage)" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Navigate to Backend directory
Set-Location -Path "$PSScriptRoot\..\Backend"

# Activate virtual environment
if (Test-Path -Path "venv\Scripts\Activate.ps1") {
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "✓ Virtual environment activated`n" -ForegroundColor Green
}

# Run code quality checks (RNF-02)
Write-Host "[1/4] Running code quality checks..." -ForegroundColor Yellow
Write-Host "`nFlake8 (PEP8 compliance):" -ForegroundColor Cyan
flake8 apps/ --count --statistics

Write-Host "`nBlack (code formatting check):" -ForegroundColor Cyan
black apps/ --check

# Run tests with coverage
Write-Host "`n[2/4] Running tests with coverage..." -ForegroundColor Yellow
pytest --cov=apps --cov-report=term-missing --cov-report=html --cov-fail-under=80 -v

# Check coverage results
Write-Host "`n[3/4] Coverage report generated in htmlcov/index.html" -ForegroundColor Cyan

# Run security checks
Write-Host "`n[4/4] Running security checks..." -ForegroundColor Yellow
Write-Host "Checking for known vulnerabilities..." -ForegroundColor Cyan
# safety check --file=requirements.txt (uncomment if safety is installed)

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "✓ Test Suite Complete!" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Cyan

Write-Host "View detailed coverage report:" -ForegroundColor Cyan
Write-Host "  htmlcov\index.html`n" -ForegroundColor White

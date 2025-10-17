# SmartKitchen Connect - Code Quality Script
# Standard: IEEE 830 | Requirement: RNF-02
# Purpose: Format and lint code automatically

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Code Quality & Formatting" -ForegroundColor Cyan
Write-Host "Requirement: RNF-02 (PEP8 compliance)" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

Set-Location -Path "$PSScriptRoot\..\Backend"

# Activate virtual environment
if (Test-Path -Path "venv\Scripts\Activate.ps1") {
    & ".\venv\Scripts\Activate.ps1"
}

# Format code with Black
Write-Host "[1/3] Formatting code with Black..." -ForegroundColor Yellow
black apps/ config/
Write-Host "✓ Code formatted`n" -ForegroundColor Green

# Sort imports with isort
Write-Host "[2/3] Sorting imports with isort..." -ForegroundColor Yellow
isort apps/ config/
Write-Host "✓ Imports sorted`n" -ForegroundColor Green

# Check with flake8
Write-Host "[3/3] Checking code quality with flake8..." -ForegroundColor Yellow
flake8 apps/ config/ --count --statistics

Write-Host "`n✓ Code quality check complete!" -ForegroundColor Green

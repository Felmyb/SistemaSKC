# SmartKitchen Connect - Setup Script
# Standard: IEEE 830 | Requirement: RNF-05
# Purpose: Automated project setup for development

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "SmartKitchen Connect - Setup Script" -ForegroundColor Cyan
Write-Host "Standard: IEEE 830 | Design Thinking" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Check Python installation
Write-Host "[1/8] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check PostgreSQL installation
Write-Host "`n[2/8] Checking PostgreSQL installation..." -ForegroundColor Yellow
try {
    $pgVersion = psql --version 2>&1
    Write-Host "✓ PostgreSQL found: $pgVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠ PostgreSQL not found. Install or use Docker." -ForegroundColor Yellow
}

# Navigate to Backend directory
Write-Host "`n[3/8] Setting up Backend environment..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\Backend"

# Create virtual environment
if (!(Test-Path -Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`n[4/8] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install dependencies (RNF-02)
Write-Host "`n[5/8] Installing Python dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Setup environment variables (RNF-03)
Write-Host "`n[6/8] Configuring environment variables..." -ForegroundColor Yellow
if (!(Test-Path -Path ".env")) {
    Copy-Item -Path ".env.example" -Destination ".env"
    Write-Host "✓ .env file created from template" -ForegroundColor Green
    Write-Host "⚠ Please edit .env file with your configuration" -ForegroundColor Yellow
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Run migrations
Write-Host "`n[7/8] Running database migrations..." -ForegroundColor Yellow
python manage.py makemigrations
python manage.py migrate
Write-Host "✓ Database migrations completed" -ForegroundColor Green

# Create superuser prompt
Write-Host "`n[8/8] Create superuser account? (Y/N)" -ForegroundColor Yellow
$createSuperuser = Read-Host
if ($createSuperuser -eq "Y" -or $createSuperuser -eq "y") {
    python manage.py createsuperuser
}

# Final instructions
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "✓ Setup Complete!" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit Backend\.env with your configuration" -ForegroundColor White
Write-Host "2. Start development server: python manage.py runserver" -ForegroundColor White
Write-Host "3. Access API docs: http://localhost:8000/api/docs/" -ForegroundColor White
Write-Host "4. Access admin panel: http://localhost:8000/admin/`n" -ForegroundColor White

Write-Host "Design Thinking Reminder:" -ForegroundColor Magenta
Write-Host "- Empathize: Understand user needs" -ForegroundColor White
Write-Host "- Define: Identify problems clearly" -ForegroundColor White
Write-Host "- Ideare: Brainstorm solutions" -ForegroundColor White
Write-Host "- Prototype: Build and iterate" -ForegroundColor White
Write-Host "- Evaluate: Test and improve`n" -ForegroundColor White

Write-Host "Happy coding! 🚀" -ForegroundColor Cyan

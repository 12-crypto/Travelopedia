# Travelopedia AI Travel Planner - Windows PowerShell Runner
# This script sets up the environment and runs the Streamlit application

Write-Host "🌍 Travelopedia AI Travel Planner - Setup & Run" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.9+ from python.org" -ForegroundColor Red
    exit 1
}

# Check Python version
$versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
if ($versionMatch) {
    $major = [int]$Matches[1]
    $minor = [int]$Matches[2]
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 9)) {
        Write-Host "✗ Python 3.9+ required. Found: $pythonVersion" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠ .env file not found!" -ForegroundColor Yellow
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠ IMPORTANT: Please edit .env file and add your API keys:" -ForegroundColor Yellow
    Write-Host "  - SERPAPI_API_KEY (required for flights/hotels)" -ForegroundColor Yellow
    Write-Host "  - OPENWEATHER_API_KEY (optional for weather)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to continue after updating .env file..." -ForegroundColor Cyan
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
} else {
    Write-Host "✓ .env file found" -ForegroundColor Green
}

Write-Host ""

# Install/upgrade dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
Write-Host "(This may take a few minutes on first run)" -ForegroundColor Gray
Write-Host ""

pip install --upgrade pip | Out-Null
pip install -r requirements.txt

Write-Host ""
Write-Host "✓ Dependencies installed" -ForegroundColor Green

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "🚀 Starting Travelopedia AI Travel Planner..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The app will open in your browser at:" -ForegroundColor Yellow
Write-Host "http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Run Streamlit app
streamlit run frontend/app.py

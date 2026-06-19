# aQuickRescue - Setup & Installation Script (PowerShell)
# Initializes the entire project

$ErrorActionPreference = "Stop"

Write-Host "[SETUP] aQuickRescue - Full Stack Setup" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check Node.js
Write-Host "[+] Checking Node.js version..." -ForegroundColor Yellow
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeCmd) {
    Write-Host "[ERROR] Node.js not found. Please install Node.js >= 18.0.0" -ForegroundColor Red
    exit 1
} else {
    $nodeVersion = (& node -v) 2>&1
    if ($nodeVersion) { $nodeVersion = $nodeVersion.Trim() }
    Write-Host "[OK] Node.js $nodeVersion found" -ForegroundColor Green
}
Write-Host ""

# Check npm
Write-Host "[+] Checking npm version..." -ForegroundColor Yellow
$npmCmd = Get-Command npm -ErrorAction SilentlyContinue
if (-not $npmCmd) {
    Write-Host "[ERROR] npm not found. Please install Node.js/npm >= 8.0.0" -ForegroundColor Red
    exit 1
} else {
    $npmVersion = (& npm -v) 2>&1
    if ($npmVersion) { $npmVersion = $npmVersion.Trim() }
    Write-Host "[OK] npm $npmVersion found" -ForegroundColor Green
}
Write-Host ""

# Check Python (optional)
Write-Host "[+] Checking Python version..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[WARNING] Python not found. Backend setup may require manual installation." -ForegroundColor Yellow
    $pythonVersion = $null
} else {
    $pythonVersion = (& python --version) 2>&1
    if ($pythonVersion) { $pythonVersion = $pythonVersion.Trim() }
    Write-Host "[OK] $pythonVersion found" -ForegroundColor Green
}
Write-Host ""

# Install Frontend Dependencies
Write-Host "[*] Installing Frontend dependencies..." -ForegroundColor Yellow
& npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] npm install failed at project root. Please check your npm configuration." -ForegroundColor Red
    exit $LASTEXITCODE
}

# Try installing workspaces explicitly (harmless if workspaces not used)
& npm install --workspace=frontend
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] npm install --workspace=frontend failed." -ForegroundColor Red
    exit $LASTEXITCODE
}
& npm install --workspace=shared
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] npm install --workspace=shared failed." -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host "[OK] Frontend dependencies installed" -ForegroundColor Green
Write-Host ""

# Install Backend Dependencies (if python available)
Write-Host "[*] Installing Backend dependencies..." -ForegroundColor Yellow
if ($pythonVersion) {
    & python -m pip install -r backend/requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to install backend Python dependencies. Run 'python -m pip install -r backend/requirements.txt' manually." -ForegroundColor Red
        exit $LASTEXITCODE
    } else {
        Write-Host "[OK] Backend dependencies installed" -ForegroundColor Green
    }
} else {
    Write-Host "[WARNING] Skipping backend dependencies - Python not found" -ForegroundColor Yellow
}
Write-Host ""

# Setup Environment Files
Write-Host "[*] Setting up environment files..." -ForegroundColor Yellow
if (!(Test-Path ".env.local")) {
    if (Test-Path ".env.example") { Copy-Item ".env.example" ".env.local" -Force }
}
if (!(Test-Path "frontend/.env.local")) {
    if (Test-Path "frontend/.env.example") { Copy-Item "frontend/.env.example" "frontend/.env.local" -Force }
}
Write-Host "[OK] Environment files configured" -ForegroundColor Green
Write-Host ""

# Build Frontend
Write-Host "[*] Building frontend (workspace: frontend)..." -ForegroundColor Yellow
& npm run build --workspace=frontend
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Frontend build failed. Check the log above for details." -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host "[OK] Frontend built" -ForegroundColor Green
Write-Host ""

Write-Host ""
Write-Host "[COMPLETE] Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "[INFO] Next Steps:" -ForegroundColor Cyan
Write-Host "1. Start the development server:" -ForegroundColor White
Write-Host "   npm run dev --workspace=frontend"
Write-Host ""
Write-Host "2. In another terminal, start the backend:" -ForegroundColor White
Write-Host "   cd backend"
Write-Host "   python -m uvicorn app.main:app --reload"
Write-Host ""
Write-Host "3. Open browser:" -ForegroundColor White
Write-Host "   http://localhost:5173"
Write-Host ""
Write-Host "Demo Credentials:" -ForegroundColor Yellow
Write-Host "  Responder: responder1 / password123"
Write-Host "  Patient: patient1 / password123"
Write-Host "  Admin: admin1 / password123"
Write-Host ""
Write-Host "[*] Documentation:" -ForegroundColor Cyan
Write-Host "  Frontend: frontend/README.md"
Write-Host "  Backend: backend/README.md"
Write-Host "  API: docs/API.md"
Write-Host ""
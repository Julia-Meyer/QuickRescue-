# aQuickRescue - Setup & Installation Script (PowerShell)
# Initialisiert das gesamte Projekt

$ErrorActionPreference = "Stop"

Write-Host "🚀 aQuickRescue - Full Stack Setup" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check Node.js
Write-Host "✓ Checking Node.js version..." -ForegroundColor Yellow
$nodeVersion = node -v 2>$null
if (!$nodeVersion) {
    Write-Host "❌ Node.js not found. Please install Node.js >= 18.0.0" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Node.js $nodeVersion found" -ForegroundColor Green
Write-Host ""

# Check Python
Write-Host "✓ Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>$null
if (!$pythonVersion) {
    Write-Host "❌ Python not found. Please install Python >= 3.11" -ForegroundColor Red
    exit 1
}
Write-Host "✅ $pythonVersion found" -ForegroundColor Green
Write-Host ""

# Install Frontend Dependencies
Write-Host "📦 Installing Frontend dependencies..." -ForegroundColor Yellow
npm install
npm install --workspace=packages/frontend
npm install --workspace=packages/shared
Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
Write-Host ""

# Install Backend Dependencies
Write-Host "📦 Installing Backend dependencies..." -ForegroundColor Yellow
pip install -r packages/backend/requirements.txt
Write-Host "✅ Backend dependencies installed" -ForegroundColor Green
Write-Host ""

# Setup Environment Files
Write-Host "⚙️  Setting up environment files..." -ForegroundColor Yellow
if (!(Test-Path ".env.local")) {
    Copy-Item ".env.example" ".env.local" -ErrorAction SilentlyContinue
}
if (!(Test-Path "packages/frontend/.env.local")) {
    Copy-Item "packages/frontend/.env.example" "packages/frontend/.env.local" -ErrorAction SilentlyContinue
}
Write-Host "✅ Environment files configured" -ForegroundColor Green
Write-Host ""

# Build Packages
Write-Host "🔨 Building packages..." -ForegroundColor Yellow
npm run build
Write-Host "✅ Packages built" -ForegroundColor Green
Write-Host ""

Write-Host ""
Write-Host "✨ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Start the development server:" -ForegroundColor White
Write-Host "   npm run dev --workspace=packages/frontend"
Write-Host ""
Write-Host "2. In another terminal, start the backend:" -ForegroundColor White
Write-Host "   cd packages/backend"
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
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "  Frontend: packages/frontend/README.md"
Write-Host "  Backend: packages/backend/README.md"
Write-Host "  API: docs/API.md"
Write-Host ""


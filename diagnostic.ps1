#!/usr/bin/env pwsh
# Quick Rescue - Diagnostic Script
# Checks frontend, backend, and provides fixes

Write-Host "🔍 aQuickRescue System Diagnostic" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check frontend
Write-Host "📱 Frontend Check:" -ForegroundColor Yellow
$frontendRunning = Test-NetConnection -ComputerName 127.0.0.1 -Port 5173 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($frontendRunning) {
    Write-Host "  ✓ Frontend server is running on port 5173" -ForegroundColor Green
    Write-Host "  📍 URL: http://localhost:5173" -ForegroundColor Green
} else {
    Write-Host "  ✗ Frontend server NOT running on port 5173" -ForegroundColor Red
    Write-Host "  💡 To fix, run: npm run dev --workspace=frontend" -ForegroundColor Yellow
}

Write-Host ""

# Check backend
Write-Host "⚙️  Backend Check:" -ForegroundColor Yellow
$backendRunning = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($backendRunning) {
    Write-Host "  ✓ Backend server is running on port 8000" -ForegroundColor Green
    Write-Host "  📍 URL: http://localhost:8000" -ForegroundColor Green
    Write-Host "  📖 API Docs: http://localhost:8000/docs" -ForegroundColor Green
} else {
    Write-Host "  ✗ Backend server NOT running on port 8000" -ForegroundColor Red
    Write-Host "  💡 To fix, run: cd backend && python -m uvicorn app.main:app --reload" -ForegroundColor Yellow
}

Write-Host ""

# Check Node processes
Write-Host "⚡ Node Processes:" -ForegroundColor Yellow
$nodeProcs = Get-Process node -ErrorAction SilentlyContinue
if ($nodeProcs) {
    Write-Host "  ✓ Node.js processes running:" -ForegroundColor Green
    $nodeProcs | ForEach-Object { Write-Host "    - PID: $($_.Id), Started: $($_.StartTime)" }
} else {
    Write-Host "  ✗ No Node.js processes found" -ForegroundColor Red
}

Write-Host ""

# Summary
Write-Host "📊 Summary:" -ForegroundColor Cyan
if ($frontendRunning -and $backendRunning) {
    Write-Host "  ✓ Both frontend and backend are running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Next Steps:" -ForegroundColor Green
    Write-Host "  1. Open browser: http://localhost:5173" -ForegroundColor White
    Write-Host "  2. If empty page, open DevTools (F12) → Console tab" -ForegroundColor White
    Write-Host "  3. Copy any error messages and paste here" -ForegroundColor White
} elseif ($frontendRunning) {
    Write-Host "  ⚠️  Frontend running, but backend is NOT responding" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🔧 Fix backend:" -ForegroundColor Yellow
    Write-Host "  cd C:\Users\patap\PycharmProjects\QuickRescue-\backend" -ForegroundColor White
    Write-Host "  python -m uvicorn app.main:app --reload" -ForegroundColor White
} elseif ($backendRunning) {
    Write-Host "  ⚠️  Backend running, but frontend is NOT responding" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🔧 Fix frontend:" -ForegroundColor Yellow
    Write-Host "  cd C:\Users\patap\PycharmProjects\QuickRescue-\frontend" -ForegroundColor White
    Write-Host "  npm run dev" -ForegroundColor White
} else {
    Write-Host "  ✗ Both frontend and backend are down" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Start both services:" -ForegroundColor Red
    Write-Host "  Terminal 1 (frontend):" -ForegroundColor White
    Write-Host "    cd C:\Users\patap\PycharmProjects\QuickRescue-\frontend && npm run dev" -ForegroundColor Yellow
    Write-Host "  Terminal 2 (backend):" -ForegroundColor White
    Write-Host "    cd C:\Users\patap\PycharmProjects\QuickRescue-\backend && python -m uvicorn app.main:app --reload" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "💡 Need help? Check QUICK_START_DEMO.md" -ForegroundColor Cyan


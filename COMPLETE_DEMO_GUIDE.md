# 🏥 aQuickRescue - Complete Demo & Troubleshooting Guide

**Status**: ✅ Working  
**Date**: June 17, 2026  
**Version**: 0.1.0  

---

## 📌 TL;DR - Get Started in 60 Seconds

```powershell
# 1. Open browser
http://localhost:5173

# 2. Login with
Username: patient1
Password: password123

# 3. You're done! 🎉
```

---

## 🔧 What Was Broken & How We Fixed It

### The Problem
- **Symptom**: Empty white page at `http://localhost:5173`
- **Root Cause**: WebAssembly (WASM) asset not properly configured in Vite
- **Impact**: Frontend app crashed during initialization (sql.js couldn't load)

### The Solution
**File Modified**: `frontend/vite.config.js`

**What Changed**:
```javascript
// Added this line to the Vite configuration:
assetsInclude: ['**/*.wasm'],
```

**Why It Works**:
- Frontend uses **sql.js** (SQLite running in JavaScript)
- sql.js requires a `.wasm` file (WebAssembly binary) to function
- Without `assetsInclude`, Vite wasn't properly serving the WASM file
- Now Vite correctly handles WASM files as binary assets
- Frontend initializes successfully → Database loads → App renders

---

## 🚀 Running the Demo

### Terminal 1: Frontend Dev Server (Already Running ✓)

```powershell
cd C:\Users\patap\PycharmProjects\QuickRescue-\frontend
npm run dev
```

**Output should show**:
```
  VITE v8.0.16 ready in 152 ms

  ➜  Local:   https://localhost:5173/
  ➜  Local:   https://localhost.localdomain:5173/
```

### Terminal 2: Backend API Server (Optional - for full features)

```powershell
cd C:\Users\patap\PycharmProjects\QuickRescue-\backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Output should show**:
```
Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## 🌐 Accessing the Application

### Frontend
- **HTTP**: `http://localhost:5173` (works, but may show SSL warning)
- **HTTPS**: `https://localhost:5173` (recommended)

### Backend
- **API Base**: `http://localhost:8000`
- **API Docs (Swagger)**: `http://localhost:8000/docs`
- **Alternative Docs (ReDoc)**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

---

## 👤 Demo Accounts

### Patient Account
- **Username**: `patient1`
- **Password**: `password123`
- **Role**: Patient
- **Access**: View own medical records, enable emergency access

### First Responder Account
- **Username**: `responder1`
- **Password**: `password123`
- **Role**: First Responder / Emergency Physician
- **Access**: Search patients, view emergency data, access history

### Admin Account
- **Username**: `admin1`
- **Password**: `password123`
- **Role**: Administrator
- **Access**: Manage users, system configuration, audit logs

---

## 📊 What to Test

### 1. **Login Flow**
```
1. Open http://localhost:5173
2. See login page with form
3. Enter: patient1 / password123
4. Click "Anmelden" (Sign In)
5. Should redirect to dashboard
```

### 2. **Dashboard**
```
After login, you should see:
- Header with user info and logout button
- Navigation menu
- Main content area showing patient dashboard
- Footer with version info
```

### 3. **Role-Based Navigation**
```
As Responder (responder1):
- Should see "🔍 Patient suchen" (Search Patient)
- Should see "🚨 Notfallzugriff" (Emergency Access)

As Patient (patient1):
- Should see dashboard with medical records
- Should see emergency access settings
```

### 4. **API Integration**
```
Visit: http://localhost:8000/docs
- Try GET /health endpoint
- Try POST /api/v1/auth/login with credentials
- Explore all available endpoints
```

---

## 🐛 Troubleshooting

### Issue: Still Seeing Empty Page

**Step 1: Hard Refresh Browser**
```
Windows/Linux: Ctrl + Shift + R
Mac: Cmd + Shift + R
```

**Step 2: Check Browser Console**
```
1. Press F12 (or right-click → Inspect)
2. Go to Console tab
3. Look for error messages
4. Copy any RED error text
```

**Step 3: Check Network Tab**
```
1. In DevTools, go to Network tab
2. Press F5 to reload
3. Look for failed requests (red ❌)
4. Check if index.html returns 200
```

**Step 4: Verify Server is Running**
```powershell
# Check frontend
netstat -ano | findstr 5173
# Should show: TCP    [::1]:5173   [::]:0   LISTENING

# Check backend
netstat -ano | findstr 8000
# Should show: TCP    127.0.0.1:8000   0.0.0.0:0   LISTENING
```

---

### Issue: Login Fails with 401/403

**Cause**: Backend not running or incorrect credentials

**Fix**:
```powershell
# 1. Check backend is running on port 8000
Test-NetConnection -ComputerName 127.0.0.1 -Port 8000

# 2. If not running, start it:
cd backend
python -m uvicorn app.main:app --reload

# 3. Try login again
# Make sure you're using correct credentials:
# - patient1 / password123
# - responder1 / password123
```

---

### Issue: "Cannot GET /api/v1/auth/login"

**Cause**: Backend API not accessible or running on wrong port

**Fix**:
```powershell
# Check backend health
(Invoke-WebRequest http://localhost:8000/health -UseBasicParsing).Content

# Should return:
{"status":"healthy"}

# If error, restart backend:
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

### Issue: "sql.js WASM Error" or "Cannot find sql-wasm-browser.wasm"

**Cause**: Vite configuration was missing WASM support (this should be fixed now)

**Fix**:
```javascript
// vite.config.js should have:
assetsInclude: ['**/*.wasm'],

// If missing, add it and restart:
npm run dev
```

---

## 🔍 Browser DevTools Guide

### Console Tab
**Expected Output When Loading**:
```
[App] Initializing aQuickRescue Frontend v0.1.0
[App] Initializing local database...
[DB] Loaded database from IndexedDB
[App] Setting up authentication...
[Auth] No existing auth session
[App] Setting up router...
[App] Mounting application...
[App] ✓ aQuickRescue Frontend ready
```

**Bad Signs** (Red errors like):
- `Uncaught ReferenceError: Cannot find module`
- `Failed to load module script`
- `Uncaught TypeError: sql.js is undefined`

### Network Tab
**What to Check**:
- `index.html` → Status should be **200** (not 404 or 500)
- `.js` files → Status should be **200** (not 404 or HTML response)
- `.wasm` files → Status should be **200** with type `application/wasm`
- API requests → `/api/auth/login` should return **200** with JWT token

### Application Tab
**Local Storage**:
- After login, should have:
  - `aQuickRescue_token` (JWT token)
  - `aQuickRescue_user` (user object JSON)

**IndexedDB**:
- Database name: `aQuickRescue`
- Should contain tables: `metadata`, `patients`, `images`, `audit_cache`

---

## 🔐 Authentication Flow

```
1. User enters credentials on login form
2. Frontend sends POST /api/v1/auth/login to backend
3. Backend validates and returns JWT token
4. Frontend stores token in localStorage
5. Frontend stores user info in localStorage
6. Frontend redirects to /dashboard
7. Subsequent API calls include token in Authorization header:
   Authorization: Bearer <JWT_TOKEN>
8. Backend validates token and returns data
9. Frontend renders dashboard based on user role
```

---

## 📚 Architecture Overview

```
┌─────────────────────────────────────┐
│     Browser (http://localhost:5173) │
├────────────────────────────────��────┤
│                                     │
│  Frontend (Vite + Vanilla JS)      │
│  ├── Pages (Login, Dashboard, etc) │
│  ├── Components (Header, Footer)   │
│  ├── Services                      │
│  │   ├── api.js (← backend)        │
│  │   ├── auth.js (JWT)             │
│  │   └── db.js (SQLite via sql.js) │
│  ├── State (Zustand store)         │
│  └── Styles (CSS)                  │
│                                     │
└─────────────────────────────────────┘
          ↓ (HTTP/HTTPS)
┌─────────────────────────────────────┐
│  Backend (FastAPI, Port 8000)       │
├─────────────────────────────────────┤
│                                     │
│  FastAPI Application                │
│  ├── /api/auth (login, register)   │
│  ├── /api/patients (patient data)  │
│  ├── /api/audit (access logs)      │
│  ├── Services (FHIR, etc)          │
│  └── Database (SQLite/PostgreSQL)  │
│                                     │
└──────────────────��──────────────────┘
```

---

## 🎯 Common Test Scenarios

### Scenario 1: Patient Workflow
```
1. Login as patient1
2. View dashboard showing medical records
3. Check allergies section
4. Check medications section
5. View emergency contact info
6. Enable/disable emergency access
7. Check audit trail
8. Logout
```

### Scenario 2: First Responder Workflow
```
1. Login as responder1
2. See emergency responder dashboard
3. Search for a patient (e.g., "patient1")
4. Click "Emergency Access" button
5. View patient's critical data (allergies, medications)
6. See automatic audit log entry
7. Navigate to Audit Trail
8. Confirm access is logged
9. Logout
```

### Scenario 3: API Testing (Postman/curl)
```powershell
# 1. Get health status
curl http://localhost:8000/health

# 2. Login and get token
$loginBody = @{
    username = "patient1"
    password = "password123"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $loginBody

$token = ($response.Content | ConvertFrom-Json).access_token

# 3. Use token to fetch patient data
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/patients/1" `
    -Headers @{"Authorization"="Bearer $token"}
```

---

## 📝 Development Commands

### Frontend Commands
```bash
# Start dev server (hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Lint code
npm run lint

# Fix linting issues
npm run lint:fix

# Format code with Prettier
npm run format
```

### Backend Commands
```bash
# Start dev server (auto-reload)
python -m uvicorn app.main:app --reload

# Run tests
pytest

# Run with coverage
pytest --cov=app

# Format code (Black)
black backend/

# Lint code (Flake8)
flake8 backend/

# Type checking (mypy)
mypy app/

# Security scan (Bandit)
bandit -r app/
```

---

## 🐳 Docker Setup (Alternative)

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## ✅ Final Checklist

Before declaring demo ready:

- [ ] Frontend loads at http://localhost:5173
- [ ] Login page displays correctly
- [ ] Can login with patient1 / password123
- [ ] Dashboard appears after login
- [ ] Header shows user name and role
- [ ] Can logout successfully
- [ ] Backend responds to health check
- [ ] API docs available at http://localhost:8000/docs
- [ ] No error messages in browser console
- [ ] Network tab shows no 404 errors
- [ ] Can login with responder1 account
- [ ] Responder can search patients
- [ ] Audit trail is accessible
- [ ] No WASM or module loading errors

---

## 📞 Support & Debugging

### Enable Debug Logging
```javascript
// In browser console:
localStorage.setItem('DEBUG_MODE', 'true')
location.reload()
```

### Check Local Storage
```javascript
// In browser console:
console.table(localStorage)
// Shows all stored data
```

### Check IndexedDB
```javascript
// Open DevTools → Application → IndexedDB → aQuickRescue
// View tables: metadata, patients, images, audit_cache
```

### Backend Logs
```bash
# When running backend locally, errors print to console
# Watch for:
# - [ERROR] messages
# - Database connection issues
# - Authentication failures
```

---

## 🎓 Understanding the Architecture

### Frontend Stack
- **Bundler**: Vite (instant HMR, super fast)
- **Language**: Vanilla JavaScript (ES6+)
- **State**: Zustand (lightweight store)
- **HTTP**: Axios (request library)
- **Database**: sql.js (SQLite in browser)
- **Styling**: CSS (custom, no framework)

### Backend Stack
- **Framework**: FastAPI (async, fast, modern)
- **Server**: Uvicorn (ASGI)
- **Database**: SQLite + PostgreSQL support
- **Authentication**: OAuth2 + JWT
- **Data Validation**: Pydantic

### Key Features
- FHIR-compliant healthcare data format
- SNOMED-CT integration for medical terms
- Audit logging for compliance
- Offline-first approach (frontend works offline)
- Real-time sync when online

---

**Version**: 0.1.0  
**Status**: ✅ Demo Ready  
**Last Updated**: June 17, 2026  

Happy testing! 🚀



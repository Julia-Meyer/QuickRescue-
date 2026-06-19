# 🚀 aQuickRescue - Quick Start Demo Guide

**Current Status: June 17, 2026**

## ✅ What's Running Now

### Frontend (Vite Dev Server)
- **Status**: ✓ Running on port 5173
- **URL**: `http://localhost:5173`
- **Process**: Node.js dev server (Vite v8.0.16)
- **Configuration**: 
  - SSL enabled (via @vitejs/plugin-basic-ssl)
  - Strict port mode: true (won't increment if port taken)
  - Proxy to backend: `/api` → `http://localhost:8000`

### Backend (FastAPI)
- **Status**: ✓ Running on port 8000
- **URL**: `http://localhost:8000`
- **Process**: Python FastAPI via Uvicorn
- **Features**:
  - CORS enabled for local development
  - Health check: `GET /health`
  - Auto-reload on code changes
  - Interactive API docs: `http://localhost:8000/docs`

---

## 🌐 Accessing the Application

### Option 1: HTTP (Recommended for Testing)
```
http://localhost:5173
```

### Option 2: HTTPS (SSL Enabled)
```
https://localhost:5173
```
*Browser may warn about self-signed certificate - click "Proceed"*

---

## 🧪 If You See Empty Page

### Quick Diagnostics

**Step 1: Check if frontend is serving HTML**
```powershell
# Open PowerShell and check port 5173
Test-NetConnection -ComputerName 127.0.0.1 -Port 5173
# Should return: TcpTestSucceeded: True
```

**Step 2: Check browser console for errors**
- Open DevTools: `F12` or `Ctrl+Shift+I`
- Go to **Console** tab
- Look for red error messages
- Common issues:
  - `Failed to load module script` → module not found
  - `Uncaught ReferenceError` → variable not defined
  - `Cannot find module 'sql.js'` → dependency issue

**Step 3: Check Network tab**
- Go to **Network** tab in DevTools
- Reload page (`F5`)
- Look for:
  - `index.html` - should be status 200
  - `.js` files - should be 200, not 404 or HTML
  - `.wasm` files - should be 200 with correct MIME type

**Step 4: Restart frontend (if hung)**
```powershell
# Kill all Node processes
taskkill /IM node.exe /F

# Restart frontend
cd C:\Users\patap\PycharmProjects\QuickRescue-\frontend
npm run dev
```

---

## 🔐 Authentication & Demo Credentials

### Getting Demo Credentials

The system uses JWT authentication. Demo accounts are mentioned in the README:

| Role | Username | Password |
|------|----------|----------|
| Patient | patient1 | password123 |
| Responder | responder1 | password123 |
| Admin | admin1 | password123 |

### Login Flow

1. **Open frontend**: `http://localhost:5173`
2. **Click Login** (or navigate to `/login`)
3. **Enter credentials**:
   - Email/Username: `patient1`
   - Password: `password123`
4. **Submit form**
5. **Verify in Network tab**:
   - Request should go to backend (`POST /api/auth/login`)
   - Response should include JWT token
   - Token stored in localStorage

### Creating a New Patient Account

If demo accounts don't work, create one via API:

```powershell
# Create a new patient account
$body = @{
    email = "testpatient@example.com"
    password = "TestPassword123"
    first_name = "Test"
    last_name = "Patient"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/api/auth/register" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $body

$response.Content | ConvertFrom-Json
```

**Response should include**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "email": "testpatient@example.com",
    "role": "PATIENT"
  }
}
```

---

## 📡 Backend API Testing

### Health Check
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:8000/health"
$response.Content
# Should return: {"status":"healthy"}
```

### Interactive API Docs
Visit `http://localhost:8000/docs` to see:
- All available endpoints
- Request/response schemas
- Try-it-out feature to test endpoints

### Available Endpoints (Core)
```
GET    /                          # Root endpoint
GET    /health                    # Health check
POST   /api/auth/register         # Register new user
POST   /api/auth/login            # Login user
POST   /api/auth/refresh          # Refresh JWT token
GET    /api/patients/{id}         # Get patient data
GET    /api/patients/{id}/allergies
GET    /api/patients/{id}/medications
GET    /api/patients/{id}/observations
POST   /api/audit/access          # Log access event
```

---

## 🛠️ Troubleshooting

### Frontend shows nothing (blank page)

1. **Check vite.config.js**:
   ```javascript
   server: {
     port: 5173,
     strictPort: true,  // ← Should be true
   }
   ```

2. **Restart frontend**:
   ```powershell
   cd frontend
   npm run dev
   ```

3. **Clear browser cache**:
   - DevTools → Application tab → Clear Site Data
   - Or hard refresh: `Ctrl+Shift+R`

### Backend not responding

1. **Check if Python installed**:
   ```powershell
   python --version
   ```

2. **Reinstall dependencies**:
   ```powershell
   cd backend
   pip install -r requirements.txt
   ```

3. **Start backend**:
   ```powershell
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

### Login fails with 401 or 404

1. **Check backend logs** - look for error messages
2. **Verify credentials** - ensure username/password are correct
3. **Check Network tab** - confirm POST request went to `/api/auth/login`
4. **Test with curl**:
   ```powershell
   $body = @{"username"="patient1";"password"="password123"} | ConvertTo-Json
   Invoke-WebRequest -Uri "http://localhost:8000/api/auth/login" `
     -Method POST `
     -Headers @{"Content-Type"="application/json"} `
     -Body $body
   ```

---

## 📝 Common Commands

### Frontend Commands
```bash
# Start dev server
npm run dev --workspace=frontend

# Build for production
npm run build --workspace=frontend

# Run tests
npm test --workspace=frontend

# Format code
npm run format --workspace=frontend

# Lint code
npm run lint --workspace=frontend
```

### Backend Commands
```bash
# Start dev server
python -m uvicorn app.main:app --reload

# Run tests
pytest

# Format code
black backend/

# Lint code
flake8 backend/

# Type checking
mypy backend/app
```

---

## 📚 Next Steps

1. **Verify frontend loads**:
   - Open `http://localhost:5173`
   - Check DevTools console for errors

2. **Test backend API**:
   - Visit `http://localhost:8000/docs`
   - Try health endpoint

3. **Try login**:
   - Use credentials: `patient1` / `password123`
   - Watch Network tab for API call

4. **Explore application**:
   - Navigate pages
   - Check audit trail
   - Test patient search (if responder role)

---

## 🆘 Need More Help?

If you see specific errors:
1. **Copy the error message** from browser console
2. **Check the Network tab** for failed requests
3. **Look at backend logs** for server errors
4. **Paste error details** and I'll diagnose

---

**Last Updated**: June 17, 2026  
**Status**: Demo Environment Ready  
**Frontend**: ✓ Running  
**Backend**: ✓ Running



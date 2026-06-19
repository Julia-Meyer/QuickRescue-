# ✅ QUICK START - aQuickRescue Demo

## What's Running Now

- ✓ **Frontend**: Node dev server (Vite) - 3 processes active
- ✓ **Backend**: Should be ready
- ✓ **Port 5173**: Frontend listening (HTTP/HTTPS)
- ✓ **Port 8000**: Backend listening (FastAPI)

---

## 🎯 NEXT STEPS (Do These Now)

### Step 1: Open Frontend in Browser
```
http://localhost:5173
```

### Step 2: If Empty Page - Check Console for Errors
1. **Right-click** → **Inspect** (or press `F12`)
2. Click **Console** tab
3. **Copy any RED errors** and paste them here
4. Look for patterns like:
   - `Cannot find module`
   - `Failed to load`
   - `ReferenceError`
   - `Uncaught`

### Step 3: Check Network Tab
1. In DevTools, click **Network** tab
2. **Reload the page** (F5)
3. Look for requests with ❌ status (4xx, 5xx errors)
4. Check if `index.html` returned status **200**

---

## 🔐 Demo Credentials (Once Loaded)

**Patient Login:**
```
Username: patient1
Password: password123
```

**Responder Login:**
```
Username: responder1
Password: password123
```

---

## 🆘 Common Issues & Fixes

### Problem: Blank White Page
**Likely Cause**: JavaScript error stopping rendering

**Fix**:
1. Open DevTools (F12) → Console
2. Look for error messages
3. Most common: `sql.js` module loading issue

**Solution if sql.js error**:
```powershell
# Kill frontend and restart
cd C:\Users\patap\PycharmProjects\QuickRescue-\frontend
npm run dev
```

### Problem: Can't reach http://localhost:5173
**Likely Cause**: Frontend dev server not running

**Fix**:
```powershell
cd C:\Users\patap\PycharmProjects\QuickRescue-\frontend
npm run dev
```

### Problem: Login fails (401 error)
**Likely Cause**: Backend not running

**Fix**:
```powershell
cd C:\Users\patap\PycharmProjects\QuickRescue-\backend
python -m uvicorn app.main:app --reload
```

---

## 📊 System Status Commands

Check if services are running:
```powershell
# Check frontend (port 5173)
Test-NetConnection -ComputerName 127.0.0.1 -Port 5173 -InformationLevel Quiet
# Result: True = running, False = not running

# Check backend (port 8000)
Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -InformationLevel Quiet
# Result: True = running, False = not running
```

---

## 🔗 Useful URLs

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs` (interactive)
- Health Check: `http://localhost:8000/health`

---

## ⚡ What To Do NOW

1. ✅ Open `http://localhost:5173` in your browser
2. ✅ If blank page, press F12 → Console
3. ✅ Copy any errors and paste them here
4. ✅ I'll diagnose and fix immediately

**Paste here:**
```
[Paste console errors here]
```



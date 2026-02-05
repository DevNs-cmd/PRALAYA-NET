# PRALAYA-NET: Complete Startup Guide

## Quick Start (2 Minutes)

### Windows PowerShell / Command Prompt

**Terminal 1 - Backend:**
```batch
cd backend
python -m uvicorn app:app --port 8000
```

**Terminal 2 - Frontend:**
```batch
cd dashboard
npm run dev
```

**Terminal 3 - Access:**
- Dashboard: http://127.0.0.1:5173
- Backend API: http://127.0.0.1:8000/docs

### macOS / Linux Terminal

**Terminal 1 - Backend:**
```bash
cd backend
python3 -m uvicorn app:app --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd dashboard
npm run dev
```

## Initial Setup (First Time Only)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate              # Linux/macOS
# OR
venv\Scripts\activate                 # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env from template
cp .env.example .env

# Edit .env if needed (API keys, etc.)
# Default settings work for localhost testing
```

### 2. Frontend Setup

```bash
cd dashboard

# Install dependencies (first time only)
npm install

# Create .env from template
cp .env.example .env.local

# Verify VITE_API_URL is set correctly:
# VITE_API_URL=http://127.0.0.1:8000
```

## Starting the System

### Recommended Setup (3 Terminals)

**Terminal 1: Backend Server**
```bash
cd backend
python -m uvicorn app:app --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

**Terminal 2: Frontend Dev Server**
```bash
cd dashboard
npm run dev
```

Expected output:
```
➜  Local:   http://127.0.0.1:5173/
```

**Terminal 3: Test API**
```bash
# Test backend health
curl http://127.0.0.1:8000/api/health

# Expected response:
# {"status":"healthy","components":{"api":"operational","ai_models":"loaded","orchestration":"ready"}}
```

## Accessing the System

| Service | URL | Description |
|---------|-----|-------------|
| Dashboard | http://127.0.0.1:5173 | Main web interface |
| API Docs | http://127.0.0.1:8000/docs | Interactive Swagger UI |
| Health Check | http://127.0.0.1:8000/api/health | Backend status |
| Root API | http://127.0.0.1:8000 | API root info |

## Verification Checklist

- [ ] Backend shows "Uvicorn running on http://127.0.0.1:8000"
- [ ] Frontend shows "Local: http://127.0.0.1:5173"
- [ ] Dashboard header shows "Backend: ONLINE" (green indicator)
- [ ] No red "Backend OFFLINE" banner
- [ ] Browser console shows `[API] Using default backend URL: http://127.0.0.1:8000`
- [ ] Can access http://127.0.0.1:8000/docs without errors

## Troubleshooting

### "Backend OFFLINE" Message in Dashboard

**Issue**: Frontend shows red banner saying "Backend OFFLINE"

**Step 1: Check if backend is running**
```bash
# Windows
netstat -ano | findstr :8000

# macOS/Linux
lsof -i :8000
```

Expected: Should show a listening port for PID

**Step 2: Start backend correctly**
```bash
cd backend
python -m uvicorn app:app --port 8000
```

**Step 3: Verify backend responds**
```bash
curl http://127.0.0.1:8000/api/health
```

**Step 4: Check frontend environment**
```bash
# dashboard/.env.local should contain:
VITE_API_URL=http://127.0.0.1:8000
```

**Step 5: Refresh frontend**
- Open http://127.0.0.1:5173 in browser
- Press F5 to hard refresh
- Check browser console (F12) for error messages

### Port Already in Use

**Error**: `Address already in use` or `Port 8000 already bound`

**Solution**:
```bash
# Windows: Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux: Kill process on port 8000
lsof -i :8000
kill -9 <PID>
```

### Dependencies Missing

**Error**: `ModuleNotFoundError` or `npm error`

**Solution**:
```bash
# Backend
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Frontend
cd dashboard
npm install
```

### Environment Variable Not Loaded

**Issue**: Frontend still tries to connect to wrong backend

**Solution**:
```bash
# 1. Verify .env.local exists in dashboard/
ls dashboard/.env.local

# 2. Check content
cat dashboard/.env.local
# Should show: VITE_API_URL=http://127.0.0.1:8000

# 3. Restart frontend
cd dashboard
npm run dev

# 4. Verify in browser console (F12)
# Should see: [API] Using VITE_API_URL: http://127.0.0.1:8000
```

## Advanced Configuration

### Running on Different Host/Port

**Backend on custom port:**
```bash
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 9000
```

**Frontend with custom backend URL:**
```bash
# Edit dashboard/.env.local
VITE_API_URL=http://127.0.0.1:9000
```

### Production Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for:
- Deploying backend to Render
- Deploying frontend to Vercel
- Environment configuration
- SSL/TLS setup

## Debug Mode

### Enable Detailed Logging

**Frontend browser console:**
- Open DevTools: F12
- Look for `[API]` prefixed messages
- Each API call will log: `[API] Calling GET /api/...`

**Backend server logs:**
- Already verbose in dev mode
- Shows each request with method, path, and status

### Check Network Requests

**Browser Network Tab:**
1. Open DevTools: F12
2. Click "Network" tab
3. Refresh page: F5
4. Look for requests to `http://127.0.0.1:8000/api/...`
5. Check response status and headers

### Common API Response Codes

- `200` - Success ✅
- `404` - Endpoint not found ❌
- `500` - Server error ❌
- `Connection refused` - Backend not running ❌

## System Information

- **Backend**: FastAPI + Uvicorn + Python 3.8+
- **Frontend**: React 18.2 + Vite 5.0
- **Default Ports**: Backend 8000, Frontend 5173
- **CORS Enabled**: For localhost and 127.0.0.1
- **Middleware**: Rate limiting, Input validation, Security headers

## Need Help?

1. Check browser console for `[API]` logs
2. Check backend terminal for errors
3. Review troubleshooting section above
4. Check [README.md](./README.md) for detailed information
5. Review [DEPLOYMENT.md](./DEPLOYMENT.md) for production setup

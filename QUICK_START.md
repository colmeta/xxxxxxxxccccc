# 🚀 QUICK START GUIDE - Pearl Data Intelligence

## Prerequisites
✅ Node.js installed  
✅ Python 3.11+ installed  
✅ Supabase account created  
✅ API keys configured in `.env`

---

## 1. Start Frontend (Already Running ✅)

```bash
cd frontend
npm run dev
```

**Access**: http://localhost:5174  
**Status**: ✅ Login page working

---

## 2. Start Backend Server

```bash
# From project root
python -m backend.main
```

**Expected Output**:
```
✅ Connected to Supabase DataVault
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Test**: Visit http://localhost:8000 - should see `{"status": "operational"}`

---

## 3. Start Worker (Optional but Recommended)

```bash
# From project root
python worker/hydra_controller.py
```

**Expected Output**:
```
[production_hydra_01] Supabase Connection Active.
✅ Deduplication service initialized
[production_hydra_01] Entering continuous surveillance loop...
```

---

## 4. Login & Test

1. **Go to**: http://localhost:5174
2. **Sign up** with email/password
3. **Navigate** to Oracle Control
4. **Create mission**: "Find SaaS companies in Austin"
5. **Watch results** populate in The Vault

---

## Common Issues

### Backend Won't Start
**Problem**: Port 8000 already in use  
**Solution**: 
```bash
# Windows
netstat -ano | findstr :8000
# Kill the process
```

### Worker Connection Error
**Problem**: Missing Supabase credentials  
**Solution**: Check `.env` has `SUPABASE_URL` and `SUPABASE_KEY`

### Frontend API Errors
**Problem**: Backend not running  
**Solution**: Start backend on port 8000 first

---

## Environment Variables Checklist

### Required (Backend)
- [ ] `SUPABASE_URL`
- [ ] `SUPABASE_KEY`
- [ ] `GEMINI_API_KEY` or `GROQ_API_KEY`

### Required (Frontend)
- [ ] `VITE_SUPABASE_URL`
- [ ] `VITE_SUPABASE_ANON_KEY`
- [ ] `VITE_API_URL` (http://localhost:8000)

### Optional
- [ ] `SCRAPER_API_KEY` (for enhanced scraping)
- [ ] `SMTP_USER` / `SMTP_PASS` (for email delivery)

---

## System Architecture

```
┌─────────────────┐
│   Frontend      │  http://localhost:5174
│   (Vite/React)  │  23 Components
└────────┬────────┘
         │ REST API
┌────────▼────────┐
│   Backend       │  http://localhost:8000
│   (FastAPI)     │  17 Routers
└────────┬────────┘
         │ PostgreSQL
┌────────▼────────┐
│   Supabase DB   │  Cloud Hosted
│   (Postgres)    │  RLS Enabled
└─────────────────┘

         ┌────────────────┐
         │   Worker        │  Local Process
         │   (Hydra)       │  23 Scrapers
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │   Web Scraping  │  Playwright
         │   (Stealth)     │  Proxy Support
         └─────────────────┘
```

---

## Key URLs

- **Frontend**: http://localhost:5174
- **Backend Health**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger)
- **Supabase**: https://wzgkvgfehuzycdhmyzsz.supabase.co

---

## Production Deployment

### Frontend (Vercel)
```bash
cd frontend
npm run build
# Deploy dist/ folder to Vercel
```

### Backend (Render/Railway)
```bash
# Build command: pip install -r requirements.txt
# Start command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### Worker (Always-On VM)
```bash
# Install Playwright
python -m playwright install chromium

# Run as service
python worker/hydra_controller.py
```

---

**Need Help?** Check `walkthrough.md` for complete system documentation.

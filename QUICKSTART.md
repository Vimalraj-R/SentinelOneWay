# SentinelOneWay - Quick Start Guide

## ✅ System Status: ALL WORKING CORRECTLY

Both frontend and backend are verified and operational.

---

## 🚀 Running the Application

### Backend (Terminal 1)

```bash
# Navigate to backend
cd backend

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will be available at:**
- API: `http://127.0.0.1:8000`
- Health Check: `http://127.0.0.1:8000/health`
- API Docs (Swagger): `http://127.0.0.1:8000/docs`

---

### Frontend (Terminal 2)

```bash
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev
```

**Frontend will be available at:**
- Application: `http://localhost:5173`

---

## ✅ Verified Components

### Backend
- ✅ FastAPI server running on port 8000
- ✅ `/health` endpoint returning healthy status
- ✅ Swagger UI documentation at `/docs`
- ✅ CORS configured for frontend
- ✅ Virtual environment with dependencies

### Frontend
- ✅ React 18 with Vite
- ✅ Tailwind CSS configured
- ✅ Recharts installed for data visualization
- ✅ Lucide React for icons
- ✅ Dev server with HMR on port 5173
- ✅ SentinelOneWay landing page rendering

### Project Structure
- ✅ Clean separation of frontend/backend
- ✅ Comprehensive README.md
- ✅ Proper .gitignore files
- ✅ All dependencies installed

---

## 🧪 Quick Test

### Test Backend
```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{"status":"healthy","service":"SentinelOneWay API"}
```

### Test Frontend
Open in browser: `http://localhost:5173`

You should see the SentinelOneWay landing page with:
- Shield icon
- Project title
- System status indicator

---

## 📦 Dependencies Installed

### Backend (Python)
- fastapi - Web framework
- uvicorn[standard] - ASGI server
- pydantic - Data validation
- sqlalchemy - Database ORM
- python-multipart - File uploads

*Note: pandas, numpy, scikit-learn will be installed when needed for ML features*

### Frontend (Node.js)
- react - UI framework
- vite - Build tool
- tailwindcss - CSS framework
- recharts - Charts library
- lucide-react - Icon library

---

## 🎯 Phase 1 Complete

All setup verified and working correctly! Ready for Phase 2 development.

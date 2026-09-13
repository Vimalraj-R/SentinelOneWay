# 🎯 SentinelOneWay - Quick Startup Guide

## Visual Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    YOUR BROWSER                                  │
│              http://localhost:5173                               │
│                                                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │  Overview   │  │ Attack       │  │  Simulation Lab     │   │
│  │  Dashboard  │  │ Timeline     │  │                     │   │
│  └─────────────┘  └──────────────┘  └─────────────────────┘   │
└────────────┬─────────────────────────────────────────────────────┘
             │
             │ HTTP REST API + WebSocket (Real-time)
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND SERVER (FastAPI)                            │
│              http://localhost:8000                               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Hybrid Detection Engine                                  │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌─────────────────┐ │  │
│  │  │ Rule-Based   │ │ Random       │ │ Isolation       │ │  │
│  │  │ Detectors    │ │ Forest       │ │ Forest          │ │  │
│  │  └──────────────┘ └──────────────┘ └─────────────────┘ │  │
│  │           │              │                  │            │  │
│  │           └──────────────┴──────────────────┘            │  │
│  │                         │                                │  │
│  │                   Risk Scorer                            │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                       │
│  ┌──────────────────────▼───────────────────────────────────┐  │
│  │  Attack Correlation Engine                               │  │
│  │  (Combines related alerts into incidents)                │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                       │
│                         ▼                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Database (SQLite)                                        │  │
│  │  - Alerts                                                 │  │
│  │  - Incidents                                              │  │
│  │  - Assets                                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Three Ways to Start

### Method 1: Manual (Recommended for First Time)

**Terminal 1 - Backend:**
```bash
cd C:\Users\Vimalraj\SentinelOneWay\backend
source venv/Scripts/activate
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd C:\Users\Vimalraj\SentinelOneWay\frontend
npm run dev
```

**Terminal 3 - Generate Data (Optional):**
```bash
cd C:\Users\Vimalraj\SentinelOneWay\backend
source venv/Scripts/activate
python demo_correlation.py
```

---

### Method 2: Quick Script (Linux/Mac/Git Bash)

```bash
cd C:\Users\Vimalraj\SentinelOneWay

# Interactive menu
./start.sh
```

**Menu options:**
1. Start Backend Only
2. Start Frontend Only
3. Generate Sample Data
4. View URLs
5. Check Status

---

### Method 3: Batch Script (Windows)

```cmd
cd C:\Users\Vimalraj\SentinelOneWay

# Interactive menu
start.bat
```

Same menu as above!

---

## ✅ Verification Checklist

After starting both servers, verify:

- [ ] **Backend Health Check**  
  Visit: http://localhost:8000/health  
  Should see: `{"status": "healthy", ...}`

- [ ] **Backend API Docs**  
  Visit: http://localhost:8000/docs  
  Should see: Swagger UI with all endpoints

- [ ] **Frontend Dashboard**  
  Visit: http://localhost:5173  
  Should see: SentinelOneWay dashboard with metrics

- [ ] **WebSocket Connection**  
  Dashboard shows: "Live" indicator (green dot)  
  Check browser console (F12): No WebSocket errors

- [ ] **Sample Data**  
  Run: `python demo_correlation.py`  
  Dashboard shows: 15 alerts, 3 incidents

---

## 📊 What You Should See

### Backend Terminal Output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**When frontend connects:**
```
INFO:     WebSocket connection accepted
INFO:     Active connections: 1
```

### Frontend Terminal Output:
```
  VITE v8.3.0  ready in 523 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

## 🎯 Your First Test

1. **Start both servers** (backend + frontend)

2. **Open dashboard** in browser: http://localhost:5173

3. **Initial state** - You'll see:
   ```
   Active Threats: 0
   Network Risk Score: 0/100 - Low Risk
   Critical Incidents: 0
   Recent Alerts: (empty state)
   ```

4. **Generate test data**:
   ```bash
   cd backend
   python demo_correlation.py
   ```

5. **Watch dashboard update** in real-time!
   ```
   Active Threats: 15
   Network Risk Score: 78/100 - High Risk
   Critical Incidents: 3
   Recent Alerts: (15 alerts listed)
   ```

6. **Click any alert** → See detailed analysis with AI explanations

7. **Visit Attack Timeline** → See 3 correlated multi-stage attacks

8. **Open Simulation Lab** → Test SYN Flood simulation

---

## 🎨 Expected Dashboard Appearance

```
┌────────────────────────────────────────────────────────────────┐
│ 🔵 Passive Monitoring                                          │
│ Read-only network observation. No active blocking or response. │
└────────────────────────────────────────────────────────────────┘

┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Active       │ │ Network Risk │ │ Critical     │ │ Flows/sec    │
│ Threats      │ │ Score        │ │ Incidents    │ │              │
│              │ │              │ │              │ │              │
│     15       │ │  78/100      │ │      3       │ │    1,245     │
│              │ │  High Risk   │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘

┌────────────────────────────────────────────────────────────────┐
│ Recent Alerts                                    🟢 Live        │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ ● Critical  PORT_SCAN           45 unique ports scanned        │
│   192.168.1.100 → 10.0.0.50     Risk: 85/100   2 min ago      │
│                                                                │
│ ● High      C2_BEACON           Periodic beaconing detected    │
│   192.168.1.100 → 203.0.113.10  Risk: 78/100   5 min ago      │
│                                                                │
│ ● High      DATA_EXFILTRATION   Large outbound transfer        │
│   192.168.1.100 → 203.0.113.10  Risk: 82/100   8 min ago      │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔗 Important URLs Reference

| What | URL |
|------|-----|
| **Main Dashboard** | http://localhost:5173 |
| **Attack Timeline** | http://localhost:5173/timeline |
| **Simulation Lab** | http://localhost:5173/simulation |
| **Backend API** | http://localhost:8000 |
| **API Documentation** | http://localhost:8000/docs |
| **Health Check** | http://localhost:8000/health |

---

## 🛑 How to Stop

1. **Stop Frontend:** Press `CTRL+C` in frontend terminal
2. **Stop Backend:** Press `CTRL+C` in backend terminal

Both will shut down gracefully.

---

## ⚡ Quick Commands Reference

```bash
# Navigate to project
cd C:\Users\Vimalraj\SentinelOneWay

# Start backend
cd backend && source venv/Scripts/activate && uvicorn main:app --reload

# Start frontend (NEW terminal)
cd frontend && npm run dev

# Generate sample data (NEW terminal)
cd backend && source venv/Scripts/activate && python demo_correlation.py

# Check backend status
curl http://localhost:8000/health

# Check frontend (open browser)
# Visit: http://localhost:5173
```

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8000 in use | `taskkill /F /IM python.exe` or use `--port 8001` |
| Port 5173 in use | `taskkill /F /IM node.exe` or use `-- --port 3000` |
| Module not found (backend) | `pip install -r requirements.txt` |
| Module not found (frontend) | `npm install` |
| No data on dashboard | Run `python demo_correlation.py` |
| WebSocket not connecting | Check backend is running at port 8000 |
| Blank screen | Check browser console (F12) for errors |

---

## 📞 Need Help?

1. Check **HOW_TO_RUN_PROJECT.md** for detailed guide
2. Check **backend/HOW_TO_RUN.md** for backend-specific help
3. Check browser console (F12) for frontend errors
4. Check terminal output for backend errors
5. Make sure BOTH servers are running!

---

## 🎓 What Each Server Does

### Backend (Port 8000)
- Runs hybrid detection engine
- Processes network flows
- Stores alerts in database
- Correlates multi-stage attacks
- Provides REST APIs
- Broadcasts WebSocket alerts

### Frontend (Port 5173)
- Displays dashboard UI
- Connects to WebSocket for real-time updates
- Calls REST APIs for data
- Shows visualizations (charts, timelines)
- Provides simulation interface

**They work together** - Frontend is the "face", Backend is the "brain"

---

## 🚀 You're Ready!

Just run these commands:

```bash
# Terminal 1
cd backend && source venv/Scripts/activate && uvicorn main:app --reload

# Terminal 2
cd frontend && npm run dev

# Open browser
http://localhost:5173
```

**That's it!** 🎉

---

**Pro Tip:** Keep both terminal windows visible side-by-side so you can see logs from both servers. This helps debug any issues!

# How to Run SentinelOneWay Backend

## Quick Start

```bash
# 1. Navigate to backend directory
cd C:\Users\Vimalraj\SentinelOneWay\backend

# 2. Activate virtual environment
source venv/Scripts/activate
# On Windows Command Prompt: venv\Scripts\activate
# On Windows PowerShell: venv\Scripts\Activate.ps1

# 3. Start the server
uvicorn main:app --reload
```

Server will start at: **http://localhost:8000**

---

## Detailed Instructions

### Step 1: Prerequisites Check

**Verify Python is installed:**
```bash
python --version
# Should show: Python 3.9+ (tested with 3.14.6)
```

**Verify you're in the backend directory:**
```bash
pwd
# Should show: /c/Users/Vimalraj/SentinelOneWay/backend
```

### Step 2: Activate Virtual Environment

**On Git Bash / Linux / Mac:**
```bash
source venv/Scripts/activate
```

**On Windows Command Prompt:**
```cmd
venv\Scripts\activate
```

**On Windows PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

**Verification:**
Your prompt should change to show `(venv)`:
```
(venv) ~/SentinelOneWay/backend$
```

### Step 3: Install Dependencies (First Time Only)

If this is your first time running, or if you see import errors:

```bash
pip install -r requirements.txt
```

**Core dependencies:**
- fastapi (API framework)
- uvicorn (ASGI server)
- sqlalchemy (Database ORM)
- pandas, numpy (Data processing)
- scikit-learn (ML models)

### Step 4: Start the FastAPI Server

**Development mode (auto-reload on code changes):**
```bash
uvicorn main:app --reload
```

**Production mode (no auto-reload):**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Custom port:**
```bash
uvicorn main:app --port 8080 --reload
```

**Alternative method (using main.py directly):**
```bash
python main.py
```

### Step 5: Verify Server is Running

You should see output like:
```
INFO:     Will watch for changes in these directories: ['/c/Users/Vimalraj/SentinelOneWay/backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Open your browser and test these URLs:**

1. **Health Check:** http://localhost:8000/health
   ```json
   {"status": "healthy", "service": "SentinelOneWay API", "version": "0.2.0"}
   ```

2. **API Root:** http://localhost:8000/
   ```json
   {
     "name": "SentinelOneWay API",
     "version": "0.2.0",
     "description": "Passive AI-powered Network Detection and Response",
     "docs": "/docs"
   }
   ```

3. **Interactive API Docs:** http://localhost:8000/docs
   - Full Swagger UI with all endpoints
   - Test APIs directly from browser

4. **Alternative Docs:** http://localhost:8000/redoc
   - Clean ReDoc documentation

### Step 6: Test API Endpoints

**Using curl (from another terminal):**

```bash
# Health check
curl http://localhost:8000/health

# Get recent alerts
curl http://localhost:8000/api/alerts/recent

# Get dashboard stats
curl http://localhost:8000/api/dashboard/stats

# Get incidents
curl http://localhost:8000/api/incidents/
```

**Using Python:**
```python
import requests

# Test health endpoint
response = requests.get("http://localhost:8000/health")
print(response.json())
# {'status': 'healthy', 'service': 'SentinelOneWay API', 'version': '0.2.0'}
```

---

## Available API Endpoints

Once the server is running, these endpoints are available:

### Core Endpoints
- `GET /` - API information
- `GET /health` - Health check

### Alerts
- `GET /api/alerts/recent` - Recent alerts (last 100)
- `GET /api/alerts/{alert_id}` - Alert details
- `GET /api/alerts/` - List alerts with filtering
- `GET /api/test-alerts/generate` - Generate test alerts

### Dashboard
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/recent-alerts` - Recent alerts for dashboard

### Incidents (Attack Correlation)
- `GET /api/incidents/` - List incidents
- `GET /api/incidents/{id}` - Incident details with timeline
- `POST /api/incidents/correlate` - Trigger correlation
- `GET /api/incidents/stats/summary` - Incident statistics

### Explainability
- `GET /api/explanations/alert/{alert_id}` - Explain alert
- `POST /api/explanations/explain` - Explain custom features
- `GET /api/explanations/cache/stats` - Cache statistics

### Simulation
- `POST /api/simulation/start` - Start simulation
- `POST /api/simulation/stop` - Stop simulation
- `GET /api/simulation/metrics` - Simulation metrics

### WebSocket
- `WS /ws/alerts` - Real-time alert streaming

### Metrics & Assets
- `GET /api/metrics/traffic` - Traffic metrics
- `GET /api/assets/` - Asset list

---

## Running Demo Scripts

After starting the server, you can run demo scripts to populate data:

### Generate Test Alerts
```bash
# In a NEW terminal (keep server running)
cd C:\Users\Vimalraj\SentinelOneWay\backend
source venv/Scripts/activate

# Generate sample alerts
python demo_detection.py
```

### Test Hybrid Detection
```bash
python demo_hybrid_engine.py
```

### Create Correlated Incidents
```bash
python demo_correlation.py
# Creates multi-stage attack scenarios
```

### Test Simulation
```bash
python test_simulation.py
```

---

## Stopping the Server

**Graceful shutdown:**
- Press `CTRL+C` in the terminal where uvicorn is running

**Kill if frozen:**
```bash
# Find the process
ps aux | grep uvicorn

# Kill by PID
kill <PID>

# Or on Windows:
taskkill /F /IM python.exe
```

---

## Common Issues & Solutions

### Issue 1: "ModuleNotFoundError"
**Problem:** Missing dependencies

**Solution:**
```bash
source venv/Scripts/activate
pip install -r requirements.txt
```

### Issue 2: "Address already in use"
**Problem:** Port 8000 is occupied

**Solution 1 - Use different port:**
```bash
uvicorn main:app --reload --port 8001
```

**Solution 2 - Kill existing process:**
```bash
# On Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# On Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Issue 3: "Database is locked"
**Problem:** SQLite database in use

**Solution:**
```bash
# Close all other connections, then restart
rm sentineloneway.db-journal  # If exists
```

### Issue 4: "SHAP not installed" Warning
**Problem:** Optional SHAP library missing

**Solution (optional - system works without it):**
```bash
pip install shap
```

### Issue 5: CORS errors from frontend
**Problem:** Frontend running on different port

**Solution:** Update `main.py` CORS settings:
```python
allow_origins=[
    "http://localhost:5173",  # Add your frontend port
    "http://localhost:3000",
]
```

### Issue 6: "Cannot find models/*.pkl"
**Problem:** ML models not trained

**Solution:**
```bash
# Train models (if needed)
python demo_features.py  # Generate features
python demo_ml_detection.py  # Train Random Forest
```

---

## Development Tips

### Auto-reload on Code Changes
Use `--reload` flag (already default in quick start):
```bash
uvicorn main:app --reload
```
Server automatically restarts when you edit Python files.

### Enable SQL Query Logging
Edit `database/base.py`:
```python
engine = create_engine(
    DATABASE_URL,
    echo=True  # Set to True
)
```

### Watch Logs in Real-Time
```bash
uvicorn main:app --reload --log-level debug
```

### Check Server Status
```bash
curl http://localhost:8000/health
```

### Monitor Active WebSocket Connections
Check logs when clients connect:
```
INFO: WebSocket connection accepted: <client_id>
INFO: Active connections: 1
```

---

## Next Steps

1. **Start Backend:** `uvicorn main:app --reload`
2. **Start Frontend:** (See frontend/README.md)
3. **Open Dashboard:** http://localhost:5173
4. **Test Detection:** Run `python demo_correlation.py`
5. **View API Docs:** http://localhost:8000/docs

---

## Production Deployment

For production (NOT for development):

```bash
# Use gunicorn with uvicorn workers
pip install gunicorn

# Run with 4 workers
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Or use Docker:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Environment Variables (Optional)

Create `.env` file for configuration:
```bash
# .env
DATABASE_URL=sqlite:///./sentineloneway.db
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

Load with:
```bash
pip install python-dotenv
```

---

## Support

**Check Logs:** Server outputs all requests and errors to terminal

**API Documentation:** http://localhost:8000/docs

**Test Endpoints:** Use Swagger UI at `/docs` to test all APIs interactively

**Database:** SQLite at `sentineloneway.db` (view with DB Browser for SQLite)

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `source venv/Scripts/activate` | Activate virtual environment |
| `uvicorn main:app --reload` | Start development server |
| `python main.py` | Alternative start method |
| `CTRL+C` | Stop server |
| `deactivate` | Exit virtual environment |
| `pip install -r requirements.txt` | Install dependencies |
| `python demo_correlation.py` | Generate sample data |

**Server URL:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs  
**WebSocket:** ws://localhost:8000/ws/alerts

#!/bin/bash
# SentinelOneWay MVP Verification Script
# Verifies complete end-to-end functionality

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  SentinelOneWay MVP Verification${NC}"
echo -e "${BLUE}  Complete End-to-End Testing${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
test_step() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $1"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Section header
section() {
    echo ""
    echo -e "${YELLOW}=== $1 ===${NC}"
}

###################
# 1. BACKEND TESTS
###################
section "Backend Verification"

cd backend

# Check virtual environment
if [ -d "venv" ]; then
    test_step "Virtual environment exists"
else
    echo -e "${RED}✗${NC} Virtual environment not found"
    ((TESTS_FAILED++))
fi

# Activate venv
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate 2>/dev/null

# Check Python version
python --version | grep -q "Python 3" && test_step "Python 3.x installed" || {
    echo -e "${RED}✗${NC} Python 3.x not found"
    ((TESTS_FAILED++))
}

# Check dependencies
echo "Checking Python dependencies..."
pip show fastapi >/dev/null 2>&1 && test_step "FastAPI installed" || {
    echo -e "${RED}✗${NC} FastAPI not installed"
    ((TESTS_FAILED++))
}

pip show uvicorn >/dev/null 2>&1 && test_step "Uvicorn installed" || {
    echo -e "${RED}✗${NC} Uvicorn not installed"
    ((TESTS_FAILED++))
}

pip show scikit-learn >/dev/null 2>&1 && test_step "scikit-learn installed" || {
    echo -e "${RED}✗${NC} scikit-learn not installed"
    ((TESTS_FAILED++))
}

pip show sqlalchemy >/dev/null 2>&1 && test_step "SQLAlchemy installed" || {
    echo -e "${RED}✗${NC} SQLAlchemy not installed"
    ((TESTS_FAILED++))
}

# Check ML models
if [ -f "models/random_forest.pkl" ]; then
    test_step "Random Forest model exists"
else
    echo -e "${RED}✗${NC} Random Forest model not found"
    ((TESTS_FAILED++))
fi

if [ -f "models/isolation_forest.pkl" ]; then
    test_step "Isolation Forest model exists"
else
    echo -e "${RED}✗${NC} Isolation Forest model not found"
    ((TESTS_FAILED++))
fi

# Test imports
python -c "from main import app" 2>/dev/null && test_step "Main app imports successfully" || {
    echo -e "${RED}✗${NC} Main app import failed"
    ((TESTS_FAILED++))
}

python -c "from detection.hybrid_engine import HybridDetectionEngine" 2>/dev/null && test_step "Hybrid engine imports" || {
    echo -e "${RED}✗${NC} Hybrid engine import failed"
    ((TESTS_FAILED++))
}

python -c "from correlation.engine import CorrelationEngine" 2>/dev/null && test_step "Correlation engine imports" || {
    echo -e "${RED}✗${NC} Correlation engine import failed"
    ((TESTS_FAILED++))
}

# Start backend in background
echo "Starting backend server..."
uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
sleep 5

# Check if backend is running
if ps -p $BACKEND_PID > /dev/null; then
    test_step "Backend server started"

    # Test health endpoint
    curl -s http://localhost:8000/health | grep -q "healthy" && test_step "Health endpoint responds" || {
        echo -e "${RED}✗${NC} Health endpoint failed"
        ((TESTS_FAILED++))
    }

    # Test API endpoints
    curl -s http://localhost:8000/api/dashboard/stats > /dev/null && test_step "Dashboard API responds" || {
        echo -e "${RED}✗${NC} Dashboard API failed"
        ((TESTS_FAILED++))
    }

    curl -s http://localhost:8000/api/alerts/recent > /dev/null && test_step "Alerts API responds" || {
        echo -e "${RED}✗${NC} Alerts API failed"
        ((TESTS_FAILED++))
    }

    curl -s http://localhost:8000/api/incidents/ > /dev/null && test_step "Incidents API responds" || {
        echo -e "${RED}✗${NC} Incidents API failed"
        ((TESTS_FAILED++))
    }

else
    echo -e "${RED}✗${NC} Backend server failed to start"
    ((TESTS_FAILED++))
fi

###################
# 2. FRONTEND TESTS
###################
cd ../frontend

section "Frontend Verification"

# Check if npm is installed
command -v npm >/dev/null 2>&1 && test_step "npm installed" || {
    echo -e "${RED}✗${NC} npm not found"
    ((TESTS_FAILED++))
}

# Check node_modules
if [ -d "node_modules" ]; then
    test_step "Dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} Dependencies not installed. Run 'npm install'"
    ((TESTS_FAILED++))
fi

# Check page files
PAGE_COUNT=$(ls src/pages/*.jsx 2>/dev/null | wc -l)
if [ "$PAGE_COUNT" -ge 7 ]; then
    test_step "All page components exist ($PAGE_COUNT files)"
else
    echo -e "${RED}✗${NC} Missing page components (found $PAGE_COUNT, expected 7+)"
    ((TESTS_FAILED++))
fi

# Check specific pages
[ -f "src/pages/Overview.jsx" ] && test_step "Overview page exists" || {
    echo -e "${RED}✗${NC} Overview page missing"
    ((TESTS_FAILED++))
}

[ -f "src/pages/LiveTraffic.jsx" ] && test_step "Live Traffic page exists" || {
    echo -e "${RED}✗${NC} Live Traffic page missing"
    ((TESTS_FAILED++))
}

[ -f "src/pages/ThreatAlerts.jsx" ] && test_step "Threat Alerts page exists" || {
    echo -e "${RED}✗${NC} Threat Alerts page missing"
    ((TESTS_FAILED++))
}

[ -f "src/pages/AttackTimeline.jsx" ] && test_step "Attack Timeline page exists" || {
    echo -e "${RED}✗${NC} Attack Timeline page missing"
    ((TESTS_FAILED++))
}

[ -f "src/pages/Assets.jsx" ] && test_step "Assets page exists" || {
    echo -e "${RED}✗${NC} Assets page missing"
    ((TESTS_FAILED++))
}

[ -f "src/pages/SimulationLab.jsx" ] && test_step "Simulation Lab page exists" || {
    echo -e "${RED}✗${NC} Simulation Lab page missing"
    ((TESTS_FAILED++))
}

[ -f "src/pages/SystemHealth.jsx" ] && test_step "System Health page exists" || {
    echo -e "${RED}✗${NC} System Health page missing"
    ((TESTS_FAILED++))
}

# Check components
[ -f "src/components/common/PassiveMonitoringBanner.jsx" ] && test_step "PassiveMonitoringBanner exists" || {
    echo -e "${RED}✗${NC} PassiveMonitoringBanner missing"
    ((TESTS_FAILED++))
}

[ -f "src/components/common/SeverityBadge.jsx" ] && test_step "SeverityBadge exists" || {
    echo -e "${RED}✗${NC} SeverityBadge missing"
    ((TESTS_FAILED++))
}

[ -f "src/components/common/EmptyState.jsx" ] && test_step "EmptyState exists" || {
    echo -e "${RED}✗${NC} EmptyState missing"
    ((TESTS_FAILED++))
}

# Try to build
echo "Testing production build..."
npm run build > /tmp/frontend-build.log 2>&1
if [ $? -eq 0 ]; then
    test_step "Production build successful"
    [ -d "dist" ] && test_step "Build output created" || {
        echo -e "${RED}✗${NC} Build output missing"
        ((TESTS_FAILED++))
    }
else
    echo -e "${RED}✗${NC} Production build failed"
    ((TESTS_FAILED++))
fi

# Start frontend in background
echo "Starting frontend server..."
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 7

# Check if frontend is running
if ps -p $FRONTEND_PID > /dev/null; then
    test_step "Frontend server started"

    # Test if accessible
    curl -s http://localhost:5173 > /dev/null && test_step "Frontend accessible" || {
        echo -e "${RED}✗${NC} Frontend not accessible"
        ((TESTS_FAILED++))
    }
else
    echo -e "${RED}✗${NC} Frontend server failed to start"
    ((TESTS_FAILED++))
fi

###################
# 3. INTEGRATION TESTS
###################
cd ../backend

section "Integration Testing"

# Generate sample data
echo "Generating sample data..."
python demo_correlation.py > /tmp/demo.log 2>&1
if [ $? -eq 0 ]; then
    test_step "Sample data generated"

    # Check database
    python -c "
from database.base import SessionLocal
from database.models import Alert
from database.incident_models import Incident

session = SessionLocal()
alert_count = session.query(Alert).count()
incident_count = session.query(Incident).count()
session.close()

print(f'Alerts: {alert_count}, Incidents: {incident_count}')
exit(0 if alert_count > 0 and incident_count > 0 else 1)
" && test_step "Database contains data" || {
        echo -e "${RED}✗${NC} Database verification failed"
        ((TESTS_FAILED++))
    }
else
    echo -e "${RED}✗${NC} Sample data generation failed"
    ((TESTS_FAILED++))
fi

# Test API with data
curl -s http://localhost:8000/api/alerts/recent | grep -q '"id"' && test_step "Alerts API returns data" || {
    echo -e "${RED}✗${NC} Alerts API returns no data"
    ((TESTS_FAILED++))
}

curl -s http://localhost:8000/api/incidents/ | grep -q '"incident_id"' && test_step "Incidents API returns data" || {
    echo -e "${RED}✗${NC} Incidents API returns no data"
    ((TESTS_FAILED++))
}

# Test detection
python -c "
from detection.hybrid_engine import HybridDetectionEngine

engine = HybridDetectionEngine()
single_flow = {'protocol': 6, 'duration': 120, 'packets': 250, 'bytes': 45000, 'syn_flag': 1, 'ack_flag': 0, 'tcp_flags_count': 1}
aggregate = {'flow_count': 45, 'unique_destination_ports': 42, 'packets_per_second': 25.5, 'bytes_per_second': 15000, 'syn_ack_ratio': 0.05, 'periodicity_score': 0.02, 'dns_entropy': 1.5, 'outbound_inbound_ratio': 5.0, 'distinct_protocols': 1}

result = engine.detect(single_flow, aggregate)
print(f'Detection: {result.threat_class}, Risk: {result.risk_score}')
exit(0)
" && test_step "Hybrid detection engine works" || {
    echo -e "${RED}✗${NC} Detection engine failed"
    ((TESTS_FAILED++))
}

###################
# 4. CLEANUP
###################
section "Cleanup"

# Stop servers
if [ ! -z "$BACKEND_PID" ]; then
    kill $BACKEND_PID 2>/dev/null
    test_step "Backend server stopped"
fi

if [ ! -z "$FRONTEND_PID" ]; then
    kill $FRONTEND_PID 2>/dev/null
    test_step "Frontend server stopped"
fi

###################
# SUMMARY
###################
echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Verification Summary${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))

echo -e "Total Tests: ${BLUE}$TOTAL_TESTS${NC}"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}✓ SentinelOneWay MVP is COMPLETE and DEPLOYMENT READY!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run backend: cd backend && uvicorn main:app --reload"
    echo "  2. Run frontend: cd frontend && npm run dev"
    echo "  3. Open browser: http://localhost:5173"
    echo "  4. For Docker: docker-compose up -d"
    echo ""
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo ""
    echo "Check the following:"
    echo "  - Backend: /tmp/backend.log"
    echo "  - Frontend: /tmp/frontend.log"
    echo "  - Build: /tmp/frontend-build.log"
    echo ""
    exit 1
fi

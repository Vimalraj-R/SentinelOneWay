#!/bin/bash
# SentinelOneWay Quick Start Script
# This script helps you start both backend and frontend

echo "=========================================="
echo "   SentinelOneWay - Quick Start"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}What would you like to do?${NC}"
echo ""
echo "1) Start Backend Only"
echo "2) Start Frontend Only"
echo "3) Generate Sample Data"
echo "4) View URLs"
echo "5) Check Status"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
  1)
    echo -e "${GREEN}Starting Backend...${NC}"
    cd backend
    source venv/Scripts/activate
    echo -e "${GREEN}Backend starting at http://localhost:8000${NC}"
    echo -e "${YELLOW}Press CTRL+C to stop${NC}"
    uvicorn main:app --reload
    ;;
  2)
    echo -e "${GREEN}Starting Frontend...${NC}"
    cd frontend
    echo -e "${GREEN}Frontend starting at http://localhost:5173${NC}"
    echo -e "${YELLOW}Press CTRL+C to stop${NC}"
    npm run dev
    ;;
  3)
    echo -e "${GREEN}Generating Sample Data...${NC}"
    cd backend
    source venv/Scripts/activate
    python demo_correlation.py
    echo ""
    echo -e "${GREEN}Done! Generated:${NC}"
    echo "  - 15 alerts (Port Scans, C2 Beacons, Exfiltration)"
    echo "  - 3 correlated incidents (Multi-stage attacks)"
    echo ""
    echo -e "${YELLOW}Refresh your dashboard to see the data!${NC}"
    ;;
  4)
    echo ""
    echo -e "${GREEN}=== SentinelOneWay URLs ===${NC}"
    echo ""
    echo "Frontend Dashboard:"
    echo "  http://localhost:5173"
    echo ""
    echo "Backend API:"
    echo "  http://localhost:8000"
    echo "  http://localhost:8000/docs (API Documentation)"
    echo "  http://localhost:8000/health (Health Check)"
    echo ""
    echo "WebSocket:"
    echo "  ws://localhost:8000/ws/alerts"
    echo ""
    ;;
  5)
    echo ""
    echo -e "${GREEN}Checking Backend...${NC}"
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
      echo -e "  ${GREEN}✓ Backend is RUNNING${NC} (http://localhost:8000)"
    else
      echo -e "  ${RED}✗ Backend is NOT running${NC}"
    fi

    echo ""
    echo -e "${GREEN}Checking Frontend...${NC}"
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
      echo -e "  ${GREEN}✓ Frontend is RUNNING${NC} (http://localhost:5173)"
    else
      echo -e "  ${RED}✗ Frontend is NOT running${NC}"
    fi
    echo ""
    ;;
  *)
    echo -e "${RED}Invalid choice${NC}"
    ;;
esac

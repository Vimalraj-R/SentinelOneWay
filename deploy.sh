#!/bin/bash
# SentinelOneWay - Quick Deployment Script
# Run this script to deploy the entire application with Docker

set -e  # Exit on error

echo "=========================================="
echo "  SentinelOneWay - Deployment Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed!${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed!${NC}"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
echo ""

# Check if ports are available
echo "Checking if required ports are available..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}Warning: Port 8000 is already in use!${NC}"
    echo "Please stop the service using port 8000 or change the port in docker-compose.yml"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

if lsof -Pi :80 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}Warning: Port 80 is already in use!${NC}"
    echo "Please stop the service using port 80 or change the port in docker-compose.yml"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}✓ Ports are available${NC}"
echo ""

# Stop existing containers
echo "Stopping existing containers (if any)..."
docker-compose down 2>/dev/null || true
echo -e "${GREEN}✓ Cleaned up existing containers${NC}"
echo ""

# Build images
echo "Building Docker images..."
echo "This may take a few minutes on first run..."
echo ""
docker-compose build --no-cache
echo -e "${GREEN}✓ Images built successfully${NC}"
echo ""

# Start services
echo "Starting services..."
docker-compose up -d
echo -e "${GREEN}✓ Services started${NC}"
echo ""

# Wait for services to be healthy
echo "Waiting for services to be healthy..."
sleep 5

# Check backend health
echo "Checking backend health..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is healthy${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Backend failed to start${NC}"
        echo "Check logs with: docker-compose logs backend"
        exit 1
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

# Check frontend health
echo "Checking frontend health..."
for i in {1..30}; do
    if curl -s http://localhost:80 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend is healthy${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Frontend failed to start${NC}"
        echo "Check logs with: docker-compose logs frontend"
        exit 1
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

echo ""
echo "=========================================="
echo -e "  ${GREEN}Deployment Successful!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}Access your application:${NC}"
echo "  Frontend: http://localhost"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo "  View logs:      docker-compose logs -f"
echo "  Stop services:  docker-compose down"
echo "  Restart:        docker-compose restart"
echo "  Status:         docker-compose ps"
echo ""
echo -e "${GREEN}Happy monitoring! 🚀${NC}"

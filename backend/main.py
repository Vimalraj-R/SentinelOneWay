"""
SentinelOneWay Backend API

FastAPI application for passive network threat detection and monitoring.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os

# Import API routers
from api.alerts import router as alerts_router
from api.metrics import router as metrics_router
from api.assets import router as assets_router
from api.dashboard import router as dashboard_router
from api.simulation import router as simulation_router
from api.websocket import router as websocket_router
from api.test_alerts import router as test_alerts_router
from api.explanations import router as explanations_router
from api.incidents import router as incidents_router
from api.continuous_traffic import router as continuous_traffic_router

# Import WebSocket heartbeat
from websocket.manager import heartbeat_loop

# Import continuous traffic service
from services.continuous_traffic_service import continuous_traffic_service
from database.base import Base, engine
from database import models  # noqa: F401
from database import incident_models  # noqa: F401

# Create FastAPI application
app = FastAPI(
    title="SentinelOneWay API",
    description="Passive AI-powered Network Detection and Response intelligence API",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for React frontend
cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]
cors_origins.extend([
    "https://sentinel-one-way-mvp.vercel.app",
    "https://sentinel-one-way-mvp-git-main-vimalraj-rs-projects.vercel.app",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:3000",
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https://sentinel-one-way(?:-mvp)?(?:-[a-z0-9-]+)*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Register API routers
app.include_router(alerts_router)
app.include_router(metrics_router)
app.include_router(assets_router)
app.include_router(dashboard_router)
app.include_router(simulation_router)
app.include_router(websocket_router)
app.include_router(test_alerts_router)
app.include_router(explanations_router)
app.include_router(incidents_router)
app.include_router(continuous_traffic_router)


# Startup event to start WebSocket heartbeat and continuous traffic
@app.on_event("startup")
async def startup_event():
    """Start background tasks on application startup."""
    # Render starts with a fresh filesystem, so create the SQLite schema first.
    Base.metadata.create_all(bind=engine)

    # Start WebSocket heartbeat loop
    asyncio.create_task(heartbeat_loop())

    # Get the current event loop and pass it to continuous traffic service
    loop = asyncio.get_event_loop()
    continuous_traffic_service.event_loop = loop

    # Start continuous traffic generation for live MVP demo
    print("\n>>> Starting continuous traffic generation...")
    print("    All pages will receive live data automatically!")
    continuous_traffic_service.start()


# Shutdown event to cleanup
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    print("\n>>> Stopping continuous traffic generation...")
    continuous_traffic_service.stop()


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring system status.
    """
    return {
        "status": "healthy",
        "service": "SentinelOneWay API",
        "version": "0.2.0"
    }


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "SentinelOneWay API",
        "version": "0.2.0",
        "description": "Passive AI-powered Network Detection and Response",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

"""
Continuous Traffic API endpoints.

Controls the background traffic generation service that provides
live data to all pages across the MVP.
"""
from fastapi import APIRouter, HTTPException

from services.continuous_traffic_service import continuous_traffic_service

router = APIRouter(prefix="/api/continuous-traffic", tags=["continuous-traffic"])


@router.post("/start")
def start_continuous_traffic():
    """
    Start continuous background traffic generation.

    Begins generating live network flows, alerts, and metrics that
    feed into all pages of the application for real-time demonstration.

    The service runs scenarios in rotation:
    - Normal traffic (baseline)
    - Attack scenarios (SYN flood, port scan, C2, etc.)
    - Automatic cycling for realistic demo

    **Safe for MVP:** All traffic is synthetic metadata only.
    No actual network packets are transmitted.

    Returns:
        Status confirmation
    """
    try:
        continuous_traffic_service.start()
        status = continuous_traffic_service.get_status()

        return {
            "status": "started",
            "message": "Continuous traffic generation started",
            **status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start: {str(e)}")


@router.post("/stop")
def stop_continuous_traffic():
    """
    Stop continuous background traffic generation.

    Stops the background service and returns statistics about
    the traffic generated during this session.

    Returns:
        Final statistics and confirmation
    """
    try:
        status_before = continuous_traffic_service.get_status()
        continuous_traffic_service.stop()

        return {
            "status": "stopped",
            "message": "Continuous traffic generation stopped",
            "flows_generated": status_before.get("flows_processed", 0),
            "alerts_generated": status_before.get("alerts_generated", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop: {str(e)}")


@router.get("/status")
def get_continuous_traffic_status():
    """
    Get current status of continuous traffic service.

    Returns information about whether the service is running,
    current scenario, and generation statistics.

    Returns:
        Service status and statistics
    """
    try:
        status = continuous_traffic_service.get_status()

        return {
            "status": "running" if status["is_running"] else "stopped",
            **status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

"""
Alert API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from database.base import get_db
from schemas.alert import AlertResponse, AlertListResponse, AlertCreate, AlertUpdate
from services.alert_service import AlertService

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=AlertListResponse)
def get_alerts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of alerts with optional filtering and pagination.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (max 1000)
    - **severity**: Filter by severity (Critical, High, Medium, Low)
    - **status**: Filter by status (Active, Investigating, Resolved, etc.)
    """
    alerts, total = AlertService.get_alerts(
        db=db,
        skip=skip,
        limit=limit,
        severity=severity,
        status=status
    )

    return AlertListResponse(
        total=total,
        alerts=alerts
    )


@router.get("/recent")
def get_recent_alerts(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of recent alerts to return"),
    db: Session = Depends(get_db)
):
    """
    Retrieve recent alerts (shortcut endpoint for common use case).

    Returns alerts ordered by timestamp descending.

    - **limit**: Maximum number of alerts to return (default 100)
    """
    alerts = AlertService.get_recent_alerts(db=db, limit=limit)

    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific alert by ID.

    - **alert_id**: The ID of the alert to retrieve
    """
    alert = AlertService.get_alert_by_id(db=db, alert_id=alert_id)

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert


@router.post("", response_model=AlertResponse, status_code=201)
def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new alert.

    This endpoint would typically be called by the detection engine
    when a threat is identified.
    """
    try:
        alert = AlertService.create_alert(db=db, alert_data=alert_data)
        return alert
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{alert_id}/status", response_model=AlertResponse)
def update_alert_status(
    alert_id: int,
    status_data: AlertUpdate,
    db: Session = Depends(get_db)
):
    """
    Update the status of an alert.

    This is used by SOC analysts to mark alerts as investigating,
    acknowledged, or resolved.

    - **alert_id**: The ID of the alert to update
    - **status**: New status (Active, Investigating, Acknowledged, Resolved, Blocked)
    """
    alert = AlertService.update_alert_status(
        db=db,
        alert_id=alert_id,
        status_data=status_data
    )

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert

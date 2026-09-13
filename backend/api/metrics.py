"""
Network Metric API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.base import get_db
from schemas.metric import NetworkMetricResponse, NetworkMetricHistoryResponse
from services.metric_service import MetricService

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/current", response_model=NetworkMetricResponse)
def get_current_metrics(db: Session = Depends(get_db)):
    """
    Retrieve the most recent network metrics.

    Returns current traffic statistics including:
    - Flows per second
    - Packets per second
    - Bytes per second
    - Protocol distribution percentages
    """
    metric = MetricService.get_current_metric(db=db)

    if not metric:
        raise HTTPException(status_code=404, detail="No metrics available")

    return metric


@router.get("/history", response_model=NetworkMetricHistoryResponse)
def get_metrics_history(
    hours: int = Query(24, ge=1, le=168, description="Hours of history to retrieve"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db)
):
    """
    Retrieve network metrics history.

    - **hours**: Number of hours of history to retrieve (max 168 = 1 week)
    - **limit**: Maximum number of records to return (max 1000)
    """
    metrics, total = MetricService.get_metrics_history(
        db=db,
        hours=hours,
        limit=limit
    )

    return NetworkMetricHistoryResponse(
        total=total,
        metrics=metrics
    )

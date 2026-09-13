"""
API endpoints for attack incidents and correlation.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from database.base import get_db
from services.incident_service import IncidentService

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])


@router.get("/")
async def get_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    severity: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of incidents with optional filtering.

    Args:
        skip: Number of incidents to skip (pagination)
        limit: Maximum number of incidents to return
        severity: Filter by severity (Critical, High, Medium, Low)
        status: Filter by status (Active, Investigating, Contained, Resolved)
    """
    incidents, total = IncidentService.get_incidents(
        db, skip, limit, severity, status
    )

    # Convert to response format
    incident_list = []
    for incident in incidents:
        import json

        incident_list.append({
            'incident_id': incident.incident_id,
            'start_time': incident.start_time.isoformat(),
            'last_updated': incident.last_updated.isoformat(),
            'duration_minutes': incident.duration_minutes,
            'risk_score': incident.risk_score,
            'severity': incident.severity.value if hasattr(incident.severity, 'value') else str(incident.severity),
            'status': incident.status.value if hasattr(incident.status, 'value') else str(incident.status),
            'attack_pattern': incident.attack_pattern,
            'summary': incident.summary,
            'alert_count': incident.alert_count,
            'affected_assets_count': len(json.loads(incident.affected_assets)),
            'correlation_confidence': incident.correlation_confidence
        })

    return {
        'incidents': incident_list,
        'total': total,
        'skip': skip,
        'limit': limit
    }


@router.get("/{incident_id}")
async def get_incident_detail(
    incident_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed incident information including timeline and related alerts.

    Args:
        incident_id: Incident ID
    """
    incident = IncidentService.get_incident_with_alerts(db, incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident


@router.post("/correlate")
async def correlate_alerts(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """
    Trigger alert correlation to create/update incidents.

    Args:
        hours: How many hours back to correlate alerts
    """
    incidents = IncidentService.correlate_recent_alerts(db, hours)

    return {
        'status': 'success',
        'incidents_created': len(incidents),
        'incidents': [
            {
                'incident_id': inc.incident_id,
                'attack_pattern': inc.attack_pattern,
                'alert_count': inc.alert_count,
                'risk_score': inc.risk_score
            }
            for inc in incidents
        ]
    }


@router.patch("/{incident_id}/status")
async def update_incident_status(
    incident_id: str,
    status: str = Query(..., regex="^(Active|Investigating|Contained|Resolved)$"),
    db: Session = Depends(get_db)
):
    """
    Update incident status.

    Args:
        incident_id: Incident ID
        status: New status (Active, Investigating, Contained, Resolved)
    """
    incident = IncidentService.update_incident_status(db, incident_id, status)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        'status': 'success',
        'incident_id': incident.incident_id,
        'new_status': incident.status.value if hasattr(incident.status, 'value') else str(incident.status)
    }


@router.get("/stats/summary")
async def get_incident_stats(db: Session = Depends(get_db)):
    """Get incident statistics for dashboard."""
    active_count = IncidentService.get_active_incidents_count(db)
    critical_count = IncidentService.get_critical_incidents_count(db)

    # Get recent incidents
    incidents, total = IncidentService.get_incidents(db, skip=0, limit=10)

    return {
        'active_incidents': active_count,
        'critical_incidents': critical_count,
        'total_incidents': total,
        'recent_incidents': [
            {
                'incident_id': inc.incident_id,
                'attack_pattern': inc.attack_pattern,
                'risk_score': inc.risk_score,
                'start_time': inc.start_time.isoformat()
            }
            for inc in incidents[:5]
        ]
    }

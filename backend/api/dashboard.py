"""
Dashboard API endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.base import get_db
from schemas.dashboard import DashboardSummary
from services.alert_service import AlertService
from services.metric_service import MetricService
from services.asset_service import AssetService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Retrieve dashboard summary data.

    This endpoint aggregates data from multiple sources to provide
    a comprehensive overview of the network security posture.

    Returns:
    - Overall risk score
    - Alert counts and statistics
    - Current traffic metrics
    - Top threatened assets
    - Recent alerts
    """
    # Get alert statistics - USE TOTAL ALERTS NOT JUST ACTIVE
    all_alerts_data = AlertService.get_recent_alerts(db, limit=1000)  # Get all
    active_alerts = len(all_alerts_data)  # Total count for consistency
    critical_threats = AlertService.get_critical_threat_count(db)
    alerts_by_severity = AlertService.get_alert_counts_by_severity(db)
    alerts_by_status = AlertService.get_alert_counts_by_status(db)

    # Get recent alerts - same source as Threat Alerts page
    recent_alerts_data = AlertService.get_recent_alerts(db, limit=6)
    recent_alerts = [
        {
            'id': alert.id,
            'time': alert.timestamp.strftime('%H:%M:%S'),
            'threat': alert.threat_class,
            'source': alert.src_ip,
            'destination': f"{alert.dst_ip}:{alert.dst_port}",
            'severity': alert.severity.value,
            'confidence': alert.confidence,
            'status': alert.status.value
        }
        for alert in recent_alerts_data
    ]

    # Get current flow rate
    current_metric = MetricService.get_current_metric(db)
    current_flow_rate = current_metric.flows_per_second if current_metric else 0.0

    # Get top threatened assets
    top_assets = AssetService.get_top_threatened_assets(db, limit=5)

    # Use current alert risk rather than a fixed baseline so a quiet network
    # does not appear risky and newly generated alerts change the score.
    if all_alerts_data:
        average_alert_risk = sum(alert.risk_score for alert in all_alerts_data) / len(all_alerts_data)
        risk_score = min(
            100,
            round(average_alert_risk + (critical_threats * 5))
        )
    else:
        risk_score = 0

    return DashboardSummary(
        risk_score=risk_score,
        active_alerts=active_alerts,
        critical_threats=critical_threats,
        current_flow_rate=current_flow_rate,
        alerts_by_severity=alerts_by_severity,
        alerts_by_status=alerts_by_status,
        top_threatened_assets=top_assets,
        recent_alerts=recent_alerts
    )

"""
Dashboard API endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, List, Any

from database.base import get_db
from schemas.dashboard import DashboardSummary
from services.alert_service import AlertService
from services.metric_service import MetricService
from services.asset_service import AssetService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummary:
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
    critical_threats = int(AlertService.get_critical_threat_count(db))

    # Get severity counts - ensure plain Python ints
    raw_severity = AlertService.get_alert_counts_by_severity(db)
    alerts_by_severity: Dict[str, int] = {}
    for k, v in raw_severity.items():
        alerts_by_severity[str(k)] = int(v)

    # Get status counts - ensure plain Python ints
    raw_status = AlertService.get_alert_counts_by_status(db)
    alerts_by_status: Dict[str, int] = {}
    for k, v in raw_status.items():
        alerts_by_status[str(k)] = int(v)

    # Get recent alerts - same source as Threat Alerts page
    recent_alerts_data = AlertService.get_recent_alerts(db, limit=6)
    recent_alerts: List[Dict[str, Any]] = []
    for alert in recent_alerts_data:
        recent_alerts.append({
            'id': int(alert.id),
            'time': alert.timestamp.strftime('%H:%M:%S'),
            'threat': alert.threat_class or 'Unknown',
            'source': alert.src_ip or '0.0.0.0',
            'destination': f"{alert.dst_ip or '0.0.0.0'}:{alert.dst_port or 0}",
            'severity': alert.severity.value if hasattr(alert.severity, 'value') else str(alert.severity),
            'confidence': float(alert.confidence) if alert.confidence else 0.0,
            'status': alert.status.value if hasattr(alert.status, 'value') else str(alert.status)
        })

    # Get current flow rate
    current_metric = MetricService.get_current_metric(db)
    current_flow_rate = 0.0
    if current_metric is not None:
        cf = current_metric.flows_per_second
        current_flow_rate = float(cf) if cf is not None else 0.0

    average_flow_rate = MetricService.get_average_flow_rate(db, hours=24)
    average_flow_rate = float(average_flow_rate) if average_flow_rate is not None else 0.0

    # Get top threatened assets - extract plain Python dicts
    top_threatened_assets: List[Dict[str, Any]] = []
    for asset in AssetService.get_top_threatened_assets(db, limit=5):
        asset_dict: Dict[str, Any] = {}
        for k, v in asset.items():
            if isinstance(v, int):
                asset_dict[str(k)] = v
            elif isinstance(v, float):
                asset_dict[str(k)] = v
            elif isinstance(v, str):
                asset_dict[str(k)] = v
            else:
                asset_dict[str(k)] = str(v)
        top_threatened_assets.append(asset_dict)

    # Estimate risk from both observed threats and traffic deviation. A rate
    # close to the recent baseline contributes little; an unusual spike or
    # drop contributes more without treating normal traffic as a threat.
    alert_risk = 0
    if all_alerts_data:
        risk_sum = 0
        for alert in all_alerts_data:
            risk_sum += int(alert.risk_score)
        average_alert_risk = risk_sum / len(all_alerts_data)
        alert_risk = min(60, round((average_alert_risk * 0.6) + (critical_threats * 5)))

    traffic_risk = 0
    if average_flow_rate > 0 and current_flow_rate > 0:
        traffic_deviation = abs(current_flow_rate - average_flow_rate) / average_flow_rate
        traffic_risk = min(40, round(traffic_deviation * 100))

    risk_score = min(100, alert_risk + traffic_risk)

    # Explicitly construct the model with only plain Python types
    return DashboardSummary(
        risk_score=risk_score,
        active_alerts=active_alerts,
        critical_threats=critical_threats,
        current_flow_rate=current_flow_rate,
        alerts_by_severity=alerts_by_severity,
        alerts_by_status=alerts_by_status,
        top_threatened_assets=top_threatened_assets,
        recent_alerts=recent_alerts
    )
"""
Pydantic schemas for Dashboard API endpoints.
"""
from pydantic import BaseModel
from typing import Dict, Any


class DashboardSummary(BaseModel):
    """Schema for dashboard summary response."""
    risk_score: int
    active_alerts: int
    critical_threats: int
    current_flow_rate: float
    alerts_by_severity: Dict[str, int]
    alerts_by_status: Dict[str, int]
    top_threatened_assets: list[Dict[str, Any]]
    recent_alerts: list[Dict[str, Any]]

"""
Pydantic schemas for Alert API endpoints.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class AlertStatus(str, Enum):
    """Alert status enumeration."""
    ACTIVE = "Active"
    INVESTIGATING = "Investigating"
    ACKNOWLEDGED = "Acknowledged"
    RESOLVED = "Resolved"
    BLOCKED = "Blocked"


class AlertSeverity(str, Enum):
    """Alert severity enumeration."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class AlertBase(BaseModel):
    """Base alert schema with common fields."""
    threat_class: str
    severity: AlertSeverity
    confidence: float = Field(ge=0.0, le=1.0)
    risk_score: int = Field(ge=0, le=100)
    src_ip: str
    dst_ip: str
    src_port: Optional[str] = None
    dst_port: str
    protocol: str


class AlertCreate(AlertBase):
    """Schema for creating a new alert."""
    timestamp: datetime
    flow_id: str
    status: AlertStatus = AlertStatus.ACTIVE
    evidence_json: Optional[str] = None


class AlertUpdate(BaseModel):
    """Schema for updating alert status."""
    status: AlertStatus


class AlertResponse(AlertBase):
    """Schema for alert API responses."""
    id: int
    timestamp: datetime
    flow_id: str
    status: AlertStatus
    evidence_json: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class AlertListResponse(BaseModel):
    """Schema for paginated alert list responses."""
    total: int
    alerts: list[AlertResponse]

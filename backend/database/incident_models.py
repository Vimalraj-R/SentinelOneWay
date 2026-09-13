"""
Database models for attack correlation and incidents.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum, JSON
from sqlalchemy.sql import func
from datetime import datetime
import enum

from .base import Base


class IncidentSeverity(str, enum.Enum):
    """Incident severity enumeration."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class IncidentStatus(str, enum.Enum):
    """Incident status enumeration."""
    ACTIVE = "Active"
    INVESTIGATING = "Investigating"
    CONTAINED = "Contained"
    RESOLVED = "Resolved"


class AttackStage(str, enum.Enum):
    """Attack stage enumeration based on cyber kill chain."""
    RECONNAISSANCE = "Reconnaissance"
    INITIAL_ACCESS = "Initial Access"
    EXECUTION = "Execution"
    PERSISTENCE = "Persistence"
    PRIVILEGE_ESCALATION = "Privilege Escalation"
    DEFENSE_EVASION = "Defense Evasion"
    CREDENTIAL_ACCESS = "Credential Access"
    DISCOVERY = "Discovery"
    LATERAL_MOVEMENT = "Lateral Movement"
    COLLECTION = "Collection"
    COMMAND_AND_CONTROL = "Command and Control"
    EXFILTRATION = "Exfiltration"
    IMPACT = "Impact"


class Incident(Base):
    """
    Incident model - correlated attack story from multiple alerts.

    Represents a higher-level security incident composed of
    multiple related alerts that form a coherent attack pattern.
    """
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(100), unique=True, nullable=False, index=True)

    # Temporal information
    start_time = Column(DateTime, nullable=False, index=True)
    last_updated = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    duration_minutes = Column(Float, nullable=True)  # Duration in minutes

    # Risk and severity
    risk_score = Column(Integer, nullable=False)  # 0-100
    severity = Column(Enum(IncidentSeverity), nullable=False, index=True)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.ACTIVE, nullable=False, index=True)

    # Attack characteristics
    attack_pattern = Column(String(200), nullable=False)  # e.g., "Multi-stage compromise"
    attack_stages_json = Column(Text, nullable=False)  # JSON list of attack stages
    summary = Column(Text, nullable=False)  # Human-readable summary

    # Affected entities
    affected_assets = Column(Text, nullable=False)  # JSON list of affected IPs/hostnames
    source_ips = Column(Text, nullable=False)  # JSON list of source IPs
    destination_ips = Column(Text, nullable=False)  # JSON list of destination IPs

    # Related alerts
    related_alert_ids = Column(Text, nullable=False)  # JSON list of alert IDs
    alert_count = Column(Integer, nullable=False)

    # Correlation metadata
    correlation_confidence = Column(Float, nullable=False)  # 0.0-1.0
    correlation_factors = Column(Text, nullable=True)  # JSON dict of correlation evidence

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Incident(id={self.incident_id}, pattern={self.attack_pattern}, alerts={self.alert_count})>"

"""
SQLAlchemy database models for SentinelOneWay.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum
from sqlalchemy.sql import func
from datetime import datetime
import enum

from .base import Base


class AlertStatus(str, enum.Enum):
    """Alert status enumeration."""
    ACTIVE = "Active"
    INVESTIGATING = "Investigating"
    ACKNOWLEDGED = "Acknowledged"
    RESOLVED = "Resolved"
    BLOCKED = "Blocked"


class AlertSeverity(str, enum.Enum):
    """Alert severity enumeration."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class AssetCriticality(str, enum.Enum):
    """Asset criticality enumeration."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Alert(Base):
    """
    Alert model - stores detected security threats.

    Represents a security event detected by SentinelOneWay's
    monitoring system. Contains network flow information,
    threat classification, and investigation details.
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    flow_id = Column(String(50), unique=True, nullable=False, index=True)

    # Threat Information
    threat_class = Column(String(100), nullable=False, index=True)
    severity = Column(Enum(AlertSeverity), nullable=False, index=True)
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    risk_score = Column(Integer, nullable=False)  # 0 to 100

    # Network Information
    src_ip = Column(String(45), nullable=False, index=True)  # Supports IPv6
    dst_ip = Column(String(45), nullable=False, index=True)
    src_port = Column(String(20), nullable=True)
    dst_port = Column(String(20), nullable=False)
    protocol = Column(String(20), nullable=False)

    # Investigation
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE, nullable=False, index=True)
    evidence_json = Column(Text, nullable=True)  # JSON string with detection evidence

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Alert(id={self.id}, threat={self.threat_class}, severity={self.severity}, status={self.status})>"


class NetworkMetric(Base):
    """
    NetworkMetric model - stores network traffic statistics.

    Captures aggregate network metrics over time for monitoring
    and baseline establishment.
    """
    __tablename__ = "network_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True, default=func.now())

    # Traffic Volume
    flows_per_second = Column(Float, nullable=False)
    packets_per_second = Column(Float, nullable=False)
    bytes_per_second = Column(Float, nullable=False)

    # Protocol Distribution (percentages)
    tcp_percentage = Column(Float, nullable=False)
    udp_percentage = Column(Float, nullable=False)
    dns_percentage = Column(Float, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f"<NetworkMetric(timestamp={self.timestamp}, flows/s={self.flows_per_second})>"


class Asset(Base):
    """
    Asset model - stores network asset inventory.

    Represents monitored network assets including servers,
    workstations, and network devices.
    """
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), unique=True, nullable=False, index=True)
    hostname = Column(String(255), nullable=False)
    asset_type = Column(String(50), nullable=False)  # server, workstation, network_device, etc.
    criticality = Column(Enum(AssetCriticality), nullable=False, index=True)
    risk_score = Column(Integer, default=0, nullable=False)  # 0 to 100

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Asset(hostname={self.hostname}, ip={self.ip_address}, criticality={self.criticality})>"

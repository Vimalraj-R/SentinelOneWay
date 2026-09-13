"""
Pydantic schemas for Network Metric API endpoints.
"""
from pydantic import BaseModel, Field
from datetime import datetime


class NetworkMetricBase(BaseModel):
    """Base network metric schema."""
    flows_per_second: float = Field(ge=0)
    packets_per_second: float = Field(ge=0)
    bytes_per_second: float = Field(ge=0)
    tcp_percentage: float = Field(ge=0, le=100)
    udp_percentage: float = Field(ge=0, le=100)
    dns_percentage: float = Field(ge=0, le=100)


class NetworkMetricCreate(NetworkMetricBase):
    """Schema for creating a new network metric."""
    timestamp: datetime


class NetworkMetricResponse(NetworkMetricBase):
    """Schema for network metric API responses."""
    id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class NetworkMetricHistoryResponse(BaseModel):
    """Schema for network metric history responses."""
    total: int
    metrics: list[NetworkMetricResponse]

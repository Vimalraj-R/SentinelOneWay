"""
Pydantic schemas for Simulation API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class SimulationStartRequest(BaseModel):
    """Schema for starting simulation."""
    scenario: str = Field(
        ...,
        description="Scenario to simulate: normal, syn_flood, port_scan, c2_beacon, dns_tunnel, data_exfiltration"
    )
    intensity: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Simulation intensity (0.0 to 1.0)"
    )


class SimulationStatusResponse(BaseModel):
    """Schema for simulation status response."""
    state: str
    scenario: Optional[str] = None
    intensity: Optional[float] = None
    total_flows_generated: int
    flows_in_memory: int
    duration_seconds: Optional[float] = None
    flows_per_second: Optional[float] = None


class SimulationStartResponse(BaseModel):
    """Schema for simulation start response."""
    status: str
    scenario: str
    intensity: float
    start_time: str


class SimulationStopResponse(BaseModel):
    """Schema for simulation stop response."""
    status: str
    scenario: Optional[str] = None
    duration_seconds: Optional[float] = None
    total_flows_generated: Optional[int] = None
    flows_available: Optional[int] = None
    message: Optional[str] = None


class FlowRecordResponse(BaseModel):
    """Schema for flow record response."""
    timestamp: datetime
    flow_id: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    packet_count: int
    byte_count: int
    duration: float
    syn_count: int
    ack_count: int
    inbound_bytes: int
    outbound_bytes: int
    dns_query: Optional[str] = None
    tls_fingerprint: Optional[str] = None

    class Config:
        from_attributes = True


class FlowListResponse(BaseModel):
    """Schema for flow list response."""
    total: int
    flows: List[FlowRecordResponse]

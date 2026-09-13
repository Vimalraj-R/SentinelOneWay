"""
Flow record data structure for network traffic simulation.

This module defines the structure of synthetic network flow records
used for testing and development of detection algorithms.
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class FlowRecord:
    """
    Synthetic network flow record.

    Represents metadata about a network flow for simulation purposes.
    This is NOT real network traffic - it's synthetic data for testing.
    """
    timestamp: datetime
    flow_id: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str  # TCP, UDP, ICMP
    packet_count: int
    byte_count: int
    duration: float  # seconds
    syn_count: int
    ack_count: int
    inbound_bytes: int
    outbound_bytes: int
    dns_query: Optional[str] = None
    tls_fingerprint: Optional[str] = None

    def to_dict(self):
        """Convert flow record to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    def get_syn_ack_ratio(self) -> float:
        """Calculate SYN/ACK ratio."""
        if self.ack_count == 0:
            return float('inf') if self.syn_count > 0 else 0.0
        return self.syn_count / self.ack_count

    def get_outbound_inbound_ratio(self) -> float:
        """Calculate outbound/inbound byte ratio."""
        if self.inbound_bytes == 0:
            return float('inf') if self.outbound_bytes > 0 else 0.0
        return self.outbound_bytes / self.inbound_bytes

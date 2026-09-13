"""
Detection configuration and thresholds.

Provides configurable thresholds for rule-based threat detection.
All magic numbers should be defined here for easy tuning.
"""
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class SynFloodThresholds:
    """Thresholds for SYN flood detection."""

    # SYN/ACK ratio threshold
    syn_ack_ratio_high: float = 10.0
    syn_ack_ratio_critical: float = 50.0

    # Packet rate threshold (packets/sec)
    packet_rate_high: float = 500.0
    packet_rate_critical: float = 2000.0

    # Source IP entropy threshold
    source_entropy_medium: float = 3.0
    source_entropy_high: float = 5.0

    # Destination concentration threshold
    dest_concentration_high: float = 0.8
    dest_concentration_critical: float = 0.95

    # Minimum flows required for aggregate detection
    min_flows_for_detection: int = 10

    # Average packet size threshold (small packets = SYN)
    small_packet_size: float = 100.0


@dataclass
class PortScanThresholds:
    """Thresholds for port scan detection."""

    # Unique destination ports threshold
    unique_ports_medium: int = 50
    unique_ports_high: int = 100
    unique_ports_critical: int = 500

    # Connection rate threshold (connections/sec)
    connection_rate_medium: float = 10.0
    connection_rate_high: float = 50.0

    # Fanout score threshold (destinations per source)
    fanout_medium: float = 10.0
    fanout_high: float = 50.0

    # Average flow duration (short flows)
    short_flow_duration: float = 1.0
    very_short_flow_duration: float = 0.1

    # Minimum flows required for detection
    min_flows_for_detection: int = 20

    # Successful connection ratio (low = scan)
    low_success_ratio: float = 0.2


@dataclass
class C2BeaconThresholds:
    """Thresholds for C2 beacon detection."""

    # Periodicity score threshold (0.0 to 1.0)
    periodicity_medium: float = 0.7
    periodicity_high: float = 0.85
    periodicity_critical: float = 0.95

    # Coefficient of variation threshold (low = regular)
    cv_low: float = 0.1
    cv_very_low: float = 0.05

    # Repeated destination count threshold
    repeated_dest_medium: int = 5
    repeated_dest_high: int = 10

    # Inter-arrival time variance threshold (seconds)
    timing_variance_low: float = 5.0
    timing_variance_very_low: float = 2.0

    # Common beacon intervals (seconds)
    common_beacon_intervals: list = field(default_factory=lambda: [
        60.0,    # 1 minute
        120.0,   # 2 minutes
        300.0,   # 5 minutes
        600.0,   # 10 minutes
        3600.0,  # 1 hour
    ])

    # Tolerance for interval matching (seconds)
    interval_tolerance: float = 5.0

    # Minimum flows required for detection
    min_flows_for_detection: int = 5


@dataclass
class DetectionConfig:
    """
    Master detection configuration.

    Provides configurable thresholds for all detectors.
    Tune these values based on your network environment.
    """

    syn_flood: SynFloodThresholds = field(default_factory=SynFloodThresholds)
    port_scan: PortScanThresholds = field(default_factory=PortScanThresholds)
    c2_beacon: C2BeaconThresholds = field(default_factory=C2BeaconThresholds)

    # Global settings
    confidence_aggregation_weight: float = 0.7  # Weight for combining multiple signals

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return {
            'syn_flood': self.syn_flood.__dict__,
            'port_scan': self.port_scan.__dict__,
            'c2_beacon': self.c2_beacon.__dict__,
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'DetectionConfig':
        """Load configuration from dictionary."""
        config = cls()

        if 'syn_flood' in config_dict:
            for key, value in config_dict['syn_flood'].items():
                if hasattr(config.syn_flood, key):
                    setattr(config.syn_flood, key, value)

        if 'port_scan' in config_dict:
            for key, value in config_dict['port_scan'].items():
                if hasattr(config.port_scan, key):
                    setattr(config.port_scan, key, value)

        if 'c2_beacon' in config_dict:
            for key, value in config_dict['c2_beacon'].items():
                if hasattr(config.c2_beacon, key):
                    setattr(config.c2_beacon, key, value)

        return config


# Default configuration instance
DEFAULT_CONFIG = DetectionConfig()

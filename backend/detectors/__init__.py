"""
Rule-based threat detection module for SentinelOneWay.

Provides baseline detectors that use configurable thresholds
to identify network threats. These detectors complement ML models
and provide explainable threat detection.
"""
from .config import DetectionConfig
from .syn_flood import SynFloodDetector
from .port_scan import PortScanDetector
from .c2_beacon import C2BeaconDetector

__all__ = [
    'DetectionConfig',
    'SynFloodDetector',
    'PortScanDetector',
    'C2BeaconDetector',
]

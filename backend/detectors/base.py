"""
Base classes and utilities for threat detectors.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class ThreatClass(str, Enum):
    """Threat classification types."""
    SYN_FLOOD = "SYN Flood"
    PORT_SCAN = "Port Scan"
    C2_BEACON = "C2 Beacon"
    DNS_TUNNEL = "DNS Tunnel"
    DATA_EXFILTRATION = "Data Exfiltration"


class Severity(str, Enum):
    """Threat severity levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass
class Detection:
    """
    Structured threat detection result.

    Attributes:
        threat_class: Type of threat detected
        confidence: Detection confidence (0.0 to 1.0)
        severity: Threat severity level
        evidence: Dictionary of evidence supporting detection
        human_explanation: List of human-readable explanation strings
    """
    threat_class: str
    confidence: float
    severity: str
    evidence: Dict[str, Any]
    human_explanation: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert detection to dictionary."""
        return {
            'threat_class': self.threat_class,
            'confidence': self.confidence,
            'severity': self.severity,
            'evidence': self.evidence,
            'human_explanation': self.human_explanation,
        }


class BaseDetector:
    """
    Base class for threat detectors.

    All detectors should inherit from this class and implement
    the detect() method.
    """

    def __init__(self, config: Optional[Any] = None):
        """
        Initialize detector.

        Args:
            config: Detector-specific configuration with thresholds
        """
        self.config = config

    def detect(self, features: Dict[str, float],
               aggregate_features: Optional[Dict[str, float]] = None) -> Optional[Detection]:
        """
        Detect threat based on features.

        Args:
            features: Single-flow or batch features
            aggregate_features: Optional aggregate features from multiple flows

        Returns:
            Detection object if threat detected, None otherwise
        """
        raise NotImplementedError("Subclasses must implement detect()")

    def _calculate_confidence(self, signals: List[float]) -> float:
        """
        Calculate overall confidence from multiple signals.

        Args:
            signals: List of confidence values (0.0 to 1.0)

        Returns:
            Combined confidence score
        """
        if not signals:
            return 0.0

        # Use weighted average with exponential weighting
        # Higher signals contribute more
        sorted_signals = sorted(signals, reverse=True)
        weights = [0.5 ** i for i in range(len(sorted_signals))]
        weighted_sum = sum(s * w for s, w in zip(sorted_signals, weights))
        weight_sum = sum(weights)

        return min(1.0, weighted_sum / weight_sum)

    def _determine_severity(self, confidence: float,
                           critical_threshold: float = 0.9,
                           high_threshold: float = 0.7,
                           medium_threshold: float = 0.5) -> str:
        """
        Determine severity based on confidence.

        Args:
            confidence: Detection confidence
            critical_threshold: Threshold for critical severity
            high_threshold: Threshold for high severity
            medium_threshold: Threshold for medium severity

        Returns:
            Severity level string
        """
        if confidence >= critical_threshold:
            return Severity.CRITICAL.value
        elif confidence >= high_threshold:
            return Severity.HIGH.value
        elif confidence >= medium_threshold:
            return Severity.MEDIUM.value
        else:
            return Severity.LOW.value

    def _normalize_score(self, value: float, low: float, high: float) -> float:
        """
        Normalize a value to 0.0-1.0 range.

        Args:
            value: Value to normalize
            low: Low threshold (maps to 0.0)
            high: High threshold (maps to 1.0)

        Returns:
            Normalized score (0.0 to 1.0)
        """
        if value <= low:
            return 0.0
        elif value >= high:
            return 1.0
        else:
            return (value - low) / (high - low)

"""
Port Scan Detector.

Detects port scanning reconnaissance by analyzing:
- High number of unique destination ports
- High fanout (many destinations per source)
- Short flow durations
- High connection rate
- Low successful connection ratio
"""
from typing import Dict, Optional, List

from .base import BaseDetector, Detection, ThreatClass
from .config import PortScanThresholds, DEFAULT_CONFIG


class PortScanDetector(BaseDetector):
    """
    Detector for port scanning attacks.

    Port scans are characterized by:
    - Many unique destination ports from single source
    - Very short flow durations
    - High connection rate
    - Low successful connection rate (few ACKs)
    - High fanout score
    """

    def __init__(self, config: Optional[PortScanThresholds] = None):
        """
        Initialize port scan detector.

        Args:
            config: Threshold configuration
        """
        super().__init__(config or DEFAULT_CONFIG.port_scan)

    def detect(self, features: Dict[str, float],
               aggregate_features: Optional[Dict[str, float]] = None) -> Optional[Detection]:
        """
        Detect port scan attack.

        Note: Port scans are primarily detected using aggregate features,
        as they manifest as patterns across multiple flows.

        Args:
            features: Flow features (can be single or batch mean)
            aggregate_features: Aggregate features from multiple flows

        Returns:
            Detection if port scan detected, None otherwise
        """
        # Port scans require aggregate features
        if not aggregate_features:
            return None

        signals = []
        evidence = {}
        explanations = []

        # Signal 1: Unique destination ports (primary indicator)
        unique_ports = aggregate_features.get('unique_destination_ports', 0)
        if unique_ports > self.config.unique_ports_medium:
            port_signal = self._normalize_score(
                unique_ports,
                self.config.unique_ports_medium,
                self.config.unique_ports_critical
            )
            signals.append(port_signal)
            evidence['unique_destination_ports'] = int(unique_ports)

            if unique_ports > self.config.unique_ports_critical:
                explanations.append(
                    f"Scanning {int(unique_ports)} unique ports indicates "
                    "aggressive reconnaissance"
                )
            elif unique_ports > self.config.unique_ports_high:
                explanations.append(
                    f"Probing {int(unique_ports)} unique ports suggests "
                    "systematic port scan"
                )
            else:
                explanations.append(
                    f"Testing {int(unique_ports)} ports shows "
                    "reconnaissance behavior"
                )

        # Signal 2: Connection rate
        connection_rate = aggregate_features.get('connection_rate', 0.0)
        if connection_rate > self.config.connection_rate_medium:
            rate_signal = self._normalize_score(
                connection_rate,
                self.config.connection_rate_medium,
                self.config.connection_rate_high
            )
            signals.append(rate_signal)
            evidence['connection_rate'] = connection_rate
            explanations.append(
                f"High connection rate ({connection_rate:.1f} connections/sec) "
                "typical of automated scanning"
            )

        # Signal 3: Fanout score
        fanout = aggregate_features.get('fanout_score', 0.0)
        if fanout > self.config.fanout_medium:
            fanout_signal = self._normalize_score(
                fanout,
                self.config.fanout_medium,
                self.config.fanout_high
            )
            signals.append(fanout_signal)
            evidence['fanout_score'] = fanout
            explanations.append(
                f"Single source targeting multiple destinations "
                f"(fanout {fanout:.1f}) indicates network mapping"
            )

        # Signal 4: Flow duration (from features)
        flow_duration = features.get('flow_duration', 10.0)
        if flow_duration < self.config.short_flow_duration:
            duration_signal = 1.0 - (flow_duration / self.config.short_flow_duration)
            signals.append(duration_signal)
            evidence['average_flow_duration'] = flow_duration

            if flow_duration < self.config.very_short_flow_duration:
                explanations.append(
                    f"Extremely short flows ({flow_duration:.3f}s) "
                    "consistent with rapid probing"
                )
            else:
                explanations.append(
                    f"Brief connections ({flow_duration:.2f}s) "
                    "suggest quick service checks"
                )

        # Signal 5: SYN/ACK ratio (low success rate)
        syn_ack_ratio = features.get('syn_ack_ratio', 1.0)
        # For scans, we expect low ACK counts (unsuccessful connections)
        # If ratio is close to 1, it means roughly equal SYN/ACK (successful)
        # If ratio is high, it means many SYNs with few ACKs (scan)
        if syn_ack_ratio > 2.0:  # More SYNs than ACKs
            success_signal = min(1.0, (syn_ack_ratio - 2.0) / 10.0)
            signals.append(success_signal)
            evidence['syn_ack_ratio'] = syn_ack_ratio
            explanations.append(
                f"Low successful connection rate (SYN/ACK ratio {syn_ack_ratio:.1f}) "
                "indicates probing closed ports"
            )

        # Require at least 2 signals for detection
        if len(signals) < 2:
            return None

        # Calculate confidence
        confidence = self._calculate_confidence(signals)

        # Determine severity
        severity = self._determine_severity(confidence)

        # Build summary
        summary = (
            f"Detected port scan with {len(signals)} indicators. "
            f"Scanned {int(unique_ports)} unique ports. "
        )
        if connection_rate > self.config.connection_rate_medium:
            summary += f"Connection rate: {connection_rate:.1f}/sec. "

        explanations.insert(0, summary)

        return Detection(
            threat_class=ThreatClass.PORT_SCAN.value,
            confidence=confidence,
            severity=severity,
            evidence=evidence,
            human_explanation=explanations
        )

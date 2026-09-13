"""
SYN Flood Detector.

Detects SYN flood DDoS attacks by analyzing:
- High SYN/ACK ratios
- High packet rates
- Small packet sizes
- High source diversity (aggregate)
- High destination concentration (aggregate)
"""
from typing import Dict, Optional, List

from .base import BaseDetector, Detection, ThreatClass
from .config import SynFloodThresholds, DEFAULT_CONFIG


class SynFloodDetector(BaseDetector):
    """
    Detector for SYN flood DDoS attacks.

    SYN floods are characterized by:
    - Very high SYN packet count with few ACKs
    - Small packet sizes (just TCP headers)
    - High packet rates
    - Many diverse sources targeting one destination (aggregate)
    """

    def __init__(self, config: Optional[SynFloodThresholds] = None):
        """
        Initialize SYN flood detector.

        Args:
            config: Threshold configuration
        """
        super().__init__(config or DEFAULT_CONFIG.syn_flood)

    def detect(self, features: Dict[str, float],
               aggregate_features: Optional[Dict[str, float]] = None) -> Optional[Detection]:
        """
        Detect SYN flood attack.

        Args:
            features: Flow features (can be from single flow or mean of batch)
            aggregate_features: Optional aggregate features from multiple flows

        Returns:
            Detection if SYN flood detected, None otherwise
        """
        signals = []
        evidence = {}
        explanations = []

        # Signal 1: SYN/ACK ratio
        syn_ack_ratio = features.get('syn_ack_ratio', 0.0)
        if syn_ack_ratio > self.config.syn_ack_ratio_high:
            ratio_signal = self._normalize_score(
                syn_ack_ratio,
                self.config.syn_ack_ratio_high,
                self.config.syn_ack_ratio_critical
            )
            signals.append(ratio_signal)
            evidence['syn_ack_ratio'] = syn_ack_ratio

            if syn_ack_ratio > self.config.syn_ack_ratio_critical:
                explanations.append(
                    f"Extremely high SYN/ACK ratio ({syn_ack_ratio:.1f}) indicates "
                    "incomplete TCP handshakes typical of SYN flood"
                )
            else:
                explanations.append(
                    f"High SYN/ACK ratio ({syn_ack_ratio:.1f}) suggests "
                    "abnormal connection attempts"
                )

        # Signal 2: Packet rate
        packet_rate = features.get('packets_per_second', 0.0)
        if packet_rate > self.config.packet_rate_high:
            rate_signal = self._normalize_score(
                packet_rate,
                self.config.packet_rate_high,
                self.config.packet_rate_critical
            )
            signals.append(rate_signal)
            evidence['packet_rate'] = packet_rate
            explanations.append(
                f"Very high packet rate ({packet_rate:.0f} pps) "
                "consistent with volumetric attack"
            )

        # Signal 3: Small packet size
        avg_packet_size = features.get('average_packet_size', 1500.0)
        if avg_packet_size < self.config.small_packet_size:
            size_signal = 1.0 - (avg_packet_size / self.config.small_packet_size)
            signals.append(size_signal)
            evidence['average_packet_size'] = avg_packet_size
            explanations.append(
                f"Small packet size ({avg_packet_size:.0f} bytes) "
                "indicates header-only SYN packets"
            )

        # Aggregate signals (if available)
        if aggregate_features:
            # Signal 4: Source IP entropy (high = distributed attack)
            source_entropy = aggregate_features.get('source_ip_entropy', 0.0)
            if source_entropy > self.config.source_entropy_medium:
                entropy_signal = self._normalize_score(
                    source_entropy,
                    self.config.source_entropy_medium,
                    self.config.source_entropy_high
                )
                signals.append(entropy_signal)
                evidence['source_ip_entropy'] = source_entropy
                explanations.append(
                    f"High source diversity (entropy {source_entropy:.2f}) "
                    "suggests distributed attack from many sources"
                )

            # Signal 5: Destination concentration (high = single target)
            dest_concentration = aggregate_features.get('destination_concentration', 0.0)
            if dest_concentration > self.config.dest_concentration_high:
                conc_signal = self._normalize_score(
                    dest_concentration,
                    self.config.dest_concentration_high,
                    self.config.dest_concentration_critical
                )
                signals.append(conc_signal)
                evidence['destination_concentration'] = dest_concentration
                explanations.append(
                    f"Traffic concentrated on single target "
                    f"({dest_concentration:.0%} of flows) typical of DDoS"
                )

        # Require at least 2 signals for detection
        if len(signals) < 2:
            return None

        # Calculate confidence
        confidence = self._calculate_confidence(signals)

        # Determine severity
        severity = self._determine_severity(confidence)

        # Build human-readable summary
        summary = (
            f"Detected SYN flood attack with {len(signals)} indicators. "
            f"Primary evidence: "
        )
        if syn_ack_ratio > self.config.syn_ack_ratio_high:
            summary += f"SYN/ACK ratio {syn_ack_ratio:.1f}. "
        if packet_rate > self.config.packet_rate_high:
            summary += f"Packet rate {packet_rate:.0f} pps. "

        explanations.insert(0, summary)

        return Detection(
            threat_class=ThreatClass.SYN_FLOOD.value,
            confidence=confidence,
            severity=severity,
            evidence=evidence,
            human_explanation=explanations
        )

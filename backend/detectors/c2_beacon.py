"""
C2 Beacon Detector.

Detects Command & Control beaconing by analyzing:
- High periodicity (regular timing intervals)
- Low timing variance
- Repeated same destination
- Timing matches common beacon intervals
"""
from typing import Dict, Optional, List

from .base import BaseDetector, Detection, ThreatClass
from .config import C2BeaconThresholds, DEFAULT_CONFIG


class C2BeaconDetector(BaseDetector):
    """
    Detector for C2 beaconing communication.

    C2 beacons are characterized by:
    - Regular periodic connections
    - Low variance in inter-arrival times
    - Repeated connections to same destination
    - Timing matches common beacon intervals (60s, 120s, etc.)
    """

    def __init__(self, config: Optional[C2BeaconThresholds] = None):
        """
        Initialize C2 beacon detector.

        Args:
            config: Threshold configuration
        """
        super().__init__(config or DEFAULT_CONFIG.c2_beacon)

    def detect(self, features: Dict[str, float],
               aggregate_features: Optional[Dict[str, float]] = None) -> Optional[Detection]:
        """
        Detect C2 beacon activity.

        Note: C2 beacons require aggregate features to identify
        periodic patterns across multiple flows.

        Args:
            features: Flow features (single or batch mean)
            aggregate_features: Aggregate features from multiple flows

        Returns:
            Detection if C2 beacon detected, None otherwise
        """
        # C2 beacons require aggregate features
        if not aggregate_features:
            return None

        signals = []
        evidence = {}
        explanations = []

        # Signal 1: Periodicity score (primary indicator)
        periodicity = aggregate_features.get('periodicity_score', 0.0)
        if periodicity > self.config.periodicity_medium:
            period_signal = self._normalize_score(
                periodicity,
                self.config.periodicity_medium,
                self.config.periodicity_critical
            )
            signals.append(period_signal)
            evidence['periodicity_score'] = periodicity

            if periodicity > self.config.periodicity_critical:
                explanations.append(
                    f"Highly regular timing pattern (periodicity {periodicity:.3f}) "
                    "strongly indicates automated beaconing"
                )
            elif periodicity > self.config.periodicity_high:
                explanations.append(
                    f"Regular timing pattern (periodicity {periodicity:.3f}) "
                    "suggests automated communication"
                )
            else:
                explanations.append(
                    f"Moderate timing regularity (periodicity {periodicity:.3f}) "
                    "may indicate scheduled communication"
                )

        # Signal 2: Low timing variance
        inter_arrival_std = aggregate_features.get('inter_arrival_std', float('inf'))
        if inter_arrival_std < self.config.timing_variance_low:
            variance_signal = 1.0 - (inter_arrival_std / self.config.timing_variance_low)
            signals.append(variance_signal)
            evidence['inter_arrival_std'] = inter_arrival_std

            if inter_arrival_std < self.config.timing_variance_very_low:
                explanations.append(
                    f"Extremely consistent timing (std {inter_arrival_std:.2f}s) "
                    "typical of programmatic beaconing"
                )
            else:
                explanations.append(
                    f"Consistent timing (std {inter_arrival_std:.2f}s) "
                    "suggests non-human communication pattern"
                )

        # Signal 3: Repeated destination
        repeated_dest = aggregate_features.get('repeated_destination_count', 0)
        if repeated_dest > self.config.repeated_dest_medium:
            dest_signal = self._normalize_score(
                repeated_dest,
                self.config.repeated_dest_medium,
                self.config.repeated_dest_high
            )
            signals.append(dest_signal)
            evidence['repeated_destination_count'] = int(repeated_dest)
            explanations.append(
                f"Repeatedly contacting same destination ({int(repeated_dest)} times) "
                "indicates persistent connection pattern"
            )

        # Signal 4: Matches common beacon interval
        mean_interval = aggregate_features.get('mean_inter_arrival_time', 0.0)
        if mean_interval > 0:
            evidence['mean_inter_arrival_time'] = mean_interval

            # Check if interval matches common beacon intervals
            matched_interval = None
            for beacon_interval in self.config.common_beacon_intervals:
                if abs(mean_interval - beacon_interval) < self.config.interval_tolerance:
                    matched_interval = beacon_interval
                    break

            if matched_interval:
                signals.append(0.8)  # High confidence for matching known interval
                evidence['matched_beacon_interval'] = matched_interval
                explanations.append(
                    f"Timing interval ({mean_interval:.1f}s) matches "
                    f"common beacon interval ({matched_interval:.0f}s)"
                )
            else:
                # Still record the interval even if not common
                explanations.append(
                    f"Regular interval of {mean_interval:.1f}s between connections"
                )

        # Signal 5: Coefficient of variation (from periodicity calculation)
        # CV = std / mean, low CV means regular pattern
        if mean_interval > 0 and inter_arrival_std < float('inf'):
            cv = inter_arrival_std / mean_interval
            if cv < self.config.cv_low:
                cv_signal = 1.0 - (cv / self.config.cv_low)
                signals.append(cv_signal)
                evidence['coefficient_of_variation'] = cv
                explanations.append(
                    f"Low coefficient of variation ({cv:.3f}) "
                    "confirms highly regular timing"
                )

        # Require at least 2 signals for detection
        if len(signals) < 2:
            return None

        # Calculate confidence
        confidence = self._calculate_confidence(signals)

        # Determine severity
        # C2 beacons are typically high severity due to indicating compromise
        severity = self._determine_severity(
            confidence,
            critical_threshold=0.85,
            high_threshold=0.6,
            medium_threshold=0.4
        )

        # Build summary
        summary = (
            f"Detected C2 beacon with {len(signals)} indicators. "
        )
        if periodicity > self.config.periodicity_high:
            summary += f"Highly periodic communication (score {periodicity:.2f}). "
        if mean_interval > 0:
            summary += f"Regular {mean_interval:.1f}s intervals. "

        explanations.insert(0, summary)

        return Detection(
            threat_class=ThreatClass.C2_BEACON.value,
            confidence=confidence,
            severity=severity,
            evidence=evidence,
            human_explanation=explanations
        )

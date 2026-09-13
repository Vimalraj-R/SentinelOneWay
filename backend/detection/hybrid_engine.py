"""
Hybrid detection engine for SentinelOneWay.

Combines rule-based, supervised ML, and unsupervised anomaly detection
with transparent risk scoring logic.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict

from detection.classifier import get_classifier
from detection.anomaly_detector import get_anomaly_detector
from detectors.syn_flood import SynFloodDetector
from detectors.port_scan import PortScanDetector
from detectors.c2_beacon import C2BeaconDetector
from detectors.config import DetectionConfig
from detectors.base import Detection


@dataclass
class HybridDetectionResult:
    """
    Result from hybrid detection engine.

    Combines outputs from all detection methods with
    transparent risk scoring.
    """
    threat_class: str
    confidence: float
    anomaly_score: float
    risk_score: int  # 0-100
    severity: str
    evidence: Dict[str, Any]
    human_explanation: List[str]
    detectors_triggered: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class HybridDetectionEngine:
    """
    Hybrid detection engine combining multiple detection methods.

    Architecture:
        Flow Features
             ↓
        ┌────┴────┬────────────┐
        ↓         ↓            ↓
     Rules    Random     Isolation
               Forest      Forest
        ↓         ↓            ↓
    Statistical Known       Anomaly
    Evidence   Threat      Detection
        └────┬────┴────────────┘
             ↓
        Risk Engine
             ↓
        Final Classification
    """

    def __init__(self, config: Optional[DetectionConfig] = None):
        """
        Initialize hybrid engine.

        Args:
            config: Detection configuration (uses defaults if None)
        """
        self.config = config or DetectionConfig()

        # Initialize ML models
        self.classifier = get_classifier()
        self.anomaly_detector = get_anomaly_detector()

        # Initialize rule-based detectors
        self.syn_flood_detector = SynFloodDetector(self.config.syn_flood)
        self.port_scan_detector = PortScanDetector(self.config.port_scan)
        self.c2_beacon_detector = C2BeaconDetector(self.config.c2_beacon)

    def detect(self,
              single_flow_features: Dict[str, float],
              aggregate_features: Optional[Dict[str, float]] = None,
              ml_threshold: float = 0.7,
              anomaly_threshold: float = 50.0) -> HybridDetectionResult:
        """
        Run hybrid detection on network flow features.

        Args:
            single_flow_features: Features from single flow
            aggregate_features: Features from multiple flows (optional)
            ml_threshold: Confidence threshold for ML classification
            anomaly_threshold: Threshold for anomaly flagging (0-100)

        Returns:
            HybridDetectionResult with final classification
        """
        # Combine features for ML models
        all_features = {**single_flow_features}
        if aggregate_features:
            all_features.update(aggregate_features)

        # Run all detectors
        ml_result = self._run_ml_classifier(all_features)
        anomaly_result = self._run_anomaly_detector(all_features, anomaly_threshold)
        rule_detections = self._run_rule_detectors(single_flow_features, aggregate_features)

        # Apply hybrid decision logic
        threat_class, confidence, detectors = self._classify_threat(
            ml_result,
            anomaly_result,
            rule_detections,
            ml_threshold
        )

        # Calculate risk score
        risk_score = self._calculate_risk_score(
            ml_result,
            anomaly_result,
            rule_detections,
            threat_class
        )

        # Determine severity
        severity = self._determine_severity(risk_score, threat_class)

        # Build evidence
        evidence = self._build_evidence(
            ml_result,
            anomaly_result,
            rule_detections,
            single_flow_features,
            aggregate_features
        )

        # Generate human explanations
        explanations = self._generate_explanations(
            threat_class,
            confidence,
            anomaly_result['anomaly_score'],
            risk_score,
            rule_detections,
            ml_result,
            anomaly_result
        )

        return HybridDetectionResult(
            threat_class=threat_class,
            confidence=confidence,
            anomaly_score=anomaly_result['anomaly_score'],
            risk_score=risk_score,
            severity=severity,
            evidence=evidence,
            human_explanation=explanations,
            detectors_triggered=detectors
        )

    def _run_ml_classifier(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Run Random Forest classifier."""
        return self.classifier.predict_threat(features)

    def _run_anomaly_detector(self, features: Dict[str, float],
                              threshold: float) -> Dict[str, Any]:
        """Run Isolation Forest anomaly detector."""
        return self.anomaly_detector.predict_anomaly(features, threshold)

    def _run_rule_detectors(self,
                           single_flow: Dict[str, float],
                           aggregate: Optional[Dict[str, float]]) -> Dict[str, Optional[Detection]]:
        """
        Run all rule-based detectors.

        Returns:
            Dictionary mapping detector name to Detection (or None)
        """
        detections = {}

        # SYN flood detection
        try:
            detections['syn_flood'] = self.syn_flood_detector.detect(
                single_flow, aggregate
            )
        except Exception:
            detections['syn_flood'] = None

        # Port scan detection
        try:
            detections['port_scan'] = self.port_scan_detector.detect(
                single_flow, aggregate
            )
        except Exception:
            detections['port_scan'] = None

        # C2 beacon detection
        try:
            detections['c2_beacon'] = self.c2_beacon_detector.detect(
                single_flow, aggregate
            )
        except Exception:
            detections['c2_beacon'] = None

        return detections

    def _classify_threat(self,
                        ml_result: Dict[str, Any],
                        anomaly_result: Dict[str, Any],
                        rule_detections: Dict[str, Optional[Detection]],
                        ml_threshold: float) -> Tuple[str, float, List[str]]:
        """
        Apply hybrid decision logic to classify threat.

        Decision tree:

        1. High ML confidence (≥threshold) for attack class
           → Classify as that attack (KNOWN THREAT)

        2. Low ML confidence but high anomaly score
           → Classify as UNKNOWN_ANOMALY

        3. Rule detector triggered with high confidence
           → Classify as that attack type

        4. Multiple rule detectors agree
           → Classify as most confident rule detection

        5. Otherwise
           → Classify as NORMAL or SUSPICIOUS based on signals

        Args:
            ml_result: ML classifier output
            anomaly_result: Anomaly detector output
            rule_detections: Rule-based detection results
            ml_threshold: Confidence threshold for ML

        Returns:
            Tuple of (threat_class, confidence, detectors_triggered)
        """
        ml_class = ml_result['threat_class']
        ml_confidence = ml_result['confidence']
        is_anomaly = anomaly_result['is_anomaly']
        anomaly_score = anomaly_result['anomaly_score']

        detectors_triggered = []

        # Case 1: High confidence ML classification of known attack
        if ml_confidence >= ml_threshold and ml_class != "NORMAL":
            detectors_triggered.append('random_forest')

            # Check if rules agree
            rule_agrees = False
            for rule_name, detection in rule_detections.items():
                if detection and detection.threat_class == ml_class:
                    detectors_triggered.append(f'rule_{rule_name}')
                    rule_agrees = True

            # Higher confidence if rules agree
            final_confidence = ml_confidence
            if rule_agrees:
                final_confidence = min(1.0, ml_confidence * 1.1)

            return ml_class, final_confidence, detectors_triggered

        # Case 2: Rule detector with high confidence
        rule_classifications = []
        for rule_name, detection in rule_detections.items():
            if detection and detection.confidence >= 0.7:
                rule_classifications.append((
                    detection.threat_class,
                    detection.confidence,
                    f'rule_{rule_name}'
                ))

        if rule_classifications:
            # Use highest confidence rule
            rule_classifications.sort(key=lambda x: x[1], reverse=True)
            threat_class, confidence, detector = rule_classifications[0]

            detectors_triggered.append(detector)

            # Check if ML somewhat agrees
            if ml_class == threat_class and ml_confidence >= 0.5:
                detectors_triggered.append('random_forest')
                confidence = min(1.0, (confidence + ml_confidence) / 2 * 1.2)

            return threat_class, confidence, detectors_triggered

        # Case 3: Low ML confidence but high anomaly score
        if is_anomaly and anomaly_score >= 70.0 and ml_confidence < ml_threshold:
            detectors_triggered.append('isolation_forest')

            # Map anomaly score to confidence (70-100 → 0.7-1.0)
            confidence = (anomaly_score - 70.0) / 30.0 * 0.3 + 0.7

            return "UNKNOWN_ANOMALY", confidence, detectors_triggered

        # Case 4: Moderate ML confidence + anomaly
        if ml_confidence >= 0.5 and ml_confidence < ml_threshold and is_anomaly:
            detectors_triggered.extend(['random_forest', 'isolation_forest'])

            # Suspicious - might be attack variant
            return "SUSPICIOUS", ml_confidence * 0.8, detectors_triggered

        # Case 5: Anomaly without strong classification
        if is_anomaly:
            detectors_triggered.append('isolation_forest')
            confidence = min(0.7, anomaly_score / 100.0)
            return "SUSPICIOUS", confidence, detectors_triggered

        # Case 6: Normal
        detectors_triggered.append('random_forest')
        return "NORMAL", ml_confidence, detectors_triggered

    def _calculate_risk_score(self,
                             ml_result: Dict[str, Any],
                             anomaly_result: Dict[str, Any],
                             rule_detections: Dict[str, Optional[Detection]],
                             threat_class: str) -> int:
        """
        Calculate transparent risk score (0-100).

        Risk Scoring Logic:

        1. Base Risk (0-60):
           - ML confidence × 60
           - If threat_class is attack: use ML confidence directly
           - If UNKNOWN_ANOMALY: use anomaly_score / 100 × 60

        2. Anomaly Boost (+0 to +20):
           - If anomaly_score ≥ 80: +20
           - If anomaly_score ≥ 60: +15
           - If anomaly_score ≥ 40: +10
           - Otherwise: +0

        3. Rule Agreement Boost (+0 to +15):
           - Each rule detection adds: rule_confidence × 5
           - Cap at +15

        4. Multi-Detector Boost (+0 to +5):
           - 2 detectors: +2
           - 3 detectors: +4
           - 4+ detectors: +5

        Total: Capped at 100

        Args:
            ml_result: ML classifier output
            anomaly_result: Anomaly detector output
            rule_detections: Rule-based detections
            threat_class: Final classified threat class

        Returns:
            Risk score (0-100)
        """
        risk = 0.0

        # 1. Base risk from primary classification
        if threat_class in ["NORMAL", "SUSPICIOUS"]:
            # Use ML confidence for normal, lower for suspicious
            base_confidence = ml_result['confidence']
            if threat_class == "SUSPICIOUS":
                risk += base_confidence * 50  # 0-50 for suspicious
            else:
                risk += (1.0 - base_confidence) * 20  # Low risk for normal
        elif threat_class == "UNKNOWN_ANOMALY":
            # Base risk from anomaly score
            risk += anomaly_result['anomaly_score'] * 0.6  # 0-60
        else:
            # Known attack - base risk from ML confidence
            risk += ml_result['confidence'] * 60  # 0-60

        # 2. Anomaly boost
        anomaly_score = anomaly_result['anomaly_score']
        if anomaly_score >= 80:
            risk += 20
        elif anomaly_score >= 60:
            risk += 15
        elif anomaly_score >= 40:
            risk += 10

        # 3. Rule agreement boost
        rule_boost = 0.0
        for detection in rule_detections.values():
            if detection:
                rule_boost += detection.confidence * 5
        rule_boost = min(15, rule_boost)
        risk += rule_boost

        # 4. Multi-detector boost
        num_detectors = sum(1 for d in rule_detections.values() if d)
        if anomaly_result['is_anomaly']:
            num_detectors += 1
        if ml_result['confidence'] >= 0.7 and ml_result['threat_class'] != "NORMAL":
            num_detectors += 1

        if num_detectors >= 4:
            risk += 5
        elif num_detectors == 3:
            risk += 4
        elif num_detectors == 2:
            risk += 2

        # Cap at 100
        return int(min(100, risk))

    def _determine_severity(self, risk_score: int, threat_class: str) -> str:
        """
        Determine severity from risk score and threat class.

        Args:
            risk_score: Risk score (0-100)
            threat_class: Classified threat class

        Returns:
            Severity level
        """
        if threat_class == "NORMAL":
            return "Low"

        if risk_score >= 85:
            return "Critical"
        elif risk_score >= 65:
            return "High"
        elif risk_score >= 40:
            return "Medium"
        else:
            return "Low"

    def _build_evidence(self,
                       ml_result: Dict[str, Any],
                       anomaly_result: Dict[str, Any],
                       rule_detections: Dict[str, Optional[Detection]],
                       single_flow: Dict[str, float],
                       aggregate: Optional[Dict[str, float]]) -> Dict[str, Any]:
        """Build comprehensive evidence dictionary."""
        evidence = {
            'ml_classification': {
                'predicted_class': ml_result['threat_class'],
                'confidence': ml_result['confidence'],
                'probabilities': ml_result['probabilities']
            },
            'anomaly_detection': {
                'is_anomaly': anomaly_result['is_anomaly'],
                'anomaly_score': anomaly_result['anomaly_score'],
                'raw_score': anomaly_result['raw_score']
            },
            'rule_based_detections': {}
        }

        # Add rule-based evidence
        for rule_name, detection in rule_detections.items():
            if detection:
                evidence['rule_based_detections'][rule_name] = {
                    'threat_class': detection.threat_class,
                    'confidence': detection.confidence,
                    'severity': detection.severity,
                    'evidence': detection.evidence
                }

        # Add key features
        key_features = [
            'packets_per_second', 'bytes_per_second', 'syn_ack_ratio',
            'average_packet_size', 'unique_destination_ports',
            'periodicity_score', 'dns_entropy'
        ]

        evidence['key_features'] = {}
        for feature in key_features:
            if feature in single_flow:
                evidence['key_features'][feature] = single_flow[feature]

        if aggregate:
            evidence['aggregate_features'] = {
                k: v for k, v in aggregate.items()
                if any(x in k for x in ['unique', 'count', 'rate', 'score'])
            }

        return evidence

    def _generate_explanations(self,
                              threat_class: str,
                              confidence: float,
                              anomaly_score: float,
                              risk_score: int,
                              rule_detections: Dict[str, Optional[Detection]],
                              ml_result: Dict[str, Any],
                              anomaly_result: Dict[str, Any]) -> List[str]:
        """Generate human-readable explanations."""
        explanations = []

        # Primary classification explanation
        if threat_class == "NORMAL":
            explanations.append(
                f"Traffic classified as normal with {confidence:.0%} confidence."
            )
        elif threat_class == "UNKNOWN_ANOMALY":
            explanations.append(
                f"Unusual network behavior detected (anomaly score: {anomaly_score:.0f}/100). "
                f"Pattern deviates from learned normal traffic but does not match known attack signatures."
            )
        elif threat_class == "SUSPICIOUS":
            explanations.append(
                f"Suspicious activity detected. Traffic shows anomalous characteristics "
                f"(anomaly score: {anomaly_score:.0f}/100) with moderate threat indicators."
            )
        else:
            explanations.append(
                f"{threat_class.replace('_', ' ').title()} detected with {confidence:.0%} confidence."
            )

        # ML evidence
        if ml_result['confidence'] >= 0.7:
            top_probs = sorted(
                ml_result['probabilities'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:2]

            explanations.append(
                f"Machine learning classifier: {top_probs[0][0]} ({top_probs[0][1]:.0%}), "
                f"{top_probs[1][0]} ({top_probs[1][1]:.0%})."
            )

        # Anomaly evidence
        if anomaly_result['is_anomaly']:
            explanations.append(
                f"Anomaly detector flagged this traffic as significantly different "
                f"from normal baseline patterns."
            )

        # Rule-based evidence
        triggered_rules = [
            (name, det) for name, det in rule_detections.items() if det
        ]
        if triggered_rules:
            rule_names = ", ".join([name.replace('_', ' ') for name, _ in triggered_rules])
            explanations.append(
                f"Rule-based detectors triggered: {rule_names}."
            )

            # Add specific rule evidence
            for name, detection in triggered_rules:
                if detection.human_explanation:
                    explanations.append(detection.human_explanation)

        # Risk explanation
        if risk_score >= 85:
            explanations.append(
                f"HIGH RISK (score: {risk_score}/100). Multiple detection methods agree. "
                f"Immediate investigation recommended."
            )
        elif risk_score >= 65:
            explanations.append(
                f"Elevated risk (score: {risk_score}/100). Strong threat indicators present."
            )
        elif risk_score >= 40:
            explanations.append(
                f"Moderate risk (score: {risk_score}/100). Some threat indicators present."
            )
        else:
            explanations.append(
                f"Low risk (score: {risk_score}/100)."
            )

        return explanations


# Global singleton
_engine_instance: Optional[HybridDetectionEngine] = None


def get_hybrid_engine() -> HybridDetectionEngine:
    """Get singleton hybrid engine instance."""
    global _engine_instance

    if _engine_instance is None:
        _engine_instance = HybridDetectionEngine()

    return _engine_instance


def detect_threat(single_flow_features: Dict[str, float],
                 aggregate_features: Optional[Dict[str, float]] = None,
                 ml_threshold: float = 0.7,
                 anomaly_threshold: float = 50.0) -> Dict[str, Any]:
    """
    Convenience function for hybrid detection.

    Args:
        single_flow_features: Features from single flow
        aggregate_features: Features from multiple flows
        ml_threshold: ML confidence threshold
        anomaly_threshold: Anomaly score threshold

    Returns:
        Detection result as dictionary
    """
    engine = get_hybrid_engine()
    result = engine.detect(
        single_flow_features,
        aggregate_features,
        ml_threshold,
        anomaly_threshold
    )
    return result.to_dict()


# Demo
if __name__ == '__main__':
    print("=" * 80)
    print("SentinelOneWay Hybrid Detection Engine - Demo")
    print("=" * 80)

    try:
        engine = HybridDetectionEngine()

        # Test scenarios
        scenarios = [
            ("Normal HTTP traffic", {
                'packets_per_second': 25.0,
                'bytes_per_second': 5000.0,
                'average_packet_size': 800.0,
                'syn_ack_ratio': 1.0,
                'packet_count': 100.0,
                'syn_count': 10.0,
                'ack_count': 10.0,
            }, None),

            ("SYN Flood attack", {
                'packets_per_second': 1500.0,
                'bytes_per_second': 90000.0,
                'average_packet_size': 60.0,
                'syn_ack_ratio': 75.0,
                'syn_count': 1500.0,
                'ack_count': 20.0,
                'packet_count': 1520.0,
            }, {
                'unique_source_ips': 45.0,
                'source_ip_entropy': 5.2,
                'destination_concentration': 0.95,
            }),

            ("Port scan", {
                'packets_per_second': 200.0,
                'bytes_per_second': 12000.0,
                'average_packet_size': 60.0,
                'syn_ack_ratio': 10.0,
            }, {
                'unique_destination_ports': 150.0,
                'connection_rate': 75.0,
                'unique_destination_hosts': 1.0,
            }),

            ("Unknown anomaly", {
                'packets_per_second': 500.0,
                'bytes_per_second': 25000.0,
                'average_packet_size': 50.0,
                'syn_ack_ratio': 3.0,
                'packet_count': 500.0,
            }, None),
        ]

        for i, (name, single_flow, aggregate) in enumerate(scenarios, 1):
            print(f"\n{'=' * 80}")
            print(f"Scenario {i}: {name}")
            print("=" * 80)

            result = engine.detect(single_flow, aggregate)

            print(f"\nClassification:")
            print(f"   Threat Class: {result.threat_class}")
            print(f"   Confidence: {result.confidence:.0%}")
            print(f"   Risk Score: {result.risk_score}/100")
            print(f"   Severity: {result.severity}")

            print(f"\nDetection Scores:")
            print(f"   ML Confidence: {result.evidence['ml_classification']['confidence']:.0%}")
            print(f"   Anomaly Score: {result.anomaly_score:.1f}/100")

            print(f"\nDetectors Triggered:")
            for detector in result.detectors_triggered:
                print(f"   * {detector.replace('_', ' ').title()}")

            if not result.detectors_triggered:
                print("   (None)")

            print(f"\nExplanation:")
            for j, explanation in enumerate(result.human_explanation, 1):
                print(f"   {j}. {explanation}")

        print(f"\n{'=' * 80}")
        print("Risk Scoring Logic:")
        print("=" * 80)
        print("1. Base Risk (0-60): ML confidence × 60 or anomaly score × 0.6")
        print("2. Anomaly Boost (+0 to +20): Based on anomaly score thresholds")
        print("3. Rule Agreement (+0 to +15): Each rule adds confidence × 5")
        print("4. Multi-Detector (+0 to +5): Bonus for multiple detectors")
        print("   Total: Capped at 100")
        print("=" * 80)

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nPlease train models first:")
        print("  python ml/train_model.py")
        print("  python ml/train_anomaly_detector.py")

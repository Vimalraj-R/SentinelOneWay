"""
Combined threat detection for SentinelOneWay.

Integrates both supervised classification (Random Forest) and
unsupervised anomaly detection (Isolation Forest) to provide
comprehensive threat detection with appropriate messaging.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Dict, Any, Optional
from detection.classifier import MLThreatClassifier, get_classifier
from detection.anomaly_detector import AnomalyDetector, get_anomaly_detector


class CombinedThreatDetector:
    """
    Combined threat detection using both supervised and unsupervised models.

    Provides:
    - Supervised classification for known threat types
    - Anomaly detection for unknown/unusual behavior
    - Appropriate messaging distinguishing between the two
    """

    def __init__(self):
        """Initialize combined detector with both models."""
        self.classifier = get_classifier()
        self.anomaly_detector = get_anomaly_detector()

    def detect(self, features: Dict[str, float],
              anomaly_threshold: float = 50.0,
              classification_confidence_threshold: float = 0.7) -> Dict[str, Any]:
        """
        Run both supervised and unsupervised detection.

        Args:
            features: Dictionary of feature name -> value
            anomaly_threshold: Threshold for anomaly flagging (0-100)
            classification_confidence_threshold: Min confidence for classification

        Returns:
            Dictionary with combined detection results
        """
        # Run supervised classification
        classification_result = self.classifier.predict_threat(features)

        # Run anomaly detection
        anomaly_result = self.anomaly_detector.predict_anomaly(
            features,
            threshold=anomaly_threshold
        )

        # Determine overall assessment
        assessment = self._assess_combined_results(
            classification_result,
            anomaly_result,
            classification_confidence_threshold
        )

        return {
            # Combined assessment
            'assessment': assessment,

            # Supervised classification (preserved independently)
            'classification': {
                'threat_class': classification_result['threat_class'],
                'confidence': classification_result['confidence'],
                'probabilities': classification_result['probabilities']
            },

            # Unsupervised anomaly detection (preserved independently)
            'anomaly_detection': {
                'is_anomaly': anomaly_result['is_anomaly'],
                'anomaly_score': anomaly_result['anomaly_score'],
                'severity': anomaly_result['severity'],
                'evidence': anomaly_result['evidence']
            },

            # Combined metadata
            'metadata': {
                'classification_threshold': classification_confidence_threshold,
                'anomaly_threshold': anomaly_threshold,
                'detection_methods': ['supervised_classification', 'anomaly_detection']
            }
        }

    def _assess_combined_results(self,
                                 classification_result: Dict[str, Any],
                                 anomaly_result: Dict[str, Any],
                                 confidence_threshold: float) -> Dict[str, Any]:
        """
        Assess combined results and generate appropriate messaging.

        Args:
            classification_result: Result from supervised classifier
            anomaly_result: Result from anomaly detector
            confidence_threshold: Minimum confidence for classification

        Returns:
            Dictionary with assessment and messaging
        """
        threat_class = classification_result['threat_class']
        confidence = classification_result['confidence']
        is_anomaly = anomaly_result['is_anomaly']
        anomaly_score = anomaly_result['anomaly_score']
        anomaly_severity = anomaly_result['severity']

        # Case 1: High confidence classification of known threat
        if confidence >= confidence_threshold and threat_class != "NORMAL":
            return {
                'detection_type': 'known_threat',
                'primary_source': 'supervised_classification',
                'message': f"{threat_class.replace('_', ' ').title()} detected",
                'severity': self._map_confidence_to_severity(confidence),
                'confidence': confidence,
                'details': f"Classified as {threat_class} with {confidence:.0%} confidence",
                'recommended_action': 'Investigate immediately - known threat pattern identified',
                'is_threat': True
            }

        # Case 2: Anomaly detected but not classified as specific threat
        elif is_anomaly and (confidence < confidence_threshold or threat_class == "NORMAL"):
            return {
                'detection_type': 'unknown_anomaly',
                'primary_source': 'anomaly_detection',
                'message': f"Unusual network behaviour detected",
                'severity': anomaly_severity,
                'anomaly_score': anomaly_score,
                'details': f"Behavior deviates significantly from normal patterns (score: {anomaly_score:.0f}/100)",
                'recommended_action': 'Investigate - unusual activity that may warrant attention',
                'is_threat': False  # Not confirmed threat, just unusual
            }

        # Case 3: Both agree it's an anomaly AND high confidence classification
        elif is_anomaly and confidence >= confidence_threshold and threat_class != "NORMAL":
            return {
                'detection_type': 'confirmed_threat',
                'primary_source': 'both',
                'message': f"{threat_class.replace('_', ' ').title()} detected with anomalous behavior",
                'severity': self._max_severity(
                    self._map_confidence_to_severity(confidence),
                    anomaly_severity
                ),
                'confidence': confidence,
                'anomaly_score': anomaly_score,
                'details': f"Both classification ({confidence:.0%}) and anomaly detection ({anomaly_score:.0f}/100) agree",
                'recommended_action': 'High priority - multiple detection methods confirm threat',
                'is_threat': True
            }

        # Case 4: Low confidence classification but high anomaly score
        elif is_anomaly and confidence < confidence_threshold and threat_class != "NORMAL":
            return {
                'detection_type': 'potential_threat',
                'primary_source': 'anomaly_detection',
                'message': f"Unusual behaviour detected (possibly {threat_class.replace('_', ' ').lower()})",
                'severity': anomaly_severity,
                'anomaly_score': anomaly_score,
                'details': f"Anomalous behavior detected. Low confidence classification suggests {threat_class}",
                'recommended_action': 'Monitor closely - anomalous with uncertain classification',
                'is_threat': False
            }

        # Case 5: Normal traffic according to both
        else:
            return {
                'detection_type': 'normal',
                'primary_source': None,
                'message': "Normal network traffic",
                'severity': "Low",
                'confidence': confidence,
                'anomaly_score': anomaly_score,
                'details': "No threats detected",
                'recommended_action': 'No action required',
                'is_threat': False
            }

    def _map_confidence_to_severity(self, confidence: float) -> str:
        """Map classification confidence to severity level."""
        if confidence >= 0.95:
            return "Critical"
        elif confidence >= 0.85:
            return "High"
        elif confidence >= 0.70:
            return "Medium"
        else:
            return "Low"

    def _max_severity(self, sev1: str, sev2: str) -> str:
        """Return the maximum of two severity levels."""
        severity_order = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
        if severity_order.get(sev1, 0) > severity_order.get(sev2, 0):
            return sev1
        return sev2


# Global singleton instance
_combined_detector_instance: Optional[CombinedThreatDetector] = None


def get_combined_detector() -> CombinedThreatDetector:
    """
    Get singleton combined detector instance.

    Returns:
        CombinedThreatDetector instance
    """
    global _combined_detector_instance

    if _combined_detector_instance is None:
        _combined_detector_instance = CombinedThreatDetector()

    return _combined_detector_instance


def detect_threat(features: Dict[str, float],
                 anomaly_threshold: float = 50.0,
                 classification_threshold: float = 0.7) -> Dict[str, Any]:
    """
    Convenience function for combined threat detection.

    Args:
        features: Dictionary of feature name -> value
        anomaly_threshold: Threshold for anomaly flagging (0-100)
        classification_threshold: Min confidence for classification

    Returns:
        Dictionary with combined detection results
    """
    detector = get_combined_detector()
    return detector.detect(features, anomaly_threshold, classification_threshold)


# Demo
if __name__ == '__main__':
    print("=" * 80)
    print("Combined Threat Detection - Demo")
    print("=" * 80)

    try:
        detector = CombinedThreatDetector()

        # Test scenarios
        scenarios = [
            ("Normal traffic", {
                'packets_per_second': 25.0,
                'bytes_per_second': 5000.0,
                'average_packet_size': 800.0,
                'syn_ack_ratio': 1.0,
            }),
            ("Known attack (SYN flood)", {
                'packets_per_second': 1500.0,
                'bytes_per_second': 90000.0,
                'average_packet_size': 60.0,
                'syn_ack_ratio': 75.0,
                'syn_count': 100.0,
            }),
            ("Unusual but unclear", {
                'packets_per_second': 500.0,
                'bytes_per_second': 25000.0,
                'average_packet_size': 50.0,
                'syn_ack_ratio': 5.0,
            })
        ]

        for name, features in scenarios:
            print(f"\n" + "-" * 80)
            print(f"Scenario: {name}")
            print("-" * 80)

            result = detector.detect(features)
            assessment = result['assessment']

            print(f"\nAssessment:")
            print(f"  Type: {assessment['detection_type']}")
            print(f"  Message: {assessment['message']}")
            print(f"  Severity: {assessment['severity']}")
            print(f"  Details: {assessment['details']}")
            print(f"  Action: {assessment['recommended_action']}")

            print(f"\nClassification:")
            print(f"  Threat: {result['classification']['threat_class']}")
            print(f"  Confidence: {result['classification']['confidence']:.0%}")

            print(f"\nAnomaly Detection:")
            print(f"  Is Anomaly: {result['anomaly_detection']['is_anomaly']}")
            print(f"  Score: {result['anomaly_detection']['anomaly_score']:.1f}/100")
            print(f"  Severity: {result['anomaly_detection']['severity']}")

        print("\n" + "=" * 80)
        print("Key Distinction:")
        print("=" * 80)
        print("  Known Threat:     'Port Scan detected' (supervised classification)")
        print("  Unknown Anomaly:  'Unusual network behaviour detected' (anomaly detection)")
        print("  Both results are preserved independently for transparency")
        print("=" * 80)

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nPlease train both models first:")
        print("  python ml/train_model.py")
        print("  python ml/train_anomaly_detector.py")

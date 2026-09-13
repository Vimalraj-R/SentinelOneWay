"""
Anomaly detector for SentinelOneWay using Isolation Forest.

Identifies unusual network behavior that deviates from learned
normal traffic patterns. Complements supervised classification
by detecting unknown threats.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import joblib
import numpy as np
from typing import Dict, Any, Optional


class AnomalyDetector:
    """
    Unsupervised anomaly detector using Isolation Forest.

    Identifies network behavior that deviates significantly
    from learned normal patterns.
    """

    def __init__(self,
                 model_path: str = 'models/isolation_forest.pkl',
                 scaler_path: str = 'models/isolation_forest_scaler.pkl',
                 metadata_path: str = 'models/isolation_forest_metadata.json'):
        """
        Initialize anomaly detector by loading trained model.

        Args:
            model_path: Path to saved Isolation Forest model
            scaler_path: Path to saved feature scaler
            metadata_path: Path to model metadata
        """
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.metadata_path = metadata_path

        self.model = None
        self.scaler = None
        self.metadata = None
        self.feature_names = None
        self.is_loaded = False

        # Score normalization parameters (learned from training data)
        self.score_mean = -0.45  # Typical normal score
        self.score_std = 0.05    # Typical score variation

        # Load model
        self._load_model()

    def _load_model(self):
        """Load model, scaler, and metadata from disk."""
        # Check if files exist
        if not Path(self.model_path).exists():
            raise FileNotFoundError(
                f"Model not found at {self.model_path}. "
                f"Train model first with: python ml/train_anomaly_detector.py"
            )

        if not Path(self.scaler_path).exists():
            raise FileNotFoundError(
                f"Scaler not found at {self.scaler_path}"
            )

        if not Path(self.metadata_path).exists():
            raise FileNotFoundError(
                f"Metadata not found at {self.metadata_path}"
            )

        # Load model and scaler
        try:
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")

        # Load metadata
        try:
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load metadata: {e}")

        # Extract information
        self.feature_names = self.metadata['feature_names']

        # Get score distribution from metadata
        if 'evaluation_metrics' in self.metadata:
            metrics = self.metadata['evaluation_metrics']
            self.score_mean = metrics.get('normal_score_mean', -0.45)
            self.score_std = metrics.get('normal_score_std', 0.05)

        self.is_loaded = True

    def _normalize_anomaly_score(self, raw_score: float) -> float:
        """
        Normalize Isolation Forest score to 0-100 scale.

        Isolation Forest returns negative scores where:
        - More negative = more anomalous
        - Typical normal scores: ~-0.40 to -0.45
        - Typical anomaly scores: <-0.50

        We transform to 0-100 where:
        - 0 = very normal
        - 50 = borderline
        - 100 = very anomalous

        Args:
            raw_score: Raw Isolation Forest score (negative)

        Returns:
            Normalized score (0-100)
        """
        # Calculate standard deviations from normal mean
        z_score = (self.score_mean - raw_score) / self.score_std

        # Map to 0-100 scale
        # z_score of 0 -> 0 (normal)
        # z_score of 5 -> 100 (very anomalous)
        normalized = (z_score / 5.0) * 100

        # Clamp to 0-100
        normalized = max(0, min(100, normalized))

        return normalized

    def _determine_severity(self, anomaly_score: float) -> str:
        """
        Determine severity based on anomaly score.

        Args:
            anomaly_score: Normalized anomaly score (0-100)

        Returns:
            Severity level string
        """
        if anomaly_score >= 80:
            return "Critical"
        elif anomaly_score >= 60:
            return "High"
        elif anomaly_score >= 40:
            return "Medium"
        else:
            return "Low"

    def predict_anomaly(self, features: Dict[str, float],
                       threshold: float = 50.0) -> Dict[str, Any]:
        """
        Predict if features represent anomalous behavior.

        Args:
            features: Dictionary of feature name -> value
            threshold: Anomaly score threshold (0-100) for flagging

        Returns:
            Dictionary with:
            - is_anomaly: Boolean flag
            - anomaly_score: Normalized score (0-100)
            - raw_score: Raw Isolation Forest score
            - severity: Severity level
            - evidence: Supporting evidence
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")

        # Prepare features in correct order
        feature_vector = []
        for feature_name in self.feature_names:
            if feature_name in features:
                feature_vector.append(features[feature_name])
            else:
                feature_vector.append(0.0)

        # Convert to numpy array and reshape
        X = np.array(feature_vector).reshape(1, -1)

        # Scale features
        X_scaled = self.scaler.transform(X)

        # Get anomaly prediction and score
        prediction = self.model.predict(X_scaled)[0]  # -1 = anomaly, 1 = normal
        raw_score = self.model.score_samples(X_scaled)[0]

        # Normalize score to 0-100
        anomaly_score = self._normalize_anomaly_score(raw_score)

        # Determine if anomalous based on threshold
        is_anomaly = anomaly_score >= threshold

        # Determine severity
        severity = self._determine_severity(anomaly_score)

        # Build evidence dictionary
        evidence = {
            'raw_anomaly_score': float(raw_score),
            'normalized_score': float(anomaly_score),
            'threshold_used': threshold,
            'deviation_from_normal': float(abs(raw_score - self.score_mean)),
            'model_prediction': 'anomaly' if prediction == -1 else 'normal'
        }

        return {
            'is_anomaly': bool(is_anomaly),
            'anomaly_score': float(anomaly_score),
            'raw_score': float(raw_score),
            'severity': severity,
            'evidence': evidence
        }

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information and metadata.

        Returns:
            Dictionary with model information
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")

        return {
            'model_type': self.metadata.get('model_type'),
            'training_date': self.metadata.get('training_date'),
            'training_samples': self.metadata.get('training_samples'),
            'trained_on_normal_only': self.metadata.get('trained_on_normal_only'),
            'num_features': len(self.feature_names),
            'detection_rate': self.metadata.get('evaluation_metrics', {}).get('recall'),
            'precision': self.metadata.get('evaluation_metrics', {}).get('precision'),
            'usage_notes': self.metadata.get('usage_notes', []),
            'warnings': self.metadata.get('warnings', [])
        }


# Global singleton instance
_anomaly_detector_instance: Optional[AnomalyDetector] = None


def get_anomaly_detector() -> AnomalyDetector:
    """
    Get singleton anomaly detector instance.

    Loads model once and reuses across predictions.

    Returns:
        AnomalyDetector instance
    """
    global _anomaly_detector_instance

    if _anomaly_detector_instance is None:
        _anomaly_detector_instance = AnomalyDetector()

    return _anomaly_detector_instance


def predict_anomaly(features: Dict[str, float],
                   threshold: float = 50.0) -> Dict[str, Any]:
    """
    Convenience function to predict anomaly.

    Automatically uses singleton detector instance.

    Args:
        features: Dictionary of feature name -> value
        threshold: Anomaly score threshold (0-100)

    Returns:
        Dictionary with prediction results
    """
    detector = get_anomaly_detector()
    return detector.predict_anomaly(features, threshold)


# Example usage
if __name__ == '__main__':
    print("=" * 80)
    print("SentinelOneWay Anomaly Detector - Demo")
    print("=" * 80)

    try:
        # Initialize detector
        detector = AnomalyDetector()

        # Get model info
        info = detector.get_model_info()
        print(f"\nModel Information:")
        print(f"  Type: {info['model_type']}")
        print(f"  Training Date: {info['training_date'][:10]}")
        print(f"  Training Samples: {info['training_samples']} (normal traffic)")
        print(f"  Detection Rate: {info['detection_rate']:.2%}")
        print(f"  Precision: {info['precision']:.2%}")

        # Example: Test with normal-looking features
        print(f"\n" + "=" * 80)
        print("Example 1: Normal-looking traffic")
        print("=" * 80)

        normal_features = {
            'packets_per_second': 25.0,
            'bytes_per_second': 5000.0,
            'average_packet_size': 800.0,
            'syn_ack_ratio': 1.0,
            'dns_entropy': 0.5,
            'periodicity_score': 0.6,
            # ... other features default to 0
        }

        result = detector.predict_anomaly(normal_features, threshold=50.0)

        print(f"\nResult:")
        print(f"  Is Anomaly: {result['is_anomaly']}")
        print(f"  Anomaly Score: {result['anomaly_score']:.1f}/100")
        print(f"  Severity: {result['severity']}")
        print(f"  Raw Score: {result['raw_score']:.4f}")

        # Example: Test with attack-like features
        print(f"\n" + "=" * 80)
        print("Example 2: Attack-like traffic (high SYN ratio)")
        print("=" * 80)

        attack_features = {
            'packets_per_second': 1500.0,
            'bytes_per_second': 90000.0,
            'average_packet_size': 60.0,
            'syn_ack_ratio': 75.0,
            'syn_count': 100.0,
            'ack_count': 2.0,
        }

        result = detector.predict_anomaly(attack_features, threshold=50.0)

        print(f"\nResult:")
        print(f"  Is Anomaly: {result['is_anomaly']}")
        print(f"  Anomaly Score: {result['anomaly_score']:.1f}/100")
        print(f"  Severity: {result['severity']}")
        print(f"  Raw Score: {result['raw_score']:.4f}")

        print(f"\n" + "=" * 80)
        print("Key Points:")
        print("=" * 80)
        for note in info['usage_notes']:
            print(f"  - {note}")

        print(f"\n" + "=" * 80)

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print(f"\nPlease train the anomaly detector first:")
        print(f"  python ml/train_anomaly_detector.py")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

"""
ML-based threat classifier for SentinelOneWay.

Loads trained Random Forest model and provides prediction interface
with confidence scores and class probabilities.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime


class MLThreatClassifier:
    """
    Machine learning threat classifier.

    Loads pre-trained Random Forest model and provides
    threat prediction with confidence scores.
    """

    def __init__(self, model_path: str = 'models/random_forest.pkl',
                 metadata_path: str = 'models/random_forest_metadata.json'):
        """
        Initialize classifier by loading trained model.

        Args:
            model_path: Path to saved model
            metadata_path: Path to model metadata
        """
        self.model_path = model_path
        self.metadata_path = metadata_path
        self.model = None
        self.metadata = None
        self.feature_names = None
        self.class_names = None
        self.is_loaded = False

        # Load model
        self._load_model()

    def _load_model(self):
        """Load model and metadata from disk."""
        # Check if files exist
        if not Path(self.model_path).exists():
            raise FileNotFoundError(
                f"Model not found at {self.model_path}. "
                f"Train model first with: python ml/train_model.py"
            )

        if not Path(self.metadata_path).exists():
            raise FileNotFoundError(
                f"Metadata not found at {self.metadata_path}"
            )

        # Load model
        try:
            self.model = joblib.load(self.model_path)
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
        self.class_names = {
            int(k): v for k, v in self.metadata['label_mapping'].items()
        }

        self.is_loaded = True

    def predict_threat(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Predict threat class for given features.

        Args:
            features: Dictionary of feature name -> value

        Returns:
            Dictionary with:
            - threat_class: Predicted class name
            - confidence: Confidence score (0-1)
            - probabilities: Dictionary of class -> probability
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")

        # Prepare features in correct order
        feature_vector = []
        missing_features = []

        for feature_name in self.feature_names:
            if feature_name in features:
                feature_vector.append(features[feature_name])
            else:
                missing_features.append(feature_name)
                feature_vector.append(0.0)  # Default to 0 for missing

        if missing_features:
            # This is expected behavior - just use 0.0 for missing features
            # Could log warning in production
            pass

        # Convert to numpy array and reshape for single prediction
        X = np.array(feature_vector).reshape(1, -1)

        # Predict class and probabilities
        predicted_class = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]

        # Get class name
        threat_class = self.class_names[predicted_class]

        # Get confidence (probability of predicted class)
        confidence = float(probabilities[predicted_class])

        # Build probability dictionary
        probability_dict = {
            self.class_names[i]: float(probabilities[i])
            for i in range(len(probabilities))
        }

        return {
            'threat_class': threat_class,
            'confidence': confidence,
            'probabilities': probability_dict
        }

    def predict_batch(self, features_list: List[Dict[str, float]]) -> List[Dict[str, Any]]:
        """
        Predict threats for multiple feature sets.

        Args:
            features_list: List of feature dictionaries

        Returns:
            List of prediction results
        """
        results = []
        for features in features_list:
            result = self.predict_threat(features)
            results.append(result)
        return results

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
            'num_features': len(self.feature_names),
            'num_classes': len(self.class_names),
            'classes': list(self.class_names.values()),
            'test_accuracy': self.metadata.get('test_metrics', {}).get('accuracy'),
            'warnings': self.metadata.get('warnings', [])
        }

    def get_feature_importance(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Get feature importance scores.

        Args:
            top_n: Number of top features to return

        Returns:
            List of feature importance dictionaries
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")

        feature_importance = self.metadata.get('feature_importance', [])
        return feature_importance[:top_n]


# Global singleton instance for efficient loading
_classifier_instance: Optional[MLThreatClassifier] = None


def get_classifier() -> MLThreatClassifier:
    """
    Get singleton classifier instance.

    Loads model once and reuses across predictions.

    Returns:
        MLThreatClassifier instance
    """
    global _classifier_instance

    if _classifier_instance is None:
        _classifier_instance = MLThreatClassifier()

    return _classifier_instance


def predict_threat(features: Dict[str, float]) -> Dict[str, Any]:
    """
    Convenience function to predict threat.

    Automatically uses singleton classifier instance.

    Args:
        features: Dictionary of feature name -> value

    Returns:
        Dictionary with prediction results
    """
    classifier = get_classifier()
    return classifier.predict_threat(features)


# Example usage
if __name__ == '__main__':
    print("=" * 80)
    print("SentinelOneWay ML Threat Classifier - Demo")
    print("=" * 80)

    try:
        # Initialize classifier
        classifier = MLThreatClassifier()

        # Get model info
        info = classifier.get_model_info()
        print(f"\nModel Information:")
        print(f"  Type: {info['model_type']}")
        print(f"  Training Date: {info['training_date']}")
        print(f"  Features: {info['num_features']}")
        print(f"  Classes: {info['num_classes']}")
        print(f"  Test Accuracy: {info['test_accuracy']:.4f}")

        print(f"\nSupported Threat Classes:")
        for class_name in info['classes']:
            print(f"  - {class_name}")

        print(f"\nTop 5 Most Important Features:")
        for feat in classifier.get_feature_importance(5):
            print(f"  {feat['feature']:30s}: {feat['importance']:.4f}")

        # Example prediction with dummy features
        print(f"\n" + "=" * 80)
        print("Example Prediction (dummy features):")
        print("=" * 80)

        example_features = {
            'packets_per_second': 1000.0,
            'syn_ack_ratio': 50.0,
            'average_packet_size': 60.0,
            'dns_entropy': 0.0,
            'periodicity_score': 0.5,
            'unique_destination_ports': 1.0,
            'outbound_inbound_ratio': 45.0,
            # ... other features would be 0.0 by default
        }

        result = classifier.predict_threat(example_features)

        print(f"\nPrediction:")
        print(f"  Threat Class: {result['threat_class']}")
        print(f"  Confidence: {result['confidence']:.4f}")
        print(f"\nProbabilities:")
        for class_name, prob in sorted(result['probabilities'].items(),
                                       key=lambda x: x[1], reverse=True):
            print(f"  {class_name:25s}: {prob:.4f}")

        print(f"\n" + "=" * 80)
        print("IMPORTANT WARNINGS:")
        print("=" * 80)
        for warning in info['warnings']:
            print(f"  - {warning}")

        print(f"\n" + "=" * 80)

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print(f"\nPlease train the model first:")
        print(f"  python ml/train_model.py")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

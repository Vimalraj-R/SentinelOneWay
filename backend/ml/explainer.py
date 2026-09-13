"""
Explainable AI for SentinelOneWay threat classification.

Uses SHAP (SHapley Additive exPlanations) to provide interpretable
explanations for Random Forest predictions.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import joblib
import json
from typing import Dict, Any, List, Tuple, Optional
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# Try to import SHAP, provide helpful error if not installed
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logger.warning(
        "SHAP not installed. Install with: pip install shap\n"
        "Explainability features will be limited."
    )


class ThreatExplainer:
    """
    Explainable AI for threat classification.

    Provides both technical feature importance and human-readable
    explanations for model predictions.
    """

    def __init__(self,
                 model_path: str = 'models/random_forest.pkl',
                 metadata_path: str = 'models/random_forest_metadata.json'):
        """
        Initialize threat explainer.

        Args:
            model_path: Path to trained model
            metadata_path: Path to model metadata
        """
        self.model_path = model_path
        self.metadata_path = metadata_path

        # Load model and metadata
        self._load_model()

        # SHAP explainer (lazy initialization)
        self._shap_explainer = None

    def _load_model(self):
        """Load model and metadata."""
        # Load model
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}")

        self.model = joblib.load(self.model_path)

        # Load metadata
        if not Path(self.metadata_path).exists():
            raise FileNotFoundError(f"Metadata not found at {self.metadata_path}")

        with open(self.metadata_path, 'r') as f:
            self.metadata = json.load(f)

        self.feature_names = self.metadata['feature_names']

        # Get class names (handle different metadata formats)
        if 'classes' in self.metadata:
            self.class_names = self.metadata['classes']
        elif 'class_names' in self.metadata:
            # Convert dict to list if needed
            class_names_dict = self.metadata['class_names']
            if isinstance(class_names_dict, dict):
                self.class_names = [class_names_dict[str(i)] for i in range(len(class_names_dict))]
            else:
                self.class_names = class_names_dict
        else:
            # Default class names
            self.class_names = ['NORMAL', 'SYN_FLOOD', 'PORT_SCAN', 'C2_BEACON', 'DNS_TUNNEL', 'DATA_EXFILTRATION']

    def _get_shap_explainer(self):
        """
        Get or create SHAP explainer (cached).

        TreeExplainer is fast for tree-based models.
        """
        if not SHAP_AVAILABLE:
            return None

        if self._shap_explainer is None:
            logger.info("Creating SHAP TreeExplainer (first time only)...")
            self._shap_explainer = shap.TreeExplainer(self.model)
            logger.info("SHAP TreeExplainer ready")

        return self._shap_explainer

    def explain_prediction(self,
                          features: Dict[str, float],
                          top_n: int = 10) -> Dict[str, Any]:
        """
        Explain a threat classification prediction.

        Args:
            features: Feature dictionary
            top_n: Number of top features to return

        Returns:
            Dictionary with technical and human-readable explanations
        """
        # Prepare feature vector
        feature_vector = self._prepare_features(features)

        # Get prediction
        prediction_proba = self.model.predict_proba(feature_vector)[0]
        predicted_class_idx = np.argmax(prediction_proba)
        predicted_class = self.class_names[predicted_class_idx]
        confidence = prediction_proba[predicted_class_idx]

        # Get SHAP values if available
        shap_values = None
        if SHAP_AVAILABLE:
            try:
                explainer = self._get_shap_explainer()
                if explainer:
                    shap_values = explainer.shap_values(feature_vector)
            except Exception as e:
                logger.warning(f"SHAP explanation failed: {e}")

        # Extract technical explanation
        technical_explanation = self._extract_technical_explanation(
            feature_vector,
            shap_values,
            predicted_class_idx,
            top_n
        )

        # Generate human-readable explanation
        human_explanation = self._generate_human_explanation(
            technical_explanation,
            predicted_class,
            features
        )

        return {
            'predicted_class': predicted_class,
            'confidence': float(confidence),
            'technical_explanation': technical_explanation,
            'human_explanation': human_explanation,
            'all_class_probabilities': {
                cls: float(prob)
                for cls, prob in zip(self.class_names, prediction_proba)
            }
        }

    def _prepare_features(self, features: Dict[str, float]) -> np.ndarray:
        """Prepare features in correct order for model."""
        feature_vector = []
        for feature_name in self.feature_names:
            feature_vector.append(features.get(feature_name, 0.0))

        return np.array(feature_vector).reshape(1, -1)

    def _extract_technical_explanation(self,
                                      feature_vector: np.ndarray,
                                      shap_values: Optional[np.ndarray],
                                      predicted_class_idx: int,
                                      top_n: int) -> List[Dict[str, Any]]:
        """
        Extract technical feature importance explanation.

        Args:
            feature_vector: Input features
            shap_values: SHAP values (if available)
            predicted_class_idx: Index of predicted class
            top_n: Number of top features

        Returns:
            List of feature importance dictionaries
        """
        if shap_values is not None and SHAP_AVAILABLE:
            # Use SHAP values for predicted class
            # shap_values shape: (n_classes, n_samples, n_features)
            class_shap_values = shap_values[predicted_class_idx][0]

            # Get feature importance (absolute SHAP values)
            feature_importance = np.abs(class_shap_values)

        else:
            # Fallback: use model's feature importances
            feature_importance = self.model.feature_importances_

        # Get top N features
        top_indices = np.argsort(feature_importance)[-top_n:][::-1]

        technical_explanation = []
        for idx in top_indices:
            feature_name = self.feature_names[idx]
            feature_value = float(feature_vector[0][idx])
            importance = float(feature_importance[idx])

            # Skip if importance is negligible
            if importance < 0.001:
                continue

            technical_explanation.append({
                'feature': feature_name,
                'value': feature_value,
                'importance': importance,
                'impact': 'positive' if (shap_values is not None and
                                        class_shap_values[idx] > 0) else 'unknown'
            })

        return technical_explanation

    def _generate_human_explanation(self,
                                   technical_explanation: List[Dict[str, Any]],
                                   predicted_class: str,
                                   features: Dict[str, float]) -> List[str]:
        """
        Generate human-readable explanations from technical features.

        Args:
            technical_explanation: Technical feature importance
            predicted_class: Predicted threat class
            features: Raw feature values

        Returns:
            List of human-readable explanation strings
        """
        explanations = []

        # Add class-specific context
        class_context = self._get_class_context(predicted_class)
        if class_context:
            explanations.append(class_context)

        # Explain top features
        for item in technical_explanation[:5]:  # Top 5 for readability
            feature_name = item['feature']
            feature_value = item['value']
            importance = item['importance']

            # Generate human explanation for this feature
            explanation = self._explain_feature(
                feature_name,
                feature_value,
                importance,
                predicted_class,
                features
            )

            if explanation:
                explanations.append(explanation)

        return explanations

    def _get_class_context(self, predicted_class: str) -> Optional[str]:
        """Get context explanation for threat class."""
        contexts = {
            'SYN_FLOOD': "This traffic pattern is consistent with a SYN flood DDoS attack.",
            'PORT_SCAN': "This activity indicates network reconnaissance through port scanning.",
            'C2_BEACON': "This behavior matches command and control (C2) beaconing patterns.",
            'DNS_TUNNEL': "This DNS traffic shows signs of data exfiltration via DNS tunneling.",
            'DATA_EXFILTRATION': "This traffic pattern suggests unauthorized data transfer.",
            'NORMAL': "This traffic appears to be legitimate network activity."
        }
        return contexts.get(predicted_class)

    def _explain_feature(self,
                        feature_name: str,
                        feature_value: float,
                        importance: float,
                        predicted_class: str,
                        all_features: Dict[str, float]) -> Optional[str]:
        """
        Generate human-readable explanation for a single feature.

        Args:
            feature_name: Feature name
            feature_value: Feature value
            importance: Feature importance
            predicted_class: Predicted class
            all_features: All feature values (for context)

        Returns:
            Human-readable explanation string or None
        """
        # Feature explanation templates
        explanations = {
            # Traffic features
            'packets_per_second': lambda v: (
                f"Packet rate is {'very high' if v > 1000 else 'elevated'} at {v:.0f} packets/sec."
                if v > 100 else None
            ),
            'bytes_per_second': lambda v: (
                f"Data transfer rate is {'extremely high' if v > 500000 else 'elevated'} "
                f"at {v/1000:.1f} KB/sec."
                if v > 50000 else None
            ),
            'average_packet_size': lambda v: (
                f"Packets are unusually {'small' if v < 100 else 'large'} "
                f"({v:.0f} bytes), typical of {'scanning' if v < 100 else 'data transfer'}."
                if v < 100 or v > 1200 else None
            ),

            # TCP features
            'syn_ack_ratio': lambda v: (
                f"SYN/ACK ratio is extremely high ({v:.1f}), "
                f"indicating incomplete TCP handshakes typical of SYN floods."
                if v > 10 else (
                    f"SYN/ACK ratio is elevated ({v:.1f}), suggesting some connection issues."
                    if v > 3 else None
                )
            ),
            'syn_count': lambda v: (
                f"Very high number of SYN packets ({v:.0f}), characteristic of flood attacks."
                if v > 500 else None
            ),

            # Reconnaissance features
            'unique_destination_ports': lambda v: (
                f"Scanning {v:.0f} different ports suggests systematic reconnaissance."
                if v > 50 else (
                    f"Accessing {v:.0f} different ports indicates broad service probing."
                    if v > 20 else None
                )
            ),
            'connection_rate': lambda v: (
                f"Very high connection rate ({v:.0f}/sec) typical of automated scanning."
                if v > 50 else None
            ),

            # DDoS features
            'unique_source_ips': lambda v: (
                f"Traffic originates from {v:.0f} different sources, "
                f"suggesting a distributed attack."
                if v > 20 else None
            ),
            'source_ip_entropy': lambda v: (
                f"High source IP diversity (entropy: {v:.2f}) indicates distributed botnet."
                if v > 4.5 else None
            ),

            # C2 features
            'periodicity_score': lambda v: (
                f"Traffic shows highly periodic behavior (score: {v:.2f}), "
                f"characteristic of automated C2 beaconing."
                if v > 0.8 else None
            ),
            'flow_regularity': lambda v: (
                f"Connection timing is suspiciously regular (score: {v:.2f})."
                if v > 0.85 else None
            ),

            # DNS features
            'dns_entropy': lambda v: (
                f"DNS query entropy is {'very high' if v > 4 else 'elevated'} ({v:.2f}), "
                f"suggesting randomized subdomain generation."
                if v > 3.5 else None
            ),
            'dns_query_length': lambda v: (
                f"DNS queries are unusually long ({v:.0f} characters), "
                f"typical of data exfiltration."
                if v > 50 else None
            ),

            # Exfiltration features
            'outbound_inbound_ratio': lambda v: (
                f"Outbound traffic is {v:.1f}x higher than inbound, "
                f"suggesting data exfiltration."
                if v > 5 else None
            ),
            'outbound_bytes': lambda v: (
                f"Large amount of outbound data ({v/1000000:.1f} MB) to external destination."
                if v > 1000000 else None
            ),
        }

        # Get explanation for this feature
        if feature_name in explanations:
            try:
                explanation = explanations[feature_name](feature_value)
                return explanation
            except Exception as e:
                logger.warning(f"Error generating explanation for {feature_name}: {e}")

        return None


# Global explainer instance (singleton)
_explainer_instance: Optional[ThreatExplainer] = None


def get_explainer() -> ThreatExplainer:
    """
    Get singleton explainer instance.

    Returns:
        ThreatExplainer instance
    """
    global _explainer_instance

    if _explainer_instance is None:
        _explainer_instance = ThreatExplainer()

    return _explainer_instance


def explain_threat(features: Dict[str, float],
                   top_n: int = 10) -> Dict[str, Any]:
    """
    Convenience function to explain a threat prediction.

    Args:
        features: Feature dictionary
        top_n: Number of top features to return

    Returns:
        Explanation dictionary
    """
    explainer = get_explainer()
    return explainer.explain_prediction(features, top_n)


# Demo
if __name__ == '__main__':
    print("=" * 80)
    print("Explainable AI - Demo")
    print("=" * 80)

    if not SHAP_AVAILABLE:
        print("\nWarning: SHAP not installed. Install with: pip install shap")
        print("Falling back to feature importances.\n")

    try:
        explainer = ThreatExplainer()

        # Test scenario: SYN Flood
        print("\nScenario: SYN Flood Attack")
        print("-" * 80)

        features = {
            'packets_per_second': 1500.0,
            'bytes_per_second': 90000.0,
            'average_packet_size': 60.0,
            'syn_ack_ratio': 75.0,
            'syn_count': 1500.0,
            'ack_count': 20.0,
            'unique_source_ips': 45.0,
            'source_ip_entropy': 5.2,
            'destination_concentration': 0.95,
        }

        explanation = explainer.explain_prediction(features, top_n=8)

        print(f"\nPrediction: {explanation['predicted_class']}")
        print(f"Confidence: {explanation['confidence']:.0%}")

        print(f"\n{'Human Explanation:':=^80}")
        for i, exp in enumerate(explanation['human_explanation'], 1):
            print(f"{i}. {exp}")

        print(f"\n{'Technical Evidence:':=^80}")
        print(f"{'Feature':<30} {'Value':>12} {'Importance':>12}")
        print("-" * 80)
        for item in explanation['technical_explanation']:
            print(f"{item['feature']:<30} {item['value']:>12.2f} {item['importance']:>12.1%}")

        print("\n" + "=" * 80)

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nPlease train the model first:")
        print("  python ml/train_model.py")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

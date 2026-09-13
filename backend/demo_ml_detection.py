"""
ML-based threat detection demo for SentinelOneWay.

Demonstrates end-to-end ML detection pipeline:
  Simulator -> Features -> ML Classifier -> Prediction
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from simulator.traffic_generator import TrafficGenerator
from features.extractor import FlowFeatureExtractor
from detection.classifier import MLThreatClassifier


def demo_ml_detection_pipeline():
    """Demonstrate complete ML detection pipeline."""
    print("=" * 80)
    print("SentinelOneWay ML Detection Pipeline Demo")
    print("=" * 80)

    # Initialize components
    print("\nInitializing components...")
    generator = TrafficGenerator()
    extractor = FlowFeatureExtractor()
    classifier = MLThreatClassifier()

    print("  [OK] Traffic generator ready")
    print("  [OK] Feature extractor ready")
    print("  [OK] ML classifier loaded")

    # Get model info
    model_info = classifier.get_model_info()
    print(f"\nModel: {model_info['model_type']}")
    print(f"  Trained: {model_info['training_date'][:10]}")
    print(f"  Test Accuracy: {model_info['test_accuracy']:.2%}")

    # Test scenarios
    scenarios = ['normal', 'syn_flood', 'port_scan', 'c2_beacon',
                 'dns_tunnel', 'data_exfiltration']

    results = []

    for scenario in scenarios:
        print(f"\n" + "-" * 80)
        print(f"Testing: {scenario.upper()}")
        print("-" * 80)

        # Generate traffic
        flows = generator.generate_traffic(scenario, intensity=0.7)
        print(f"  Generated {len(flows)} flows")

        # Extract features
        features_df = extractor.extract_batch(flows)
        mean_features = features_df.mean().to_dict()
        aggregate_features = extractor.extract_aggregate(flows)

        # Combine features
        combined_features = {**mean_features, **aggregate_features}

        # Predict with ML
        prediction = classifier.predict_threat(combined_features)

        print(f"\n  ML Prediction:")
        print(f"    Threat: {prediction['threat_class']}")
        print(f"    Confidence: {prediction['confidence']:.2%}")

        print(f"\n  Top 3 Probabilities:")
        sorted_probs = sorted(
            prediction['probabilities'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        for class_name, prob in sorted_probs[:3]:
            print(f"    {class_name:25s}: {prob:.2%}")

        # Check if correct
        expected_class = scenario.upper()
        is_correct = prediction['threat_class'] == expected_class

        results.append({
            'scenario': scenario,
            'predicted': prediction['threat_class'],
            'confidence': prediction['confidence'],
            'correct': is_correct
        })

        if is_correct:
            print(f"\n  [OK] Correct prediction!")
        else:
            print(f"\n  [MISMATCH] Expected {expected_class}, "
                  f"got {prediction['threat_class']}")

    # Summary
    print("\n" + "=" * 80)
    print("Detection Summary")
    print("=" * 80)

    correct_count = sum(1 for r in results if r['correct'])
    accuracy = correct_count / len(results)

    print(f"\nResults: {correct_count}/{len(results)} correct ({accuracy:.0%})")
    print(f"\nDetection Matrix:")
    print(f"{'Scenario':20s} {'Predicted':25s} {'Confidence':>12s} {'Status':>10s}")
    print("-" * 80)

    for r in results:
        status = "[OK]" if r['correct'] else "[MISS]"
        print(f"{r['scenario']:20s} {r['predicted']:25s} "
              f"{r['confidence']:11.0%} {status:>10s}")

    avg_confidence = sum(r['confidence'] for r in results) / len(results)
    print(f"\nAverage Confidence: {avg_confidence:.0%}")


def demo_feature_importance():
    """Show feature importance analysis."""
    print("\n\n" + "=" * 80)
    print("Feature Importance Analysis")
    print("=" * 80)

    classifier = MLThreatClassifier()

    print("\nTop 15 Most Important Features for Threat Detection:")
    print("-" * 80)

    for i, feat in enumerate(classifier.get_feature_importance(15), 1):
        importance_bar = "#" * int(feat['importance'] * 100)
        print(f"{i:2d}. {feat['feature']:30s} {feat['importance']:.4f} {importance_bar}")


def demo_confidence_analysis():
    """Analyze confidence scores across scenarios."""
    print("\n\n" + "=" * 80)
    print("Confidence Score Analysis")
    print("=" * 80)

    generator = TrafficGenerator()
    extractor = FlowFeatureExtractor()
    classifier = MLThreatClassifier()

    scenarios = {
        'syn_flood': 'SYN_FLOOD',
        'port_scan': 'PORT_SCAN',
        'c2_beacon': 'C2_BEACON',
        'dns_tunnel': 'DNS_TUNNEL',
        'data_exfiltration': 'DATA_EXFILTRATION',
        'normal': 'NORMAL'
    }

    print(f"\nTesting 10 samples per scenario...")

    for scenario, expected_class in scenarios.items():
        confidences = []

        for i in range(10):
            # Generate sample
            flows = generator.generate_traffic(scenario, intensity=0.5 + i*0.05)

            # Extract features
            features_df = extractor.extract_batch(flows)
            mean_features = features_df.mean().to_dict()
            aggregate = extractor.extract_aggregate(flows)
            combined = {**mean_features, **aggregate}

            # Predict
            result = classifier.predict_threat(combined)

            if result['threat_class'] == expected_class:
                confidences.append(result['confidence'])

        if confidences:
            avg_conf = sum(confidences) / len(confidences)
            min_conf = min(confidences)
            max_conf = max(confidences)

            print(f"\n{scenario:20s}: avg={avg_conf:.2%} "
                  f"min={min_conf:.2%} max={max_conf:.2%} "
                  f"({len(confidences)}/10 correct)")


if __name__ == '__main__':
    print("\n")
    print("=" * 80)
    print(" " * 20 + "SentinelOneWay ML Detection Demo")
    print("=" * 80)

    try:
        demo_ml_detection_pipeline()
        demo_feature_importance()
        demo_confidence_analysis()

        print("\n\n" + "=" * 80)
        print("IMPORTANT NOTES")
        print("=" * 80)
        print("\n1. Model trained on SYNTHETIC data only")
        print("2. Real network traffic may have different characteristics")
        print("3. Validation on production data required before deployment")
        print("4. False positive rate on real traffic is unknown")
        print("5. Use in combination with rule-based detectors for best results")

        print("\n" + "=" * 80)
        print("Demo complete!")
        print("=" * 80)

    except FileNotFoundError as e:
        print(f"\n\nError: {e}")
        print(f"\nPlease train the model first:")
        print(f"  python ml/train_model.py")

    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()

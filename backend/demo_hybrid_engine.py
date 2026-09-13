"""
Comprehensive demo of the Hybrid Detection Engine.

Shows how the engine combines rule-based, supervised ML, and
unsupervised anomaly detection for comprehensive threat detection.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from detection.hybrid_engine import HybridDetectionEngine, detect_threat
from simulator.traffic_generator import TrafficGenerator
from features.extractor import FlowFeatureExtractor
import warnings
warnings.filterwarnings('ignore')


def print_section(title: str, char: str = "="):
    """Print section header."""
    print(f"\n{char * 80}")
    print(f"{title}")
    print(f"{char * 80}")


def print_detection_result(scenario_name: str, result: dict):
    """Print detection result in formatted way."""
    print(f"\nScenario: {scenario_name}")
    print("-" * 80)

    print(f"\nFinal Classification:")
    print(f"  Threat Class:  {result['threat_class']}")
    print(f"  Confidence:    {result['confidence']:.0%}")
    print(f"  Risk Score:    {result['risk_score']}/100")
    print(f"  Severity:      {result['severity']}")

    print(f"\nDetection Components:")
    ml = result['evidence']['ml_classification']
    anomaly = result['evidence']['anomaly_detection']
    print(f"  ML Classifier:      {ml['predicted_class']} ({ml['confidence']:.0%})")
    print(f"  Anomaly Detector:   {'FLAGGED' if anomaly['is_anomaly'] else 'normal'} ({anomaly['anomaly_score']:.1f}/100)")

    rules = result['evidence']['rule_based_detections']
    if rules:
        print(f"  Rule Detectors:     {len(rules)} triggered")
        for rule_name, rule_data in rules.items():
            print(f"    - {rule_name}: {rule_data['threat_class']} ({rule_data['confidence']:.0%})")
    else:
        print(f"  Rule Detectors:     None triggered")

    print(f"\nDetectors Triggered: {', '.join(result['detectors_triggered'])}")

    print(f"\nExplanation:")
    for i, explanation in enumerate(result['human_explanation'], 1):
        # Wrap long explanations
        if len(explanation) > 75:
            words = explanation.split()
            line = f"  {i}. "
            for word in words:
                if len(line) + len(word) + 1 > 78:
                    print(line)
                    line = "     " + word
                else:
                    line += word + " "
            print(line)
        else:
            print(f"  {i}. {explanation}")


def demo_basic_scenarios():
    """Demo basic detection scenarios."""
    print_section("HYBRID DETECTION ENGINE - Basic Scenarios")

    engine = HybridDetectionEngine()

    scenarios = [
        ("Normal HTTP Traffic", {
            'packets_per_second': 25.0,
            'bytes_per_second': 5000.0,
            'average_packet_size': 800.0,
            'syn_ack_ratio': 1.0,
            'packet_count': 100.0,
            'syn_count': 10.0,
            'ack_count': 10.0,
            'flow_duration': 10.0,
            'byte_count': 50000.0,
        }, None),

        ("SYN Flood Attack", {
            'packets_per_second': 1500.0,
            'bytes_per_second': 90000.0,
            'average_packet_size': 60.0,
            'syn_ack_ratio': 75.0,
            'syn_count': 1500.0,
            'ack_count': 20.0,
            'packet_count': 1520.0,
            'flow_duration': 1.0,
            'byte_count': 90000.0,
        }, {
            'unique_source_ips': 45.0,
            'source_ip_entropy': 5.2,
            'destination_concentration': 0.95,
        }),

        ("Port Scan", {
            'packets_per_second': 200.0,
            'bytes_per_second': 12000.0,
            'average_packet_size': 60.0,
            'syn_ack_ratio': 10.0,
            'packet_count': 200.0,
            'syn_count': 180.0,
            'flow_duration': 1.0,
        }, {
            'unique_destination_ports': 150.0,
            'connection_rate': 75.0,
            'unique_destination_hosts': 1.0,
        }),

        ("C2 Beacon", {
            'packets_per_second': 2.0,
            'bytes_per_second': 500.0,
            'average_packet_size': 250.0,
            'packet_count': 120.0,
            'flow_duration': 60.0,
            'periodicity_score': 0.95,
        }, {
            'flow_regularity': 0.92,
            'common_intervals_count': 3.0,
        }),
    ]

    for name, single_flow, aggregate in scenarios:
        result = engine.detect(single_flow, aggregate)
        print_detection_result(name, result.to_dict())
        print()


def demo_edge_cases():
    """Demo edge cases and ambiguous scenarios."""
    print_section("Edge Cases and Ambiguous Scenarios", "-")

    engine = HybridDetectionEngine()

    scenarios = [
        ("High Volume Legitimate (Backup)", {
            'packets_per_second': 800.0,
            'bytes_per_second': 800000.0,
            'average_packet_size': 1000.0,
            'syn_ack_ratio': 1.0,
            'packet_count': 8000.0,
            'flow_duration': 10.0,
        }, None),

        ("Unknown Anomaly", {
            'packets_per_second': 500.0,
            'bytes_per_second': 25000.0,
            'average_packet_size': 50.0,
            'syn_ack_ratio': 3.0,
            'packet_count': 500.0,
            'flow_duration': 1.0,
        }, None),

        ("Low Confidence Multi-Signal", {
            'packets_per_second': 150.0,
            'bytes_per_second': 15000.0,
            'average_packet_size': 100.0,
            'syn_ack_ratio': 5.0,
            'packet_count': 150.0,
        }, {
            'unique_destination_ports': 80.0,
            'connection_rate': 40.0,
        }),
    ]

    for name, single_flow, aggregate in scenarios:
        result = engine.detect(single_flow, aggregate)
        print_detection_result(name, result.to_dict())
        print()


def demo_threshold_sensitivity():
    """Demo how threshold changes affect classification."""
    print_section("Threshold Sensitivity Analysis", "-")

    engine = HybridDetectionEngine()

    # Borderline case
    features = {
        'packets_per_second': 300.0,
        'bytes_per_second': 18000.0,
        'average_packet_size': 60.0,
        'syn_ack_ratio': 8.0,
        'packet_count': 300.0,
    }

    print("\nBorderline Case: Moderate attack signals")
    print("Features: 300 pps, SYN/ACK ratio 8.0")
    print("-" * 80)

    thresholds = [
        (0.5, 30.0, "Sensitive"),
        (0.7, 50.0, "Balanced (default)"),
        (0.85, 70.0, "Conservative"),
    ]

    for ml_thresh, anomaly_thresh, label in thresholds:
        result = engine.detect(
            features,
            ml_threshold=ml_thresh,
            anomaly_threshold=anomaly_thresh
        )

        print(f"\n{label} (ML: {ml_thresh}, Anomaly: {anomaly_thresh}):")
        print(f"  Classification: {result.threat_class}")
        print(f"  Risk Score:     {result.risk_score}/100")
        print(f"  Severity:       {result.severity}")


def demo_risk_score_breakdown():
    """Demo detailed risk score calculation."""
    print_section("Risk Score Breakdown", "-")

    engine = HybridDetectionEngine()

    # Known attack with high agreement
    print("\nScenario: SYN Flood (High Agreement)")
    print("-" * 80)

    features = {
        'packets_per_second': 1500.0,
        'bytes_per_second': 90000.0,
        'average_packet_size': 60.0,
        'syn_ack_ratio': 75.0,
        'syn_count': 1500.0,
        'ack_count': 20.0,
        'packet_count': 1520.0,
        'flow_duration': 1.0,
    }

    aggregate = {
        'unique_source_ips': 45.0,
        'source_ip_entropy': 5.2,
        'destination_concentration': 0.95,
    }

    result = engine.detect(features, aggregate)

    # Manually calculate risk breakdown
    ml_conf = result.evidence['ml_classification']['confidence']
    anomaly_score = result.evidence['anomaly_detection']['anomaly_score']
    rule_count = len(result.evidence['rule_based_detections'])
    detector_count = len(result.detectors_triggered)

    print(f"\nRisk Score: {result.risk_score}/100")
    print(f"\nBreakdown:")
    print(f"  1. Base Risk:")
    print(f"     ML Confidence: {ml_conf:.0%}")
    if result.threat_class not in ["NORMAL", "SUSPICIOUS", "UNKNOWN_ANOMALY"]:
        base = ml_conf * 60
        print(f"     Base = {ml_conf:.2f} × 60 = {base:.1f} points")

    print(f"\n  2. Anomaly Boost:")
    print(f"     Anomaly Score: {anomaly_score:.1f}/100")
    if anomaly_score >= 80:
        print(f"     Boost = +20 points (score ≥ 80)")
    elif anomaly_score >= 60:
        print(f"     Boost = +15 points (score ≥ 60)")
    elif anomaly_score >= 40:
        print(f"     Boost = +10 points (score ≥ 40)")
    else:
        print(f"     Boost = +0 points (score < 40)")

    print(f"\n  3. Rule Agreement:")
    print(f"     Rules Triggered: {rule_count}")
    if rule_count > 0:
        print(f"     Boost = up to +15 points (confidence weighted)")
    else:
        print(f"     Boost = +0 points")

    print(f"\n  4. Multi-Detector:")
    print(f"     Detectors Active: {detector_count}")
    if detector_count >= 4:
        print(f"     Boost = +5 points")
    elif detector_count == 3:
        print(f"     Boost = +4 points")
    elif detector_count == 2:
        print(f"     Boost = +2 points")
    else:
        print(f"     Boost = +0 points")

    print(f"\n  Final: {result.risk_score}/100 → {result.severity} Severity")


def demo_with_simulated_traffic():
    """Demo with traffic from simulator."""
    print_section("Detection with Simulated Traffic", "-")

    generator = TrafficGenerator()
    extractor = FlowFeatureExtractor()
    engine = HybridDetectionEngine()

    scenarios = [
        ("Normal Traffic", lambda: generator.generate_normal_traffic(intensity=0.5)),
        ("SYN Flood", lambda: generator.generate_syn_flood(intensity=0.8)),
        ("Port Scan", lambda: generator.generate_port_scan(intensity=0.6)),
    ]

    for name, generate_func in scenarios:
        print(f"\n{name}")
        print("-" * 80)

        # Generate flows
        flows = generate_func()
        print(f"Generated: {len(flows)} flows")

        # Extract features
        single_features = extractor.extract_single(flows[0])
        aggregate_features = extractor.extract_aggregate(flows)

        # Detect
        result = engine.detect(single_features, aggregate_features)

        print(f"\nDetection Result:")
        print(f"  Threat:   {result.threat_class}")
        print(f"  Risk:     {result.risk_score}/100")
        print(f"  Severity: {result.severity}")
        print(f"  Detectors: {', '.join(result.detectors_triggered)}")


def print_summary():
    """Print summary of capabilities."""
    print_section("HYBRID ENGINE CAPABILITIES", "=")

    print("""
The Hybrid Detection Engine combines:

1. RULE-BASED DETECTORS
   - Fast, interpretable detection of known patterns
   - Clear evidence and explanations
   - Instant detection (no model loading delay)

2. RANDOM FOREST CLASSIFIER
   - Supervised ML for known threat types
   - 6 classes: NORMAL, SYN_FLOOD, PORT_SCAN, C2_BEACON, DNS_TUNNEL, DATA_EXFILTRATION
   - Confidence scores via predict_proba

3. ISOLATION FOREST DETECTOR
   - Unsupervised anomaly detection
   - Detects unknown/novel attacks
   - Anomaly scores (0-100)

DECISION LOGIC:
- High ML confidence + attack = Known threat
- Low ML confidence + high anomaly = Unknown anomaly
- Rule triggered + high confidence = Rule classification
- Multiple weak signals = Suspicious
- No strong signals = Normal

RISK SCORING (0-100):
- Base Risk (0-60): Primary classification confidence
- Anomaly Boost (+0 to +20): Deviation magnitude
- Rule Agreement (+0 to +15): Statistical evidence
- Multi-Detector (+0 to +5): Agreement between methods

OUTPUT:
- Threat class with confidence
- Risk score (0-100)
- Severity (Low/Medium/High/Critical)
- Evidence from all detectors
- Human-readable explanations
- List of triggered detectors

ADVANTAGES:
+ Detects both known and unknown threats
+ Transparent risk scoring
+ Clear explanations for analysts
+ Configurable thresholds
+ Low latency (~5-10ms per detection)
""")


def main():
    """Run all demos."""
    try:
        print_summary()
        demo_basic_scenarios()
        demo_edge_cases()
        demo_threshold_sensitivity()
        demo_risk_score_breakdown()

        print_section("SIMULATION DEMO", "=")
        print("\nNote: Simulator demos require more time. Running one example...")
        demo_with_simulated_traffic()

        print_section("DEMO COMPLETE", "=")
        print("\nHybrid engine successfully demonstrated.")
        print("Ready for integration with production pipeline.")

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nPlease train models first:")
        print("  python ml/train_model.py")
        print("  python ml/train_anomaly_detector.py")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

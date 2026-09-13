"""
Threat Detection Demo for SentinelOneWay.

Demonstrates rule-based baseline detection system that identifies
network threats using configurable thresholds.
"""
from simulator.traffic_generator import TrafficGenerator
from features.extractor import FlowFeatureExtractor
from detectors import SynFloodDetector, PortScanDetector, C2BeaconDetector
from detectors.config import DetectionConfig


def demo_syn_flood_detection():
    """Demonstrate SYN flood detection."""
    print("=" * 80)
    print("DEMO 1: SYN Flood Detection")
    print("=" * 80)

    generator = TrafficGenerator()
    extractor = FlowFeatureExtractor()
    detector = SynFloodDetector()

    # Generate SYN flood traffic
    print("\nGenerating SYN flood traffic (intensity 0.8)...")
    flows = generator.generate_traffic('syn_flood', intensity=0.8)
    print(f"Generated {len(flows)} flows")

    # Extract features
    features_df = extractor.extract_batch(flows)
    mean_features = features_df.mean().to_dict()
    aggregate = extractor.extract_aggregate(flows)

    # Run detection
    detection = detector.detect(mean_features, aggregate)

    if detection:
        print(f"\n[OK] THREAT DETECTED")
        print(f"  Class: {detection.threat_class}")
        print(f"  Confidence: {detection.confidence:.2%}")
        print(f"  Severity: {detection.severity}")
        print(f"\n  Evidence:")
        for key, value in detection.evidence.items():
            print(f"    - {key}: {value}")
        print(f"\n  Explanation:")
        for i, explanation in enumerate(detection.human_explanation, 1):
            print(f"    {i}. {explanation}")
    else:
        print("\n[X] No threat detected")


def demo_port_scan_detection():
    """Demonstrate port scan detection."""
    print("\n\n" + "=" * 80)
    print("DEMO 2: Port Scan Detection")
    print("=" * 80)

    generator = TrafficGenerator()
    extractor = FlowFeatureExtractor()
    detector = PortScanDetector()

    # Generate port scan traffic
    print("\nGenerating port scan traffic (intensity 0.7)...")
    flows = generator.generate_traffic('port_scan', intensity=0.7)
    print(f"Generated {len(flows)} flows")

    # Extract features
    features_df = extractor.extract_batch(flows)
    mean_features = features_df.mean().to_dict()
    aggregate = extractor.extract_aggregate(flows)

    # Run detection
    detection = detector.detect(mean_features, aggregate)

    if detection:
        print(f"\n[OK] THREAT DETECTED")
        print(f"  Class: {detection.threat_class}")
        print(f"  Confidence: {detection.confidence:.2%}")
        print(f"  Severity: {detection.severity}")
        print(f"\n  Evidence:")
        for key, value in detection.evidence.items():
            print(f"    - {key}: {value}")
        print(f"\n  Explanation:")
        for i, explanation in enumerate(detection.human_explanation, 1):
            print(f"    {i}. {explanation}")
    else:
        print("\n[X] No threat detected")


def demo_c2_beacon_detection():
    """Demonstrate C2 beacon detection."""
    print("\n\n" + "=" * 80)
    print("DEMO 3: C2 Beacon Detection")
    print("=" * 80)

    generator = TrafficGenerator()
    extractor = FlowFeatureExtractor()
    detector = C2BeaconDetector()

    # Generate C2 beacon traffic
    print("\nGenerating C2 beacon traffic (intensity 0.6)...")
    flows = generator.generate_traffic('c2_beacon', intensity=0.6)
    print(f"Generated {len(flows)} flows")

    # Extract features
    features_df = extractor.extract_batch(flows)
    mean_features = features_df.mean().to_dict()
    aggregate = extractor.extract_aggregate(flows)

    # Run detection
    detection = detector.detect(mean_features, aggregate)

    if detection:
        print(f"\n[OK] THREAT DETECTED")
        print(f"  Class: {detection.threat_class}")
        print(f"  Confidence: {detection.confidence:.2%}")
        print(f"  Severity: {detection.severity}")
        print(f"\n  Evidence:")
        for key, value in detection.evidence.items():
            print(f"    - {key}: {value}")
        print(f"\n  Explanation:")
        for i, explanation in enumerate(detection.human_explanation, 1):
            print(f"    {i}. {explanation}")
    else:
        print("\n[X] No threat detected")


def demo_normal_traffic():
    """Demonstrate no false positives on normal traffic."""
    print("\n\n" + "=" * 80)
    print("DEMO 4: Normal Traffic (No False Positives)")
    print("=" * 80)

    generator = TrafficGenerator()
    extractor = FlowFeatureExtractor()

    detectors = {
        'SYN Flood': SynFloodDetector(),
        'Port Scan': PortScanDetector(),
        'C2 Beacon': C2BeaconDetector(),
    }

    # Generate normal traffic
    print("\nGenerating normal traffic (intensity 0.5)...")
    flows = generator.generate_traffic('normal', intensity=0.5)
    print(f"Generated {len(flows)} flows")

    # Extract features
    features_df = extractor.extract_batch(flows)
    mean_features = features_df.mean().to_dict()
    aggregate = extractor.extract_aggregate(flows)

    # Test all detectors
    print("\nTesting all detectors on normal traffic:")
    detections = []

    for name, detector in detectors.items():
        detection = detector.detect(mean_features, aggregate)
        print(f"\n  {name} Detector:")
        if detection:
            print(f"    [!] Detected (confidence: {detection.confidence:.2%})")
            detections.append((name, detection))
        else:
            print(f"    [OK] No detection")

    if not detections:
        print("\n[OK] SUCCESS: No false positives on normal traffic")
    else:
        print(f"\n[!] WARNING: {len(detections)} false positive(s)")


def demo_custom_configuration():
    """Demonstrate custom threshold configuration."""
    print("\n\n" + "=" * 80)
    print("DEMO 5: Custom Configuration")
    print("=" * 80)

    # Create custom configuration with more sensitive thresholds
    config = DetectionConfig()
    original_threshold = config.syn_flood.syn_ack_ratio_high
    config.syn_flood.syn_ack_ratio_high = 5.0  # More sensitive

    print(f"\nDefault SYN/ACK threshold: {original_threshold}")
    print(f"Custom SYN/ACK threshold: {config.syn_flood.syn_ack_ratio_high}")

    # Create detector with custom config
    detector = SynFloodDetector(config.syn_flood)

    generator = TrafficGenerator()
    extractor = FlowFeatureExtractor()

    # Test with moderate attack
    flows = generator.generate_traffic('syn_flood', intensity=0.4)
    features_df = extractor.extract_batch(flows)
    mean_features = features_df.mean().to_dict()
    aggregate = extractor.extract_aggregate(flows)

    detection = detector.detect(mean_features, aggregate)

    print(f"\nTesting with moderate SYN flood (intensity 0.4):")
    if detection:
        print(f"  [OK] Detected with custom threshold")
        print(f"  Confidence: {detection.confidence:.2%}")
        print(f"  Evidence SYN/ACK ratio: {detection.evidence.get('syn_ack_ratio', 0):.1f}")
    else:
        print(f"  [X] Not detected even with sensitive threshold")


def demo_multi_threat_analysis():
    """Demonstrate analyzing multiple threat scenarios."""
    print("\n\n" + "=" * 80)
    print("DEMO 6: Multi-Threat Analysis")
    print("=" * 80)

    generator = TrafficGenerator()
    extractor = FlowFeatureExtractor()

    scenarios = ['normal', 'syn_flood', 'port_scan', 'c2_beacon']
    detectors = [
        ('SYN Flood', SynFloodDetector()),
        ('Port Scan', PortScanDetector()),
        ('C2 Beacon', C2BeaconDetector()),
    ]

    results = []

    for scenario in scenarios:
        print(f"\n\nAnalyzing {scenario.upper()} traffic:")
        print("-" * 60)

        flows = generator.generate_traffic(scenario, intensity=0.6)
        features_df = extractor.extract_batch(flows)
        mean_features = features_df.mean().to_dict()
        aggregate = extractor.extract_aggregate(flows)

        scenario_results = {'scenario': scenario, 'detections': []}

        for detector_name, detector in detectors:
            detection = detector.detect(mean_features, aggregate)
            if detection and detection.confidence > 0.3:
                print(f"  {detector_name}: {detection.confidence:.1%} confidence")
                scenario_results['detections'].append({
                    'detector': detector_name,
                    'confidence': detection.confidence,
                    'severity': detection.severity
                })
            else:
                print(f"  {detector_name}: No detection")

        results.append(scenario_results)

    # Summary table
    print("\n\n" + "=" * 80)
    print("SUMMARY: Detection Matrix")
    print("=" * 80)
    print(f"\n{'Scenario':<20} {'SYN Flood':<15} {'Port Scan':<15} {'C2 Beacon':<15}")
    print("-" * 65)

    for result in results:
        row = f"{result['scenario']:<20}"
        for detector_name in ['SYN Flood', 'Port Scan', 'C2 Beacon']:
            detection = next((d for d in result['detections']
                            if d['detector'] == detector_name), None)
            if detection:
                row += f"{detection['confidence']:.0%} ({detection['severity'][0]})"
                row += " " * (15 - len(f"{detection['confidence']:.0%} ({detection['severity'][0]})"))
            else:
                row += "-" + " " * 14
        print(row)


if __name__ == '__main__':
    print("\n")
    print("=" * 80)
    print(" " * 25 + "SentinelOneWay Detection Demo")
    print("=" * 80)
    print("\nRule-Based Baseline Threat Detection System")
    print("Configurable thresholds, explainable detections")

    try:
        demo_syn_flood_detection()
        demo_port_scan_detection()
        demo_c2_beacon_detection()
        demo_normal_traffic()
        demo_custom_configuration()
        demo_multi_threat_analysis()

        print("\n\n" + "=" * 80)
        print("Demo completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()

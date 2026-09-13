"""
Unit tests for threat detectors.

Tests detectors using simulator-generated traffic to verify
correct detection of SYN floods, port scans, and C2 beacons.
"""
import unittest

from simulator.traffic_generator import TrafficGenerator
from features.extractor import FlowFeatureExtractor
from detectors.syn_flood import SynFloodDetector
from detectors.port_scan import PortScanDetector
from detectors.c2_beacon import C2BeaconDetector
from detectors.config import DetectionConfig


class TestSynFloodDetector(unittest.TestCase):
    """Test SYN flood detector."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = TrafficGenerator()
        self.extractor = FlowFeatureExtractor()
        self.detector = SynFloodDetector()

    def test_detects_syn_flood(self):
        """Test detector identifies SYN flood traffic."""
        # Generate SYN flood traffic
        flows = self.generator.generate_traffic('syn_flood', intensity=0.8)

        # Extract features
        features_df = self.extractor.extract_batch(flows)
        mean_features = features_df.mean().to_dict()
        aggregate = self.extractor.extract_aggregate(flows)

        # Run detection
        detection = self.detector.detect(mean_features, aggregate)

        # Verify detection
        self.assertIsNotNone(detection, "SYN flood should be detected")
        self.assertEqual(detection.threat_class, "SYN Flood")
        self.assertGreater(detection.confidence, 0.5, "Confidence should be significant")
        self.assertIn(detection.severity, ["Medium", "High", "Critical"])
        self.assertIn('syn_ack_ratio', detection.evidence)
        self.assertGreater(len(detection.human_explanation), 0)

        print(f"\nSYN Flood Detection:")
        print(f"  Confidence: {detection.confidence:.2f}")
        print(f"  Severity: {detection.severity}")
        print(f"  Evidence: {detection.evidence}")

    def test_no_false_positive_on_normal(self):
        """Test detector does not flag normal traffic."""
        # Generate normal traffic
        flows = self.generator.generate_traffic('normal', intensity=0.5)

        # Extract features
        features_df = self.extractor.extract_batch(flows)
        mean_features = features_df.mean().to_dict()
        aggregate = self.extractor.extract_aggregate(flows)

        # Run detection
        detection = self.detector.detect(mean_features, aggregate)

        # Should not detect SYN flood in normal traffic
        if detection:
            # If detected, confidence should be very low
            self.assertLess(detection.confidence, 0.3,
                          "Normal traffic should not trigger high confidence detection")

    def test_high_confidence_on_intense_attack(self):
        """Test high confidence on intense SYN flood."""
        # Generate intense SYN flood
        flows = self.generator.generate_traffic('syn_flood', intensity=1.0)

        features_df = self.extractor.extract_batch(flows)
        mean_features = features_df.mean().to_dict()
        aggregate = self.extractor.extract_aggregate(flows)

        detection = self.detector.detect(mean_features, aggregate)

        self.assertIsNotNone(detection)
        self.assertGreater(detection.confidence, 0.7,
                          "Intense attack should have high confidence")
        self.assertIn(detection.severity, ["High", "Critical"])

    def test_evidence_fields(self):
        """Test detection includes proper evidence fields."""
        flows = self.generator.generate_traffic('syn_flood', intensity=0.8)
        features_df = self.extractor.extract_batch(flows)
        mean_features = features_df.mean().to_dict()
        aggregate = self.extractor.extract_aggregate(flows)

        detection = self.detector.detect(mean_features, aggregate)

        self.assertIsNotNone(detection)
        # Should have evidence of high SYN/ACK ratio
        self.assertIn('syn_ack_ratio', detection.evidence)
        self.assertGreater(detection.evidence['syn_ack_ratio'], 10.0)


class TestPortScanDetector(unittest.TestCase):
    """Test port scan detector."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = TrafficGenerator()
        self.extractor = FlowFeatureExtractor()
        self.detector = PortScanDetector()

    def test_detects_port_scan(self):
        """Test detector identifies port scan traffic."""
        # Generate port scan traffic
        flows = self.generator.generate_traffic('port_scan', intensity=0.6)

        # Extract features
        features_df = self.extractor.extract_batch(flows)
        mean_features = features_df.mean().to_dict()
        aggregate = self.extractor.extract_aggregate(flows)

        # Run detection
        detection = self.detector.detect(mean_features, aggregate)

        # Verify detection
        self.assertIsNotNone(detection, "Port scan should be detected")
        self.assertEqual(detection.threat_class, "Port Scan")
        self.assertGreater(detection.confidence, 0.5)
        self.assertIn('unique_destination_ports', detection.evidence)
        self.assertGreater(detection.evidence['unique_destination_ports'], 100)
        self.assertGreater(len(detection.human_explanation), 0)

        print(f"\nPort Scan Detection:")
        print(f"  Confidence: {detection.confidence:.2f}")
        print(f"  Severity: {detection.severity}")
        print(f"  Ports scanned: {detection.evidence['unique_destination_ports']}")

    def test_no_false_positive_on_normal(self):
        """Test detector does not flag normal traffic."""
        flows = self.generator.generate_traffic('normal', intensity=0.5)

        features_df = self.extractor.extract_batch(flows)
        mean_features = features_df.mean().to_dict()
        aggregate = self.extractor.extract_aggregate(flows)

        detection = self.detector.detect(mean_features, aggregate)

        # Should not detect port scan in normal traffic
        if detection:
            self.assertLess(detection.confidence, 0.3)

    def test_requires_aggregate_features(self):
        """Test detector requires aggregate features."""
        flows = self.generator.generate_traffic('port_scan', intensity=0.6)
        features_df = self.extractor.extract_batch(flows)
        mean_features = features_df.mean().to_dict()

        # Run without aggregate features
        detection = self.detector.detect(mean_features, aggregate_features=None)

        # Should not detect without aggregate
        self.assertIsNone(detection,
                         "Port scan detector requires aggregate features")

    def test_high_intensity_scan(self):
        """Test detection of aggressive port scan."""
        flows = self.generator.generate_traffic('port_scan', intensity=1.0)

        features_df = self.extractor.extract_batch(flows)
        mean_features = features_df.mean().to_dict()
        aggregate = self.extractor.extract_aggregate(flows)

        detection = self.detector.detect(mean_features, aggregate)

        self.assertIsNotNone(detection)
        self.assertGreater(detection.confidence, 0.7)
        self.assertGreater(detection.evidence['unique_destination_ports'], 500)


class TestC2BeaconDetector(unittest.TestCase):
    """Test C2 beacon detector."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = TrafficGenerator()
        self.extractor = FlowFeatureExtractor()
        self.detector = C2BeaconDetector()

    def test_detects_c2_beacon(self):
        """Test detector identifies C2 beacon traffic."""
        # Generate C2 beacon traffic
        flows = self.generator.generate_traffic('c2_beacon', intensity=0.6)

        # Extract features
        features_df = self.extractor.extract_batch(flows)
        mean_features = features_df.mean().to_dict()
        aggregate = self.extractor.extract_aggregate(flows)

        # Run detection
        detection = self.detector.detect(mean_features, aggregate)

        # Verify detection
        self.assertIsNotNone(detection, "C2 beacon should be detected")
        self.assertEqual(detection.threat_class, "C2 Beacon")
        self.assertGreater(detection.confidence, 0.5)
        self.assertIn('periodicity_score', detection.evidence)
        self.assertGreater(detection.evidence['periodicity_score'], 0.7)
        self.assertGreater(len(detection.human_explanation), 0)

        print(f"\nC2 Beacon Detection:")
        print(f"  Confidence: {detection.confidence:.2f}")
        print(f"  Severity: {detection.severity}")
        print(f"  Periodicity: {detection.evidence['periodicity_score']:.3f}")
        if 'mean_inter_arrival_time' in detection.evidence:
            print(f"  Interval: {detection.evidence['mean_inter_arrival_time']:.1f}s")

    def test_no_false_positive_on_normal(self):
        """Test detector does not flag normal traffic."""
        flows = self.generator.generate_traffic('normal', intensity=0.5)

        features_df = self.extractor.extract_batch(flows)
        mean_features = features_df.mean().to_dict()
        aggregate = self.extractor.extract_aggregate(flows)

        detection = self.detector.detect(mean_features, aggregate)

        # Normal traffic should not have high periodicity
        if detection:
            self.assertLess(detection.confidence, 0.4)

    def test_requires_aggregate_features(self):
        """Test detector requires aggregate features."""
        flows = self.generator.generate_traffic('c2_beacon', intensity=0.6)
        features_df = self.extractor.extract_batch(flows)
        mean_features = features_df.mean().to_dict()

        # Run without aggregate features
        detection = self.detector.detect(mean_features, aggregate_features=None)

        # Should not detect without aggregate
        self.assertIsNone(detection,
                         "C2 beacon detector requires aggregate features")

    def test_detects_common_beacon_interval(self):
        """Test detection recognizes common beacon intervals."""
        flows = self.generator.generate_traffic('c2_beacon', intensity=0.6)

        features_df = self.extractor.extract_batch(flows)
        mean_features = features_df.mean().to_dict()
        aggregate = self.extractor.extract_aggregate(flows)

        detection = self.detector.detect(mean_features, aggregate)

        self.assertIsNotNone(detection)
        # Should detect interval close to 120s (configured in simulator)
        if 'mean_inter_arrival_time' in detection.evidence:
            interval = detection.evidence['mean_inter_arrival_time']
            self.assertLess(abs(interval - 120.0), 10.0,
                          "Should detect ~120s beacon interval")

    def test_high_periodicity_high_confidence(self):
        """Test high periodicity leads to high confidence."""
        flows = self.generator.generate_traffic('c2_beacon', intensity=0.8)

        features_df = self.extractor.extract_batch(flows)
        mean_features = features_df.mean().to_dict()
        aggregate = self.extractor.extract_aggregate(flows)

        detection = self.detector.detect(mean_features, aggregate)

        self.assertIsNotNone(detection)
        # C2 beacons have very high periodicity
        self.assertGreater(detection.evidence['periodicity_score'], 0.9)
        self.assertGreater(detection.confidence, 0.7)


class TestDetectionConfig(unittest.TestCase):
    """Test detection configuration."""

    def test_default_config_exists(self):
        """Test default configuration is valid."""
        config = DetectionConfig()

        self.assertIsNotNone(config.syn_flood)
        self.assertIsNotNone(config.port_scan)
        self.assertIsNotNone(config.c2_beacon)

        # Verify thresholds are reasonable
        self.assertGreater(config.syn_flood.syn_ack_ratio_high, 0)
        self.assertGreater(config.port_scan.unique_ports_medium, 0)
        self.assertGreater(config.c2_beacon.periodicity_medium, 0)

    def test_config_to_dict(self):
        """Test configuration can be exported to dict."""
        config = DetectionConfig()
        config_dict = config.to_dict()

        self.assertIn('syn_flood', config_dict)
        self.assertIn('port_scan', config_dict)
        self.assertIn('c2_beacon', config_dict)

    def test_config_from_dict(self):
        """Test configuration can be loaded from dict."""
        custom_config = {
            'syn_flood': {
                'syn_ack_ratio_high': 20.0
            }
        }

        config = DetectionConfig.from_dict(custom_config)
        self.assertEqual(config.syn_flood.syn_ack_ratio_high, 20.0)

    def test_detectors_accept_custom_config(self):
        """Test detectors can use custom configuration."""
        config = DetectionConfig()
        config.syn_flood.syn_ack_ratio_high = 5.0  # More sensitive

        detector = SynFloodDetector(config.syn_flood)
        self.assertEqual(detector.config.syn_ack_ratio_high, 5.0)


class TestDetectionStructure(unittest.TestCase):
    """Test detection result structure."""

    def test_detection_to_dict(self):
        """Test detection can be serialized to dict."""
        flows = TrafficGenerator().generate_traffic('syn_flood', intensity=0.8)
        extractor = FlowFeatureExtractor()
        detector = SynFloodDetector()

        features_df = extractor.extract_batch(flows)
        mean_features = features_df.mean().to_dict()
        aggregate = extractor.extract_aggregate(flows)

        detection = detector.detect(mean_features, aggregate)

        if detection:
            result_dict = detection.to_dict()

            self.assertIn('threat_class', result_dict)
            self.assertIn('confidence', result_dict)
            self.assertIn('severity', result_dict)
            self.assertIn('evidence', result_dict)
            self.assertIn('human_explanation', result_dict)

            # Verify types
            self.assertIsInstance(result_dict['confidence'], float)
            self.assertIsInstance(result_dict['evidence'], dict)
            self.assertIsInstance(result_dict['human_explanation'], list)


class TestMultiThreatScenarios(unittest.TestCase):
    """Test detection across multiple threat scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = TrafficGenerator()
        self.extractor = FlowFeatureExtractor()

    def test_all_detectors_on_respective_threats(self):
        """Test each detector on its target threat."""
        scenarios = {
            'syn_flood': SynFloodDetector(),
            'port_scan': PortScanDetector(),
            'c2_beacon': C2BeaconDetector(),
        }

        results = {}

        for scenario, detector in scenarios.items():
            flows = self.generator.generate_traffic(scenario, intensity=0.7)
            features_df = self.extractor.extract_batch(flows)
            mean_features = features_df.mean().to_dict()
            aggregate = self.extractor.extract_aggregate(flows)

            detection = detector.detect(mean_features, aggregate)

            results[scenario] = detection

        # All should detect their respective threats
        for scenario, detection in results.items():
            self.assertIsNotNone(detection,
                                f"{scenario} detector should detect {scenario} traffic")
            self.assertGreater(detection.confidence, 0.5,
                              f"{scenario} should have significant confidence")

        print("\n" + "=" * 60)
        print("Multi-Threat Detection Summary:")
        print("=" * 60)
        for scenario, detection in results.items():
            print(f"\n{scenario.upper()}:")
            print(f"  Threat: {detection.threat_class}")
            print(f"  Confidence: {detection.confidence:.2f}")
            print(f"  Severity: {detection.severity}")
            print(f"  Indicators: {len(detection.human_explanation) - 1}")


if __name__ == '__main__':
    unittest.main(verbosity=2)

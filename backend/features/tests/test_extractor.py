"""
Unit tests for flow feature extractor.

Tests feature extraction logic, edge case handling, and utility functions.
"""
import unittest
from datetime import datetime, timedelta
import math

import numpy as np
import pandas as pd

from simulator.flow_record import FlowRecord
from features.extractor import (
    FlowFeatureExtractor,
    safe_divide,
    calculate_syn_ack_ratio,
    calculate_string_entropy,
    calculate_digit_ratio,
    calculate_unique_char_ratio,
    calculate_list_entropy,
)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions for feature calculation."""

    def test_safe_divide_normal(self):
        """Test safe division with normal values."""
        self.assertEqual(safe_divide(10, 2), 5.0)
        self.assertEqual(safe_divide(7, 3), 7/3)
        self.assertEqual(safe_divide(0, 5), 0.0)

    def test_safe_divide_zero_denominator(self):
        """Test safe division handles zero denominator."""
        self.assertEqual(safe_divide(10, 0), 0.0)
        self.assertEqual(safe_divide(10, 0, default=999), 999)

    def test_safe_divide_edge_cases(self):
        """Test safe division with NaN and infinity."""
        self.assertEqual(safe_divide(float('nan'), 5), 0.0)
        self.assertEqual(safe_divide(10, float('inf')), 0.0)
        self.assertEqual(safe_divide(10, float('nan')), 0.0)

    def test_syn_ack_ratio_normal(self):
        """Test SYN/ACK ratio calculation."""
        self.assertEqual(calculate_syn_ack_ratio(10, 10), 1.0)
        self.assertEqual(calculate_syn_ack_ratio(100, 10), 10.0)
        self.assertEqual(calculate_syn_ack_ratio(5, 20), 0.25)

    def test_syn_ack_ratio_zero_ack(self):
        """Test SYN/ACK ratio with zero ACKs."""
        self.assertEqual(calculate_syn_ack_ratio(100, 0), 100.0)
        self.assertEqual(calculate_syn_ack_ratio(0, 0), 0.0)

    def test_string_entropy_normal(self):
        """Test entropy calculation."""
        # Uniform distribution
        entropy_uniform = calculate_string_entropy("abcdefgh")
        self.assertGreater(entropy_uniform, 2.5)

        # Low entropy (repeated)
        entropy_low = calculate_string_entropy("aaaaaaaa")
        self.assertEqual(entropy_low, 0.0)

        # Medium entropy
        entropy_med = calculate_string_entropy("hello")
        self.assertGreater(entropy_med, 0.0)
        self.assertLess(entropy_med, 3.0)

    def test_string_entropy_empty(self):
        """Test entropy with empty string."""
        self.assertEqual(calculate_string_entropy(""), 0.0)
        self.assertEqual(calculate_string_entropy(None), 0.0)

    def test_digit_ratio(self):
        """Test digit ratio calculation."""
        self.assertEqual(calculate_digit_ratio("123"), 1.0)
        self.assertEqual(calculate_digit_ratio("abc"), 0.0)
        self.assertEqual(calculate_digit_ratio("a1b2c3"), 0.5)
        self.assertEqual(calculate_digit_ratio(""), 0.0)

    def test_unique_char_ratio(self):
        """Test unique character ratio."""
        self.assertEqual(calculate_unique_char_ratio("abcd"), 1.0)
        self.assertEqual(calculate_unique_char_ratio("aaaa"), 0.25)
        self.assertEqual(calculate_unique_char_ratio("aabbcc"), 0.5)
        self.assertEqual(calculate_unique_char_ratio(""), 0.0)

    def test_list_entropy(self):
        """Test list entropy calculation."""
        # Uniform
        uniform = ['a', 'b', 'c', 'd']
        self.assertGreater(calculate_list_entropy(uniform), 1.5)

        # Low entropy
        repeated = ['a', 'a', 'a', 'a']
        self.assertEqual(calculate_list_entropy(repeated), 0.0)

        # Empty
        self.assertEqual(calculate_list_entropy([]), 0.0)


class TestSingleFlowExtraction(unittest.TestCase):
    """Test feature extraction from single flows."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = FlowFeatureExtractor()
        self.now = datetime.now()

    def _create_test_flow(self, **kwargs) -> FlowRecord:
        """Create a test flow with default values."""
        defaults = {
            'timestamp': self.now,
            'flow_id': 'TEST-001',
            'src_ip': '10.0.1.1',
            'dst_ip': '203.0.113.1',
            'src_port': 50000,
            'dst_port': 443,
            'protocol': 'TCP',
            'packet_count': 100,
            'byte_count': 50000,
            'duration': 10.0,
            'syn_count': 5,
            'ack_count': 5,
            'inbound_bytes': 25000,
            'outbound_bytes': 25000,
            'dns_query': None,
            'tls_fingerprint': None,
        }
        defaults.update(kwargs)
        return FlowRecord(**defaults)

    def test_traffic_features_normal(self):
        """Test basic traffic feature extraction."""
        flow = self._create_test_flow(
            packet_count=100,
            byte_count=50000,
            duration=10.0
        )

        features = self.extractor.extract_single(flow)

        self.assertEqual(features['packets_per_second'], 10.0)
        self.assertEqual(features['bytes_per_second'], 5000.0)
        self.assertEqual(features['average_packet_size'], 500.0)
        self.assertEqual(features['flow_duration'], 10.0)
        self.assertEqual(features['packet_count'], 100.0)
        self.assertEqual(features['byte_count'], 50000.0)

    def test_traffic_features_zero_duration(self):
        """Test traffic features with zero duration."""
        flow = self._create_test_flow(duration=0.0)
        features = self.extractor.extract_single(flow)

        # Should not crash, should use minimum duration
        self.assertGreater(features['packets_per_second'], 0)
        self.assertIsNotNone(features['bytes_per_second'])

    def test_tcp_features(self):
        """Test TCP-specific features."""
        flow = self._create_test_flow(
            syn_count=100,
            ack_count=10
        )

        features = self.extractor.extract_single(flow)

        self.assertEqual(features['syn_count'], 100.0)
        self.assertEqual(features['ack_count'], 10.0)
        self.assertEqual(features['syn_ack_ratio'], 10.0)

    def test_dns_features_with_query(self):
        """Test DNS features with query present."""
        flow = self._create_test_flow(
            dns_query='a1b2c3d4e5f6g7h8.malicious.com'
        )

        features = self.extractor.extract_single(flow)

        self.assertEqual(features['dns_query_length'], len('a1b2c3d4e5f6g7h8.malicious.com'))
        self.assertGreater(features['dns_entropy'], 0)
        self.assertGreater(features['dns_digit_ratio'], 0)
        self.assertEqual(features['dns_subdomain_count'], 3.0)  # 3 parts

    def test_dns_features_without_query(self):
        """Test DNS features with no query."""
        flow = self._create_test_flow(dns_query=None)

        features = self.extractor.extract_single(flow)

        self.assertEqual(features['dns_query_length'], 0.0)
        self.assertEqual(features['dns_entropy'], 0.0)
        self.assertEqual(features['dns_digit_ratio'], 0.0)
        self.assertEqual(features['dns_unique_char_ratio'], 0.0)
        self.assertEqual(features['dns_subdomain_count'], 0.0)

    def test_exfiltration_features(self):
        """Test data exfiltration features."""
        flow = self._create_test_flow(
            inbound_bytes=1000,
            outbound_bytes=100000
        )

        features = self.extractor.extract_single(flow)

        self.assertEqual(features['inbound_bytes'], 1000.0)
        self.assertEqual(features['outbound_bytes'], 100000.0)
        self.assertEqual(features['outbound_inbound_ratio'], 100.0)

    def test_exfiltration_zero_inbound(self):
        """Test exfiltration ratio with zero inbound."""
        flow = self._create_test_flow(
            inbound_bytes=0,
            outbound_bytes=50000
        )

        features = self.extractor.extract_single(flow)

        # Should not crash
        self.assertIsNotNone(features['outbound_inbound_ratio'])
        self.assertEqual(features['outbound_inbound_ratio'], 0.0)

    def test_protocol_features(self):
        """Test protocol indicator features."""
        tcp_flow = self._create_test_flow(protocol='TCP')
        udp_flow = self._create_test_flow(protocol='UDP')
        icmp_flow = self._create_test_flow(protocol='ICMP')

        tcp_features = self.extractor.extract_single(tcp_flow)
        udp_features = self.extractor.extract_single(udp_flow)
        icmp_features = self.extractor.extract_single(icmp_flow)

        self.assertEqual(tcp_features['is_tcp'], 1.0)
        self.assertEqual(tcp_features['is_udp'], 0.0)
        self.assertEqual(tcp_features['is_icmp'], 0.0)

        self.assertEqual(udp_features['is_tcp'], 0.0)
        self.assertEqual(udp_features['is_udp'], 1.0)
        self.assertEqual(udp_features['is_icmp'], 0.0)

        self.assertEqual(icmp_features['is_tcp'], 0.0)
        self.assertEqual(icmp_features['is_udp'], 0.0)
        self.assertEqual(icmp_features['is_icmp'], 1.0)


class TestBatchExtraction(unittest.TestCase):
    """Test batch feature extraction."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = FlowFeatureExtractor()
        self.now = datetime.now()

    def _create_test_flow(self, **kwargs) -> FlowRecord:
        """Create a test flow."""
        defaults = {
            'timestamp': self.now,
            'flow_id': 'TEST-001',
            'src_ip': '10.0.1.1',
            'dst_ip': '203.0.113.1',
            'src_port': 50000,
            'dst_port': 443,
            'protocol': 'TCP',
            'packet_count': 100,
            'byte_count': 50000,
            'duration': 10.0,
            'syn_count': 5,
            'ack_count': 5,
            'inbound_bytes': 25000,
            'outbound_bytes': 25000,
            'dns_query': None,
            'tls_fingerprint': None,
        }
        defaults.update(kwargs)
        return FlowRecord(**defaults)

    def test_extract_batch_multiple_flows(self):
        """Test extracting features from multiple flows."""
        flows = [
            self._create_test_flow(flow_id=f'FLOW-{i}', packet_count=i*10)
            for i in range(1, 6)
        ]

        df = self.extractor.extract_batch(flows)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 5)
        self.assertIn('packets_per_second', df.columns)
        self.assertIn('syn_ack_ratio', df.columns)

    def test_extract_batch_empty(self):
        """Test batch extraction with empty list."""
        df = self.extractor.extract_batch([])

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 0)
        self.assertIn('packets_per_second', df.columns)

    def test_extract_batch_has_all_features(self):
        """Test that all expected features are present."""
        flows = [self._create_test_flow()]
        df = self.extractor.extract_batch(flows)

        for feature in self.extractor.feature_names:
            self.assertIn(feature, df.columns,
                         f"Missing feature: {feature}")


class TestAggregateExtraction(unittest.TestCase):
    """Test aggregate feature extraction from multiple flows."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = FlowFeatureExtractor()
        self.now = datetime.now()

    def _create_test_flow(self, **kwargs) -> FlowRecord:
        """Create a test flow."""
        defaults = {
            'timestamp': self.now,
            'flow_id': 'TEST-001',
            'src_ip': '10.0.1.1',
            'dst_ip': '203.0.113.1',
            'src_port': 50000,
            'dst_port': 443,
            'protocol': 'TCP',
            'packet_count': 100,
            'byte_count': 50000,
            'duration': 10.0,
            'syn_count': 5,
            'ack_count': 5,
            'inbound_bytes': 25000,
            'outbound_bytes': 25000,
            'dns_query': None,
            'tls_fingerprint': None,
        }
        defaults.update(kwargs)
        return FlowRecord(**defaults)

    def test_reconnaissance_features_port_scan(self):
        """Test reconnaissance features detect port scanning."""
        # Single source scanning many ports
        flows = [
            self._create_test_flow(
                flow_id=f'FLOW-{i}',
                src_ip='10.0.1.1',
                dst_ip='203.0.113.1',
                dst_port=i
            )
            for i in range(1, 101)
        ]

        features = self.extractor.extract_aggregate(flows)

        self.assertEqual(features['unique_destination_ports'], 100)
        self.assertEqual(features['unique_destination_hosts'], 1)
        self.assertGreater(features['connection_rate'], 0)

    def test_ddos_features_syn_flood(self):
        """Test DDoS features detect SYN flood."""
        # Many sources targeting single destination
        flows = [
            self._create_test_flow(
                flow_id=f'FLOW-{i}',
                src_ip=f'10.0.1.{i}',
                dst_ip='203.0.113.1',
                syn_count=100,
                ack_count=1
            )
            for i in range(1, 51)
        ]

        features = self.extractor.extract_aggregate(flows)

        self.assertEqual(features['source_ip_count'], 50)
        self.assertGreater(features['source_ip_entropy'], 4.0)  # High diversity
        self.assertGreater(features['destination_concentration'], 0.9)  # Single target

    def test_c2_features_beaconing(self):
        """Test C2 features detect periodic beaconing."""
        # Regular periodic connections
        flows = [
            self._create_test_flow(
                flow_id=f'FLOW-{i}',
                timestamp=self.now + timedelta(seconds=i*120),
                src_ip='10.0.1.1',
                dst_ip='185.220.101.5',
                dst_port=8080
            )
            for i in range(10)
        ]

        features = self.extractor.extract_aggregate(flows)

        # Should detect regular 120s interval
        self.assertAlmostEqual(features['mean_inter_arrival_time'], 120.0, delta=1.0)
        self.assertGreater(features['periodicity_score'], 0.9)  # Very periodic
        self.assertEqual(features['repeated_destination_count'], 10.0)

    def test_c2_features_irregular_timing(self):
        """Test C2 features with irregular timing."""
        # Highly irregular timing
        import random
        random.seed(42)
        flows = [
            self._create_test_flow(
                flow_id=f'FLOW-{i}',
                timestamp=self.now + timedelta(seconds=random.randint(0, 1000)),
                dst_port=8080
            )
            for i in range(10)
        ]

        features = self.extractor.extract_aggregate(flows)

        # Should have lower periodicity than regular beaconing
        self.assertLess(features['periodicity_score'], 0.95)

    def test_aggregate_empty_flows(self):
        """Test aggregate features with empty flow list."""
        features = self.extractor.extract_aggregate([])

        self.assertEqual(features['unique_destination_ports'], 0.0)
        self.assertEqual(features['source_ip_count'], 0.0)
        self.assertEqual(features['mean_inter_arrival_time'], 0.0)

    def test_aggregate_single_flow(self):
        """Test aggregate features with single flow."""
        flows = [self._create_test_flow()]
        features = self.extractor.extract_aggregate(flows)

        # Should not crash, should return reasonable values
        self.assertIsNotNone(features['unique_destination_ports'])
        # With single flow, no repeated destinations
        self.assertGreaterEqual(features['repeated_destination_count'], 0.0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = FlowFeatureExtractor()
        self.now = datetime.now()

    def test_malformed_flow_minimal_data(self):
        """Test with flow containing minimal required fields."""
        flow = FlowRecord(
            timestamp=self.now,
            flow_id='TEST',
            src_ip='10.0.0.1',
            dst_ip='10.0.0.2',
            src_port=1234,
            dst_port=80,
            protocol='TCP',
            packet_count=0,
            byte_count=0,
            duration=0.0,
            syn_count=0,
            ack_count=0,
            inbound_bytes=0,
            outbound_bytes=0,
        )

        # Should not crash
        features = self.extractor.extract_single(flow)
        self.assertIsInstance(features, dict)

    def test_very_large_values(self):
        """Test with very large packet/byte counts."""
        flow = FlowRecord(
            timestamp=self.now,
            flow_id='TEST',
            src_ip='10.0.0.1',
            dst_ip='10.0.0.2',
            src_port=1234,
            dst_port=80,
            protocol='TCP',
            packet_count=10_000_000,
            byte_count=10_000_000_000,
            duration=1.0,
            syn_count=0,
            ack_count=0,
            inbound_bytes=0,
            outbound_bytes=10_000_000_000,
        )

        features = self.extractor.extract_single(flow)

        self.assertIsInstance(features['packets_per_second'], float)
        self.assertFalse(math.isnan(features['packets_per_second']))
        self.assertFalse(math.isinf(features['packets_per_second']))


if __name__ == '__main__':
    unittest.main()

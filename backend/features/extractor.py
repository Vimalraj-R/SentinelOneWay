"""
Flow feature extractor for SentinelOneWay.

Converts raw network flow metadata into numerical features
for machine learning models. Handles synthetic flows generated
by the simulator or read from passive monitoring.
"""
import math
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter
from datetime import datetime

import pandas as pd
import numpy as np

from simulator.flow_record import FlowRecord


class FlowFeatureExtractor:
    """
    Extracts numerical features from network flow records.

    Converts raw flow metadata into engineered features suitable
    for threat detection models.
    """

    def __init__(self):
        """Initialize feature extractor."""
        self.feature_names = self._get_feature_names()

    def _get_feature_names(self) -> List[str]:
        """Get list of all feature names."""
        return [
            # Traffic features
            'packets_per_second',
            'bytes_per_second',
            'average_packet_size',
            'flow_duration',
            'packet_count',
            'byte_count',

            # TCP features
            'syn_count',
            'ack_count',
            'syn_ack_ratio',

            # DNS features
            'dns_query_length',
            'dns_entropy',
            'dns_digit_ratio',
            'dns_unique_char_ratio',
            'dns_subdomain_count',

            # Exfiltration features
            'inbound_bytes',
            'outbound_bytes',
            'outbound_inbound_ratio',

            # Protocol indicator
            'is_tcp',
            'is_udp',
            'is_icmp',
        ]

    def extract_single(self, flow: FlowRecord) -> Dict[str, float]:
        """
        Extract features from a single flow record.

        Args:
            flow: FlowRecord to extract features from

        Returns:
            Dictionary of feature name -> value
        """
        features = {}

        # Traffic features
        features.update(self._extract_traffic_features(flow))

        # TCP features
        features.update(self._extract_tcp_features(flow))

        # DNS features
        features.update(self._extract_dns_features(flow))

        # Exfiltration features
        features.update(self._extract_exfiltration_features(flow))

        # Protocol features
        features.update(self._extract_protocol_features(flow))

        return features

    def extract_batch(self, flows: List[FlowRecord]) -> pd.DataFrame:
        """
        Extract features from multiple flows.

        Args:
            flows: List of FlowRecords

        Returns:
            DataFrame with one row per flow, columns are features
        """
        if not flows:
            return pd.DataFrame(columns=self.feature_names)

        feature_dicts = [self.extract_single(flow) for flow in flows]
        df = pd.DataFrame(feature_dicts)

        # Ensure all expected columns exist
        for col in self.feature_names:
            if col not in df.columns:
                df[col] = 0.0

        return df[self.feature_names]

    def extract_aggregate(self, flows: List[FlowRecord], window_seconds: int = 60) -> Dict[str, float]:
        """
        Extract aggregate features from multiple flows in a time window.

        Useful for detecting patterns that span multiple flows:
        - Port scans (many unique ports)
        - DDoS (many unique sources)
        - C2 beaconing (periodicity)

        Args:
            flows: List of FlowRecords
            window_seconds: Time window for aggregation

        Returns:
            Dictionary of aggregate features
        """
        if not flows:
            return self._empty_aggregate_features()

        features = {}

        # Reconnaissance features
        features.update(self._extract_reconnaissance_features(flows))

        # DDoS features
        features.update(self._extract_ddos_features(flows))

        # C2 beaconing features
        features.update(self._extract_c2_features(flows))

        return features

    # ===== Traffic Features =====

    def _extract_traffic_features(self, flow: FlowRecord) -> Dict[str, float]:
        """Extract basic traffic rate and volume features."""
        duration = max(flow.duration, 0.001)  # Avoid division by zero

        return {
            'packets_per_second': safe_divide(flow.packet_count, duration),
            'bytes_per_second': safe_divide(flow.byte_count, duration),
            'average_packet_size': safe_divide(flow.byte_count, flow.packet_count),
            'flow_duration': flow.duration,
            'packet_count': float(flow.packet_count),
            'byte_count': float(flow.byte_count),
        }

    # ===== TCP Features =====

    def _extract_tcp_features(self, flow: FlowRecord) -> Dict[str, float]:
        """Extract TCP-specific features."""
        return {
            'syn_count': float(flow.syn_count),
            'ack_count': float(flow.ack_count),
            'syn_ack_ratio': calculate_syn_ack_ratio(flow.syn_count, flow.ack_count),
        }

    # ===== DNS Features =====

    def _extract_dns_features(self, flow: FlowRecord) -> Dict[str, float]:
        """Extract DNS query analysis features."""
        if not flow.dns_query:
            return {
                'dns_query_length': 0.0,
                'dns_entropy': 0.0,
                'dns_digit_ratio': 0.0,
                'dns_unique_char_ratio': 0.0,
                'dns_subdomain_count': 0.0,
            }

        query = flow.dns_query

        return {
            'dns_query_length': float(len(query)),
            'dns_entropy': calculate_string_entropy(query),
            'dns_digit_ratio': calculate_digit_ratio(query),
            'dns_unique_char_ratio': calculate_unique_char_ratio(query),
            'dns_subdomain_count': float(query.count('.') + 1),
        }

    # ===== Exfiltration Features =====

    def _extract_exfiltration_features(self, flow: FlowRecord) -> Dict[str, float]:
        """Extract data exfiltration indicators."""
        return {
            'inbound_bytes': float(flow.inbound_bytes),
            'outbound_bytes': float(flow.outbound_bytes),
            'outbound_inbound_ratio': safe_divide(
                flow.outbound_bytes,
                flow.inbound_bytes
            ),
        }

    # ===== Protocol Features =====

    def _extract_protocol_features(self, flow: FlowRecord) -> Dict[str, float]:
        """Extract protocol type indicators."""
        protocol = flow.protocol.upper()
        return {
            'is_tcp': 1.0 if protocol == 'TCP' else 0.0,
            'is_udp': 1.0 if protocol == 'UDP' else 0.0,
            'is_icmp': 1.0 if protocol == 'ICMP' else 0.0,
        }

    # ===== Aggregate Features (Multi-Flow) =====

    def _extract_reconnaissance_features(self, flows: List[FlowRecord]) -> Dict[str, float]:
        """Extract port scan and reconnaissance indicators."""
        if not flows:
            return {
                'unique_destination_ports': 0.0,
                'unique_destination_hosts': 0.0,
                'connection_rate': 0.0,
                'fanout_score': 0.0,
            }

        dst_ports = set(flow.dst_port for flow in flows)
        dst_hosts = set(flow.dst_ip for flow in flows)
        src_hosts = set(flow.src_ip for flow in flows)

        # Time span
        timestamps = [flow.timestamp for flow in flows]
        time_span = (max(timestamps) - min(timestamps)).total_seconds() or 1.0

        # Fanout: how many destinations per source
        fanout = safe_divide(len(dst_hosts), len(src_hosts))

        return {
            'unique_destination_ports': float(len(dst_ports)),
            'unique_destination_hosts': float(len(dst_hosts)),
            'connection_rate': safe_divide(len(flows), time_span),
            'fanout_score': fanout,
        }

    def _extract_ddos_features(self, flows: List[FlowRecord]) -> Dict[str, float]:
        """Extract DDoS attack indicators."""
        if not flows:
            return {
                'source_ip_count': 0.0,
                'source_ip_entropy': 0.0,
                'destination_concentration': 0.0,
                'aggregate_packet_rate': 0.0,
            }

        src_ips = [flow.src_ip for flow in flows]
        dst_ips = [flow.dst_ip for flow in flows]

        # Source diversity
        unique_sources = len(set(src_ips))
        source_entropy = calculate_list_entropy(src_ips)

        # Destination concentration
        dst_counter = Counter(dst_ips)
        most_common_dst_count = dst_counter.most_common(1)[0][1]
        dst_concentration = safe_divide(most_common_dst_count, len(flows))

        # Aggregate packet rate
        total_packets = sum(flow.packet_count for flow in flows)
        timestamps = [flow.timestamp for flow in flows]
        time_span = (max(timestamps) - min(timestamps)).total_seconds() or 1.0

        return {
            'source_ip_count': float(unique_sources),
            'source_ip_entropy': source_entropy,
            'destination_concentration': dst_concentration,
            'aggregate_packet_rate': safe_divide(total_packets, time_span),
        }

    def _extract_c2_features(self, flows: List[FlowRecord]) -> Dict[str, float]:
        """Extract C2 beaconing indicators."""
        if len(flows) < 2:
            return {
                'mean_inter_arrival_time': 0.0,
                'inter_arrival_std': 0.0,
                'periodicity_score': 0.0,
                'repeated_destination_count': 0.0,
            }

        # Sort by timestamp
        sorted_flows = sorted(flows, key=lambda f: f.timestamp)

        # Inter-arrival times
        inter_arrival_times = []
        for i in range(1, len(sorted_flows)):
            delta = (sorted_flows[i].timestamp - sorted_flows[i-1].timestamp).total_seconds()
            inter_arrival_times.append(delta)

        mean_iat = np.mean(inter_arrival_times) if inter_arrival_times else 0.0
        std_iat = np.std(inter_arrival_times) if len(inter_arrival_times) > 1 else 0.0

        # Periodicity: low coefficient of variation indicates regular timing
        cv = safe_divide(std_iat, mean_iat)
        periodicity = 1.0 / (1.0 + cv) if cv > 0 else 1.0

        # Repeated destinations
        dst_pairs = [(flow.dst_ip, flow.dst_port) for flow in flows]
        dst_counter = Counter(dst_pairs)
        max_repeated = max(dst_counter.values()) if dst_counter else 0

        return {
            'mean_inter_arrival_time': mean_iat,
            'inter_arrival_std': std_iat,
            'periodicity_score': periodicity,
            'repeated_destination_count': float(max_repeated),
        }

    def _empty_aggregate_features(self) -> Dict[str, float]:
        """Return zero-filled aggregate features."""
        return {
            # Reconnaissance
            'unique_destination_ports': 0.0,
            'unique_destination_hosts': 0.0,
            'connection_rate': 0.0,
            'fanout_score': 0.0,
            # DDoS
            'source_ip_count': 0.0,
            'source_ip_entropy': 0.0,
            'destination_concentration': 0.0,
            'aggregate_packet_rate': 0.0,
            # C2
            'mean_inter_arrival_time': 0.0,
            'inter_arrival_std': 0.0,
            'periodicity_score': 0.0,
            'repeated_destination_count': 0.0,
        }


# ===== Utility Functions =====

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safe division that handles zero denominator.

    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value if division fails

    Returns:
        Division result or default
    """
    try:
        if denominator == 0 or math.isnan(denominator) or math.isinf(denominator):
            return default
        result = numerator / denominator
        if math.isnan(result) or math.isinf(result):
            return default
        return result
    except (ZeroDivisionError, TypeError):
        return default


def calculate_syn_ack_ratio(syn_count: int, ack_count: int) -> float:
    """
    Calculate SYN/ACK ratio.

    High ratio indicates potential SYN flood.

    Args:
        syn_count: Number of SYN packets
        ack_count: Number of ACK packets

    Returns:
        SYN/ACK ratio
    """
    if ack_count == 0:
        return float(syn_count) if syn_count > 0 else 0.0
    return safe_divide(float(syn_count), float(ack_count))


def calculate_string_entropy(s: str) -> float:
    """
    Calculate Shannon entropy of a string.

    High entropy indicates random/encrypted data, often seen in
    DNS tunneling or DGA domains.

    Args:
        s: Input string

    Returns:
        Entropy value (0.0 to ~5.0 for typical text)
    """
    if not s:
        return 0.0

    # Count character frequencies
    char_counts = Counter(s)
    length = len(s)

    # Calculate entropy
    entropy = 0.0
    for count in char_counts.values():
        probability = count / length
        if probability > 0:
            entropy -= probability * math.log2(probability)

    return entropy


def calculate_digit_ratio(s: str) -> float:
    """
    Calculate ratio of digits to total characters.

    High digit ratio in DNS queries can indicate tunneling.

    Args:
        s: Input string

    Returns:
        Digit ratio (0.0 to 1.0)
    """
    if not s:
        return 0.0

    digit_count = sum(1 for c in s if c.isdigit())
    return safe_divide(digit_count, len(s))


def calculate_unique_char_ratio(s: str) -> float:
    """
    Calculate ratio of unique characters to total length.

    Low ratio indicates repetitive patterns.

    Args:
        s: Input string

    Returns:
        Unique character ratio (0.0 to 1.0)
    """
    if not s:
        return 0.0

    unique_count = len(set(s))
    return safe_divide(unique_count, len(s))


def calculate_list_entropy(items: List[Any]) -> float:
    """
    Calculate Shannon entropy of a list of items.

    High entropy indicates high diversity (many different sources).
    Low entropy indicates concentration (few repeated sources).

    Args:
        items: List of items

    Returns:
        Entropy value
    """
    if not items:
        return 0.0

    # Count item frequencies
    item_counts = Counter(items)
    total = len(items)

    # Calculate entropy
    entropy = 0.0
    for count in item_counts.values():
        probability = count / total
        if probability > 0:
            entropy -= probability * math.log2(probability)

    return entropy

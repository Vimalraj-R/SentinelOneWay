"""
Feature Engineering Demo for SentinelOneWay.

Demonstrates how to extract features from simulated network flows
for use in machine learning models.
"""
import pandas as pd
from tabulate import tabulate

from simulator.traffic_generator import TrafficGenerator
from features.extractor import FlowFeatureExtractor


def demo_single_flow_features():
    """Demonstrate feature extraction from single flows."""
    print("=" * 80)
    print("DEMO 1: Single Flow Feature Extraction")
    print("=" * 80)

    generator = TrafficGenerator()
    extractor = FlowFeatureExtractor()

    # Generate different types of traffic
    scenarios = ['normal', 'syn_flood', 'port_scan', 'c2_beacon', 'dns_tunnel']

    for scenario in scenarios:
        print(f"\n{scenario.upper()} Traffic:")
        print("-" * 80)

        flows = generator.generate_traffic(scenario, intensity=0.5)
        flow = flows[0]  # Take first flow

        print(f"\nRaw Flow:")
        print(f"  {flow.src_ip}:{flow.src_port} -> {flow.dst_ip}:{flow.dst_port}")
        print(f"  Protocol: {flow.protocol}")
        print(f"  Packets: {flow.packet_count}, Bytes: {flow.byte_count}")
        print(f"  Duration: {flow.duration:.3f}s")
        print(f"  SYN: {flow.syn_count}, ACK: {flow.ack_count}")

        features = extractor.extract_single(flow)

        print(f"\nExtracted Features (top 10):")
        sorted_features = sorted(features.items(), key=lambda x: abs(x[1]), reverse=True)[:10]
        for name, value in sorted_features:
            print(f"  {name:30s}: {value:10.2f}")


def demo_batch_extraction():
    """Demonstrate batch feature extraction."""
    print("\n\n" + "=" * 80)
    print("DEMO 2: Batch Feature Extraction")
    print("=" * 80)

    generator = TrafficGenerator()
    extractor = FlowFeatureExtractor()

    # Generate SYN flood traffic
    print("\nGenerating 50 SYN flood flows...")
    flows = generator.generate_traffic('syn_flood', intensity=0.5)[:50]

    print(f"Extracting features from {len(flows)} flows...")
    df = extractor.extract_batch(flows)

    print(f"\nDataFrame shape: {df.shape}")
    print(f"Columns: {len(df.columns)}")
    print(f"\nFirst 5 rows:")
    print(df.head().to_string())

    print(f"\nFeature Statistics:")
    stats = df[['packets_per_second', 'syn_ack_ratio', 'average_packet_size']].describe()
    print(stats.to_string())


def demo_aggregate_features():
    """Demonstrate aggregate feature extraction."""
    print("\n\n" + "=" * 80)
    print("DEMO 3: Aggregate Features (Multi-Flow Patterns)")
    print("=" * 80)

    generator = TrafficGenerator()
    extractor = FlowFeatureExtractor()

    scenarios = {
        'port_scan': 'Port Scan Detection',
        'syn_flood': 'DDoS Detection',
        'c2_beacon': 'C2 Beaconing Detection'
    }

    results = []

    for scenario, description in scenarios.items():
        print(f"\n{description}:")
        print("-" * 80)

        flows = generator.generate_traffic(scenario, intensity=0.6)

        aggregate = extractor.extract_aggregate(flows)

        print(f"Generated {len(flows)} flows")
        print(f"\nAggregate Features:")
        for name, value in sorted(aggregate.items()):
            print(f"  {name:35s}: {value:10.2f}")

        results.append({
            'Scenario': scenario,
            'Flows': len(flows),
            'Unique Ports': aggregate['unique_destination_ports'],
            'Source Entropy': aggregate['source_ip_entropy'],
            'Periodicity': aggregate['periodicity_score'],
        })

    print("\n\nComparison Table:")
    print(tabulate(results, headers='keys', tablefmt='grid'))


def demo_threat_indicators():
    """Demonstrate extracting threat-specific indicators."""
    print("\n\n" + "=" * 80)
    print("DEMO 4: Threat-Specific Indicators")
    print("=" * 80)

    generator = TrafficGenerator()
    extractor = FlowFeatureExtractor()

    print("\n1. DNS TUNNELING INDICATORS")
    print("-" * 80)
    dns_flows = generator.generate_traffic('dns_tunnel', intensity=0.5)
    dns_features = extractor.extract_batch(dns_flows)

    print(f"DNS Query Lengths: {dns_features['dns_query_length'].describe()}")
    print(f"DNS Entropy: mean={dns_features['dns_entropy'].mean():.2f}, "
          f"max={dns_features['dns_entropy'].max():.2f}")
    print(f"High entropy DNS queries: {(dns_features['dns_entropy'] > 4.0).sum()}/{len(dns_flows)}")

    print("\n2. DATA EXFILTRATION INDICATORS")
    print("-" * 80)
    exfil_flows = generator.generate_traffic('data_exfiltration', intensity=0.5)
    exfil_features = extractor.extract_batch(exfil_flows)

    print(f"Outbound/Inbound Ratios:")
    print(f"  Mean: {exfil_features['outbound_inbound_ratio'].mean():.2f}")
    print(f"  Max: {exfil_features['outbound_inbound_ratio'].max():.2f}")
    print(f"  High ratio (>50): {(exfil_features['outbound_inbound_ratio'] > 50).sum()}/{len(exfil_flows)}")

    print("\n3. SYN FLOOD INDICATORS")
    print("-" * 80)
    syn_flows = generator.generate_traffic('syn_flood', intensity=0.8)
    syn_features = extractor.extract_batch(syn_flows)

    print(f"SYN/ACK Ratios:")
    print(f"  Mean: {syn_features['syn_ack_ratio'].mean():.2f}")
    print(f"  Max: {syn_features['syn_ack_ratio'].max():.2f}")
    print(f"  Suspicious (>10): {(syn_features['syn_ack_ratio'] > 10).sum()}/{len(syn_flows)}")


def demo_ml_pipeline_prep():
    """Demonstrate preparing features for ML pipeline."""
    print("\n\n" + "=" * 80)
    print("DEMO 5: ML Pipeline Preparation")
    print("=" * 80)

    generator = TrafficGenerator()
    extractor = FlowFeatureExtractor()

    print("\nGenerating labeled dataset from multiple scenarios...")

    data = []

    scenarios_labels = {
        'normal': 0,
        'syn_flood': 1,
        'port_scan': 2,
        'c2_beacon': 3,
        'dns_tunnel': 4,
        'data_exfiltration': 5
    }

    for scenario, label in scenarios_labels.items():
        print(f"  Generating {scenario}...")
        flows = generator.generate_traffic(scenario, intensity=0.5)[:20]
        features_df = extractor.extract_batch(flows)
        features_df['label'] = label
        features_df['scenario'] = scenario
        data.append(features_df)

    # Combine all scenarios
    full_df = pd.concat(data, ignore_index=True)

    print(f"\nDataset created:")
    print(f"  Total samples: {len(full_df)}")
    print(f"  Features: {len(full_df.columns) - 2}")  # -2 for label and scenario
    print(f"  Classes: {full_df['label'].nunique()}")

    print(f"\nClass distribution:")
    print(full_df['scenario'].value_counts().to_string())

    print(f"\nSample features (first 3 rows):")
    print(full_df[['packets_per_second', 'syn_ack_ratio', 'dns_entropy',
                    'outbound_inbound_ratio', 'scenario']].head(3).to_string())

    print(f"\nDataset ready for ML model training!")
    print(f"  X = df.drop(['label', 'scenario'], axis=1)")
    print(f"  y = df['label']")


if __name__ == '__main__':
    print("\n")
    print("=" * 80)
    print(" " * 20 + "SentinelOneWay Feature Engineering Demo")
    print("=" * 80)

    try:
        demo_single_flow_features()
        demo_batch_extraction()
        demo_aggregate_features()
        demo_threat_indicators()
        demo_ml_pipeline_prep()

        print("\n\n" + "=" * 80)
        print("Demo completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()

"""
Dataset generation pipeline for SentinelOneWay ML training.

Generates labeled feature records from synthetic traffic flows
with varied, realistic parameters to avoid overfitting.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from simulator.traffic_generator import TrafficGenerator
from features.extractor import FlowFeatureExtractor


class ThreatClass:
    """Threat class labels for ML training."""
    NORMAL = 0
    SYN_FLOOD = 1
    PORT_SCAN = 2
    C2_BEACON = 3
    DNS_TUNNEL = 4
    DATA_EXFILTRATION = 5

    @staticmethod
    def get_label_name(label: int) -> str:
        """Get human-readable name for label."""
        mapping = {
            0: 'NORMAL',
            1: 'SYN_FLOOD',
            2: 'PORT_SCAN',
            3: 'C2_BEACON',
            4: 'DNS_TUNNEL',
            5: 'DATA_EXFILTRATION'
        }
        return mapping.get(label, 'UNKNOWN')

    @staticmethod
    def get_all_labels() -> Dict[str, int]:
        """Get all class labels."""
        return {
            'normal': ThreatClass.NORMAL,
            'syn_flood': ThreatClass.SYN_FLOOD,
            'port_scan': ThreatClass.PORT_SCAN,
            'c2_beacon': ThreatClass.C2_BEACON,
            'dns_tunnel': ThreatClass.DNS_TUNNEL,
            'data_exfiltration': ThreatClass.DATA_EXFILTRATION
        }


class DatasetGenerator:
    """
    Generate ML training dataset from synthetic traffic.

    Creates varied, labeled examples across all threat classes
    with randomized parameters to avoid overfitting.
    """

    def __init__(self, random_seed: Optional[int] = None):
        """
        Initialize dataset generator.

        Args:
            random_seed: Random seed for reproducibility
        """
        self.generator = TrafficGenerator()
        self.extractor = FlowFeatureExtractor()
        self.random_seed = random_seed

        if random_seed is not None:
            random.seed(random_seed)
            np.random.seed(random_seed)

    def generate_scenario_samples(self,
                                  scenario: str,
                                  label: int,
                                  num_samples: int,
                                  intensity_range: Tuple[float, float] = (0.3, 1.0),
                                  flows_per_sample_range: Tuple[int, int] = (10, 50)
                                  ) -> pd.DataFrame:
        """
        Generate varied samples for a scenario.

        Each sample represents a different "observation" with randomized
        parameters to create diversity in the dataset.

        Args:
            scenario: Traffic scenario name
            label: Numeric label for this class
            num_samples: Number of samples to generate
            intensity_range: Range for randomizing intensity
            flows_per_sample_range: Range for flows per sample

        Returns:
            DataFrame with features and labels
        """
        samples = []

        for i in range(num_samples):
            # Randomize intensity
            intensity = random.uniform(*intensity_range)

            # Randomize number of flows per sample
            # This creates variation in aggregate features
            num_flows = random.randint(*flows_per_sample_range)

            # Generate flows
            flows = self.generator.generate_traffic(scenario, intensity)

            # Take random subset if needed
            if len(flows) > num_flows:
                flows = random.sample(flows, num_flows)
            elif len(flows) == 0:
                continue  # Skip if no flows generated

            # Extract single-flow features (mean of all flows in sample)
            features_df = self.extractor.extract_batch(flows)
            mean_features = features_df.mean().to_dict()

            # Extract aggregate features
            aggregate_features = self.extractor.extract_aggregate(flows)

            # Combine features
            combined_features = {**mean_features, **aggregate_features}

            # Add label
            combined_features['label'] = label
            combined_features['label_name'] = ThreatClass.get_label_name(label)

            samples.append(combined_features)

        return pd.DataFrame(samples)

    def generate_normal_samples(self, num_samples: int) -> pd.DataFrame:
        """
        Generate normal traffic samples with extra variation.

        Normal traffic is more diverse than attack traffic,
        so we add extra randomization.

        Args:
            num_samples: Number of normal samples

        Returns:
            DataFrame with normal traffic features
        """
        return self.generate_scenario_samples(
            scenario='normal',
            label=ThreatClass.NORMAL,
            num_samples=num_samples,
            intensity_range=(0.2, 0.8),  # More varied intensity
            flows_per_sample_range=(5, 20)  # Fewer flows per sample
        )

    def generate_syn_flood_samples(self, num_samples: int) -> pd.DataFrame:
        """Generate SYN flood attack samples."""
        return self.generate_scenario_samples(
            scenario='syn_flood',
            label=ThreatClass.SYN_FLOOD,
            num_samples=num_samples,
            intensity_range=(0.4, 1.0),
            flows_per_sample_range=(20, 80)  # Many flows for DDoS
        )

    def generate_port_scan_samples(self, num_samples: int) -> pd.DataFrame:
        """Generate port scan samples."""
        return self.generate_scenario_samples(
            scenario='port_scan',
            label=ThreatClass.PORT_SCAN,
            num_samples=num_samples,
            intensity_range=(0.3, 1.0),
            flows_per_sample_range=(50, 200)  # Many flows for scanning
        )

    def generate_c2_beacon_samples(self, num_samples: int) -> pd.DataFrame:
        """Generate C2 beacon samples."""
        return self.generate_scenario_samples(
            scenario='c2_beacon',
            label=ThreatClass.C2_BEACON,
            num_samples=num_samples,
            intensity_range=(0.3, 0.9),
            flows_per_sample_range=(5, 20)  # Fewer flows, but periodic
        )

    def generate_dns_tunnel_samples(self, num_samples: int) -> pd.DataFrame:
        """Generate DNS tunnel samples."""
        return self.generate_scenario_samples(
            scenario='dns_tunnel',
            label=ThreatClass.DNS_TUNNEL,
            num_samples=num_samples,
            intensity_range=(0.3, 1.0),
            flows_per_sample_range=(10, 50)
        )

    def generate_data_exfiltration_samples(self, num_samples: int) -> pd.DataFrame:
        """Generate data exfiltration samples."""
        return self.generate_scenario_samples(
            scenario='data_exfiltration',
            label=ThreatClass.DATA_EXFILTRATION,
            num_samples=num_samples,
            intensity_range=(0.3, 1.0),
            flows_per_sample_range=(2, 10)  # Few large flows
        )

    def generate_dataset(self,
                        samples_per_class: int = 500,
                        class_weights: Optional[Dict[str, float]] = None
                        ) -> pd.DataFrame:
        """
        Generate complete ML training dataset.

        Args:
            samples_per_class: Base number of samples per class
            class_weights: Optional weights to adjust class distribution
                          (e.g., {'normal': 2.0} generates 2x normal samples)

        Returns:
            Complete dataset with all classes
        """
        if class_weights is None:
            class_weights = {
                'normal': 1.5,  # More normal samples (common in real networks)
                'syn_flood': 1.0,
                'port_scan': 1.0,
                'c2_beacon': 0.8,
                'dns_tunnel': 0.8,
                'data_exfiltration': 0.6
            }

        print(f"Generating ML training dataset...")
        print(f"Base samples per class: {samples_per_class}")
        print(f"Random seed: {self.random_seed}")
        print()

        datasets = []

        # Generate NORMAL traffic
        num_normal = int(samples_per_class * class_weights['normal'])
        print(f"Generating {num_normal} NORMAL samples...")
        normal_df = self.generate_normal_samples(num_normal)
        datasets.append(normal_df)
        print(f"  Generated: {len(normal_df)} samples")

        # Generate SYN FLOOD
        num_syn = int(samples_per_class * class_weights['syn_flood'])
        print(f"Generating {num_syn} SYN_FLOOD samples...")
        syn_df = self.generate_syn_flood_samples(num_syn)
        datasets.append(syn_df)
        print(f"  Generated: {len(syn_df)} samples")

        # Generate PORT SCAN
        num_port = int(samples_per_class * class_weights['port_scan'])
        print(f"Generating {num_port} PORT_SCAN samples...")
        port_df = self.generate_port_scan_samples(num_port)
        datasets.append(port_df)
        print(f"  Generated: {len(port_df)} samples")

        # Generate C2 BEACON
        num_c2 = int(samples_per_class * class_weights['c2_beacon'])
        print(f"Generating {num_c2} C2_BEACON samples...")
        c2_df = self.generate_c2_beacon_samples(num_c2)
        datasets.append(c2_df)
        print(f"  Generated: {len(c2_df)} samples")

        # Generate DNS TUNNEL
        num_dns = int(samples_per_class * class_weights['dns_tunnel'])
        print(f"Generating {num_dns} DNS_TUNNEL samples...")
        dns_df = self.generate_dns_tunnel_samples(num_dns)
        datasets.append(dns_df)
        print(f"  Generated: {len(dns_df)} samples")

        # Generate DATA EXFILTRATION
        num_exfil = int(samples_per_class * class_weights['data_exfiltration'])
        print(f"Generating {num_exfil} DATA_EXFILTRATION samples...")
        exfil_df = self.generate_data_exfiltration_samples(num_exfil)
        datasets.append(exfil_df)
        print(f"  Generated: {len(exfil_df)} samples")

        # Combine all datasets
        print(f"\nCombining datasets...")
        combined_df = pd.concat(datasets, ignore_index=True)

        # Shuffle dataset
        print(f"Shuffling dataset...")
        combined_df = combined_df.sample(frac=1, random_state=self.random_seed).reset_index(drop=True)

        print(f"\nDataset generation complete!")
        print(f"Total samples: {len(combined_df)}")
        print(f"Features: {len(combined_df.columns) - 2}")  # -2 for label and label_name

        return combined_df

    def save_dataset(self, df: pd.DataFrame, output_path: str):
        """
        Save dataset to CSV file.

        Args:
            df: Dataset DataFrame
            output_path: Path to save CSV
        """
        # Create directory if needed
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Save to CSV
        df.to_csv(output_path, index=False)
        print(f"\nDataset saved to: {output_path}")
        print(f"File size: {Path(output_path).stat().st_size / 1024 / 1024:.2f} MB")

    def get_dataset_info(self, df: pd.DataFrame) -> Dict:
        """
        Get dataset statistics.

        Args:
            df: Dataset DataFrame

        Returns:
            Dictionary with dataset information
        """
        info = {
            'total_samples': len(df),
            'num_features': len(df.columns) - 2,  # Exclude label and label_name
            'class_distribution': df['label_name'].value_counts().to_dict(),
            'missing_values': df.isnull().sum().sum(),
            'duplicate_rows': df.duplicated().sum(),
            'feature_names': [col for col in df.columns if col not in ['label', 'label_name']]
        }
        return info


def main():
    """Main function to generate dataset."""
    # Configuration
    RANDOM_SEED = 42
    SAMPLES_PER_CLASS = 500
    OUTPUT_PATH = 'datasets/network_flows.csv'

    # Create generator
    generator = DatasetGenerator(random_seed=RANDOM_SEED)

    # Generate dataset
    dataset = generator.generate_dataset(samples_per_class=SAMPLES_PER_CLASS)

    # Get info
    info = generator.get_dataset_info(dataset)

    print("\n" + "=" * 80)
    print("DATASET SUMMARY")
    print("=" * 80)
    print(f"Total samples: {info['total_samples']}")
    print(f"Features: {info['num_features']}")
    print(f"Missing values: {info['missing_values']}")
    print(f"Duplicate rows: {info['duplicate_rows']}")
    print(f"\nClass distribution:")
    for class_name, count in sorted(info['class_distribution'].items()):
        pct = count / info['total_samples'] * 100
        print(f"  {class_name:25s}: {count:5d} ({pct:5.1f}%)")

    # Save dataset
    generator.save_dataset(dataset, OUTPUT_PATH)

    print("\n" + "=" * 80)
    print("Dataset generation complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()

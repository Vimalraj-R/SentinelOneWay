"""
Dataset analysis and preparation for SentinelOneWay ML training.

Performs comprehensive dataset inspection, analysis, and train/test splitting.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from typing import Dict, Tuple


class DatasetAnalyzer:
    """
    Analyze and prepare ML training dataset.

    Provides inspection, visualization, and train/test splitting
    functionality for the network flows dataset.
    """

    def __init__(self, dataset_path: str):
        """
        Initialize analyzer with dataset.

        Args:
            dataset_path: Path to dataset CSV file
        """
        self.dataset_path = dataset_path
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None

    def load_dataset(self):
        """Load dataset from CSV."""
        print(f"Loading dataset from: {self.dataset_path}")
        self.df = pd.read_csv(self.dataset_path)
        print(f"Loaded {len(self.df)} samples with {len(self.df.columns)} columns")
        return self.df

    def inspect_basic_info(self):
        """Print basic dataset information."""
        print("\n" + "=" * 80)
        print("BASIC DATASET INFORMATION")
        print("=" * 80)

        print(f"\nDataset shape: {self.df.shape}")
        print(f"  Rows (samples): {self.df.shape[0]}")
        print(f"  Columns (features + labels): {self.df.shape[1]}")

        print(f"\nMemory usage: {self.df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

        print(f"\nColumn types:")
        print(self.df.dtypes.value_counts())

    def analyze_class_distribution(self):
        """Analyze and visualize class distribution."""
        print("\n" + "=" * 80)
        print("CLASS DISTRIBUTION")
        print("=" * 80)

        # Count by label name
        class_counts = self.df['label_name'].value_counts().sort_index()
        total = len(self.df)

        print("\nSamples per class:")
        for class_name, count in class_counts.items():
            pct = count / total * 100
            print(f"  {class_name:25s}: {count:5d} ({pct:5.1f}%)")

        # Check balance
        max_count = class_counts.max()
        min_count = class_counts.min()
        imbalance_ratio = max_count / min_count

        print(f"\nClass balance:")
        print(f"  Max samples: {max_count}")
        print(f"  Min samples: {min_count}")
        print(f"  Imbalance ratio: {imbalance_ratio:.2f}:1")

        if imbalance_ratio > 3:
            print(f"  WARNING: Dataset is imbalanced (ratio > 3:1)")
            print(f"  Consider using class weights or resampling")
        else:
            print(f"  OK: Dataset is reasonably balanced")

        # Label distribution
        label_counts = self.df['label'].value_counts().sort_index()
        print(f"\nNumeric label distribution:")
        for label, count in label_counts.items():
            print(f"  Label {label}: {count} samples")

    def analyze_missing_values(self):
        """Analyze missing values."""
        print("\n" + "=" * 80)
        print("MISSING VALUES ANALYSIS")
        print("=" * 80)

        missing = self.df.isnull().sum()
        missing_pct = (missing / len(self.df)) * 100

        if missing.sum() == 0:
            print("\nNo missing values found!")
            print("Dataset is complete.")
        else:
            print(f"\nTotal missing values: {missing.sum()}")
            print(f"\nColumns with missing values:")
            for col in missing[missing > 0].index:
                print(f"  {col:30s}: {missing[col]:5d} ({missing_pct[col]:5.2f}%)")

    def analyze_feature_statistics(self):
        """Analyze feature distributions and statistics."""
        print("\n" + "=" * 80)
        print("FEATURE STATISTICS")
        print("=" * 80)

        # Get feature columns (exclude label and label_name)
        feature_cols = [col for col in self.df.columns
                       if col not in ['label', 'label_name']]

        print(f"\nTotal features: {len(feature_cols)}")

        # Basic statistics
        stats = self.df[feature_cols].describe()

        print(f"\nFeature ranges:")
        print(f"  {'Feature':30s} {'Min':>12s} {'Max':>12s} {'Mean':>12s} {'Std':>12s}")
        print(f"  {'-'*30} {'-'*12} {'-'*12} {'-'*12} {'-'*12}")

        for col in feature_cols[:10]:  # Show first 10 features
            min_val = stats.loc['min', col]
            max_val = stats.loc['max', col]
            mean_val = stats.loc['mean', col]
            std_val = stats.loc['std', col]
            print(f"  {col:30s} {min_val:12.2f} {max_val:12.2f} {mean_val:12.2f} {std_val:12.2f}")

        if len(feature_cols) > 10:
            print(f"  ... and {len(feature_cols) - 10} more features")

        # Check for constant features
        constant_features = []
        for col in feature_cols:
            if self.df[col].nunique() == 1:
                constant_features.append(col)

        if constant_features:
            print(f"\nWARNING: {len(constant_features)} constant features found:")
            for col in constant_features:
                print(f"  - {col}")
            print(f"Consider removing these features.")
        else:
            print(f"\nNo constant features found.")

        # Check for high correlation
        print(f"\nChecking for highly correlated features...")
        corr_matrix = self.df[feature_cols].corr().abs()
        upper_triangle = corr_matrix.where(
            np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
        )
        high_corr_pairs = [
            (column, row, corr_matrix.loc[row, column])
            for column in upper_triangle.columns
            for row in upper_triangle.index
            if upper_triangle.loc[row, column] > 0.95
        ]

        if high_corr_pairs:
            print(f"  Found {len(high_corr_pairs)} highly correlated pairs (>0.95):")
            for col1, col2, corr in high_corr_pairs[:5]:  # Show first 5
                print(f"    {col1} <-> {col2}: {corr:.3f}")
            if len(high_corr_pairs) > 5:
                print(f"    ... and {len(high_corr_pairs) - 5} more pairs")
        else:
            print(f"  No highly correlated features found.")

    def analyze_feature_distributions_by_class(self):
        """Analyze key feature distributions by class."""
        print("\n" + "=" * 80)
        print("FEATURE DISTRIBUTIONS BY CLASS")
        print("=" * 80)

        # Key features to analyze
        key_features = [
            'syn_ack_ratio',
            'packets_per_second',
            'dns_entropy',
            'periodicity_score',
            'unique_destination_ports',
            'outbound_inbound_ratio'
        ]

        # Filter to features that exist
        key_features = [f for f in key_features if f in self.df.columns]

        print(f"\nAnalyzing {len(key_features)} key features by class...")

        for feature in key_features:
            print(f"\n{feature}:")
            for class_name in sorted(self.df['label_name'].unique()):
                class_data = self.df[self.df['label_name'] == class_name][feature]
                print(f"  {class_name:25s}: mean={class_data.mean():8.2f}, "
                      f"std={class_data.std():8.2f}, "
                      f"min={class_data.min():8.2f}, "
                      f"max={class_data.max():8.2f}")

    def check_data_quality(self):
        """Check overall data quality."""
        print("\n" + "=" * 80)
        print("DATA QUALITY CHECK")
        print("=" * 80)

        issues = []

        # Check for duplicates
        duplicates = self.df.duplicated().sum()
        if duplicates > 0:
            issues.append(f"{duplicates} duplicate rows")
            print(f"\nWARNING: Found {duplicates} duplicate rows")
        else:
            print(f"\nNo duplicate rows found.")

        # Check for infinite values
        feature_cols = [col for col in self.df.columns
                       if col not in ['label', 'label_name']]
        inf_count = np.isinf(self.df[feature_cols]).sum().sum()
        if inf_count > 0:
            issues.append(f"{inf_count} infinite values")
            print(f"WARNING: Found {inf_count} infinite values")
        else:
            print(f"No infinite values found.")

        # Check for NaN values
        nan_count = self.df[feature_cols].isnull().sum().sum()
        if nan_count > 0:
            issues.append(f"{nan_count} NaN values")
            print(f"WARNING: Found {nan_count} NaN values")
        else:
            print(f"No NaN values found.")

        # Summary
        if issues:
            print(f"\nData quality issues found:")
            for issue in issues:
                print(f"  - {issue}")
            print(f"\nRecommendation: Clean data before training")
        else:
            print(f"\nData quality: EXCELLENT")
            print(f"Dataset is ready for training!")

    def create_train_test_split(self,
                                test_size: float = 0.2,
                                random_state: int = 42,
                                stratify: bool = True):
        """
        Create train/test split.

        Args:
            test_size: Fraction of data for test set
            random_state: Random seed for reproducibility
            stratify: Whether to stratify split by class

        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        print("\n" + "=" * 80)
        print("TRAIN/TEST SPLIT")
        print("=" * 80)

        # Separate features and labels
        feature_cols = [col for col in self.df.columns
                       if col not in ['label', 'label_name']]

        X = self.df[feature_cols]
        y = self.df['label']

        print(f"\nSplitting dataset...")
        print(f"  Test size: {test_size * 100:.0f}%")
        print(f"  Random state: {random_state}")
        print(f"  Stratified: {stratify}")

        # Split
        if stratify:
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                X, y,
                test_size=test_size,
                random_state=random_state,
                stratify=y
            )
        else:
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                X, y,
                test_size=test_size,
                random_state=random_state
            )

        print(f"\nSplit complete:")
        print(f"  Training samples: {len(self.X_train)} ({len(self.X_train)/len(X)*100:.1f}%)")
        print(f"  Test samples: {len(self.X_test)} ({len(self.X_test)/len(X)*100:.1f}%)")

        # Check class distribution in splits
        print(f"\nClass distribution in training set:")
        train_dist = pd.Series(self.y_train).value_counts().sort_index()
        for label, count in train_dist.items():
            class_name = self.df[self.df['label'] == label]['label_name'].iloc[0]
            pct = count / len(self.y_train) * 100
            print(f"  {class_name:25s}: {count:5d} ({pct:5.1f}%)")

        print(f"\nClass distribution in test set:")
        test_dist = pd.Series(self.y_test).value_counts().sort_index()
        for label, count in test_dist.items():
            class_name = self.df[self.df['label'] == label]['label_name'].iloc[0]
            pct = count / len(self.y_test) * 100
            print(f"  {class_name:25s}: {count:5d} ({pct:5.1f}%)")

        return self.X_train, self.X_test, self.y_train, self.y_test

    def save_splits(self, output_dir: str = 'datasets'):
        """
        Save train/test splits to separate files.

        Args:
            output_dir: Directory to save split files
        """
        if self.X_train is None:
            print("Error: Must create train/test split first!")
            return

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Save training set
        train_df = self.X_train.copy()
        train_df['label'] = self.y_train.values
        train_path = Path(output_dir) / 'train.csv'
        train_df.to_csv(train_path, index=False)
        print(f"\nTraining set saved to: {train_path}")

        # Save test set
        test_df = self.X_test.copy()
        test_df['label'] = self.y_test.values
        test_path = Path(output_dir) / 'test.csv'
        test_df.to_csv(test_path, index=False)
        print(f"Test set saved to: {test_path}")

    def run_full_analysis(self):
        """Run complete dataset analysis."""
        self.load_dataset()
        self.inspect_basic_info()
        self.analyze_class_distribution()
        self.analyze_missing_values()
        self.analyze_feature_statistics()
        self.analyze_feature_distributions_by_class()
        self.check_data_quality()
        self.create_train_test_split()
        self.save_splits()


def main():
    """Main analysis script."""
    DATASET_PATH = 'datasets/network_flows.csv'

    print("\n")
    print("=" * 80)
    print(" " * 20 + "SentinelOneWay Dataset Analysis")
    print("=" * 80)

    # Check if dataset exists
    if not Path(DATASET_PATH).exists():
        print(f"\nError: Dataset not found at {DATASET_PATH}")
        print(f"Run 'python ml/dataset_generator.py' first to generate dataset.")
        return

    # Create analyzer
    analyzer = DatasetAnalyzer(DATASET_PATH)

    # Run full analysis
    analyzer.run_full_analysis()

    print("\n" + "=" * 80)
    print("Analysis complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()

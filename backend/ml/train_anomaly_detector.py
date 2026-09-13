"""
Train Isolation Forest for anomaly detection in SentinelOneWay.

Trains unsupervised model primarily on NORMAL traffic to identify
unusual network behavior that deviates from baseline patterns.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
import joblib
import json
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
from typing import Dict, Any


class AnomalyDetectorTrainer:
    """
    Train Isolation Forest for anomaly detection.

    Focuses on learning normal traffic patterns to identify
    anomalous behavior that may indicate unknown threats.
    """

    def __init__(self, random_state: int = 42):
        """
        Initialize trainer.

        Args:
            random_state: Random seed for reproducibility
        """
        self.random_state = random_state
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.metadata = {}

    def load_data(self, dataset_path: str, normal_only: bool = False) -> tuple:
        """
        Load training data.

        Args:
            dataset_path: Path to CSV dataset
            normal_only: If True, only load NORMAL traffic

        Returns:
            Tuple of (X, y, feature_names)
        """
        print(f"Loading dataset from: {dataset_path}")
        df = pd.read_csv(dataset_path)

        print(f"  Total samples: {len(df)}")

        # Filter to normal traffic if requested
        if normal_only:
            df = df[df['label'] == 0]  # NORMAL = 0
            print(f"  Filtered to NORMAL traffic: {len(df)} samples")

        # Identify feature columns (exclude labels and identifiers)
        exclude_cols = ['label', 'label_name']
        identifier_keywords = ['id', 'timestamp', 'ip', 'address', 'flow_id']

        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in identifier_keywords):
                if col not in exclude_cols:
                    exclude_cols.append(col)

        feature_cols = [col for col in df.columns if col not in exclude_cols]

        print(f"  Features: {len(feature_cols)}")

        # Separate features and labels
        X = df[feature_cols]
        y = df['label']

        return X, y, feature_cols

    def prepare_data(self, X: pd.DataFrame,
                    contamination: float = 0.1) -> tuple:
        """
        Prepare data for Isolation Forest training.

        Args:
            X: Feature DataFrame
            contamination: Expected proportion of anomalies

        Returns:
            Tuple of (X_scaled, scaler)
        """
        print(f"\nPreparing data for anomaly detection...")
        print(f"  Contamination rate: {contamination:.1%}")

        # Fit scaler on training data
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        print(f"  Features scaled to zero mean and unit variance")

        return X_scaled

    def train(self, X_scaled: np.ndarray,
             n_estimators: int = 100,
             contamination: float = 0.1,
             max_samples: int = 256) -> None:
        """
        Train Isolation Forest model.

        Args:
            X_scaled: Scaled feature array
            n_estimators: Number of isolation trees
            contamination: Expected proportion of anomalies
            max_samples: Number of samples to draw for each tree
        """
        print(f"\nTraining Isolation Forest...")
        print(f"  Trees: {n_estimators}")
        print(f"  Max samples per tree: {max_samples}")
        print(f"  Contamination: {contamination}")

        self.model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            max_samples=max_samples,
            random_state=self.random_state,
            n_jobs=-1,
            verbose=0
        )

        self.model.fit(X_scaled)

        print(f"  Training complete!")

    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """
        Evaluate anomaly detector.

        Note: Isolation Forest is unsupervised, so evaluation is done
        by checking if it correctly identifies known attack classes as anomalies.

        Args:
            X: Test features
            y: Test labels (0=normal, others=attacks)

        Returns:
            Dictionary of evaluation metrics
        """
        print(f"\nEvaluating anomaly detector...")

        # Scale features
        X_scaled = self.scaler.transform(X)

        # Predict (-1 = anomaly, 1 = normal)
        predictions = self.model.predict(X_scaled)

        # Get anomaly scores (more negative = more anomalous)
        scores = self.model.score_samples(X_scaled)

        # Convert to binary (0=normal, 1=anomaly for sklearn metrics)
        y_pred_binary = (predictions == -1).astype(int)
        y_true_binary = (y != 0).astype(int)  # 0=normal, others=anomaly

        # Calculate metrics
        from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

        accuracy = accuracy_score(y_true_binary, y_pred_binary)
        precision = precision_score(y_true_binary, y_pred_binary, zero_division=0)
        recall = recall_score(y_true_binary, y_pred_binary, zero_division=0)
        f1 = f1_score(y_true_binary, y_pred_binary, zero_division=0)

        print(f"\n  Anomaly Detection Metrics:")
        print(f"    Accuracy:  {accuracy:.4f}")
        print(f"    Precision: {precision:.4f} (% of flagged anomalies that are real attacks)")
        print(f"    Recall:    {recall:.4f} (% of attacks detected)")
        print(f"    F1-score:  {f1:.4f}")

        # Score distribution
        normal_scores = scores[y == 0]
        attack_scores = scores[y != 0]

        print(f"\n  Anomaly Score Distribution:")
        print(f"    Normal traffic:  mean={normal_scores.mean():.4f}, "
              f"std={normal_scores.std():.4f}")
        print(f"    Attack traffic:  mean={attack_scores.mean():.4f}, "
              f"std={attack_scores.std():.4f}")

        # Confusion matrix
        cm = confusion_matrix(y_true_binary, y_pred_binary)
        print(f"\n  Confusion Matrix:")
        print(f"    {'':20s} Predicted Normal  Predicted Anomaly")
        print(f"    {'Actual Normal':20s} {cm[0][0]:16d}  {cm[0][1]:17d}")
        print(f"    {'Actual Attack':20s} {cm[1][0]:16d}  {cm[1][1]:17d}")

        # Per-class detection rates
        print(f"\n  Detection Rates by Threat Class:")
        for label in sorted(y.unique()):
            if label == 0:
                class_name = "NORMAL"
            else:
                class_name = {
                    1: "SYN_FLOOD",
                    2: "PORT_SCAN",
                    3: "C2_BEACON",
                    4: "DNS_TUNNEL",
                    5: "DATA_EXFILTRATION"
                }.get(label, "UNKNOWN")

            class_mask = y == label
            class_predictions = predictions[class_mask]
            anomaly_rate = (class_predictions == -1).sum() / len(class_predictions)

            print(f"    {class_name:25s}: {anomaly_rate:.1%} flagged as anomalous")

        return {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'confusion_matrix': cm.tolist(),
            'normal_score_mean': float(normal_scores.mean()),
            'normal_score_std': float(normal_scores.std()),
            'attack_score_mean': float(attack_scores.mean()),
            'attack_score_std': float(attack_scores.std())
        }

    def save_model(self, model_path: str, scaler_path: str, metadata_path: str):
        """
        Save trained model, scaler, and metadata.

        Args:
            model_path: Path to save model (.pkl)
            scaler_path: Path to save scaler (.pkl)
            metadata_path: Path to save metadata (.json)
        """
        # Create directory
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)

        # Save model
        print(f"\nSaving model to: {model_path}")
        joblib.dump(self.model, model_path)

        # Save scaler
        print(f"Saving scaler to: {scaler_path}")
        joblib.dump(self.scaler, scaler_path)

        # Save metadata
        print(f"Saving metadata to: {metadata_path}")
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)

        print(f"\nModel saved successfully!")
        print(f"  Model size: {Path(model_path).stat().st_size / 1024:.2f} KB")

    def train_and_evaluate(self, dataset_path: str,
                          model_path: str,
                          scaler_path: str,
                          metadata_path: str,
                          train_on_normal_only: bool = True):
        """
        Complete training and evaluation pipeline.

        Args:
            dataset_path: Path to training dataset
            model_path: Path to save model
            scaler_path: Path to save scaler
            metadata_path: Path to save metadata
            train_on_normal_only: If True, train only on normal traffic
        """
        print("=" * 80)
        print("SentinelOneWay Anomaly Detection - Training")
        print("=" * 80)

        # Load data
        X, y, feature_names = self.load_data(dataset_path, normal_only=train_on_normal_only)
        self.feature_names = feature_names

        # Prepare data
        X_scaled = self.prepare_data(X)

        # Train model
        # Use low contamination for normal-only training (expect few outliers)
        # Use higher contamination when training on mixed data
        contamination = 0.001 if train_on_normal_only else 0.15
        self.train(X_scaled, contamination=contamination)

        # Evaluate on full dataset (includes attacks)
        print(f"\nEvaluating on full dataset (including attacks)...")
        X_full, y_full, _ = self.load_data(dataset_path, normal_only=False)
        eval_results = self.evaluate(X_full, y_full)

        # Prepare metadata
        self.metadata = {
            'model_type': 'IsolationForest',
            'training_date': datetime.now().isoformat(),
            'dataset_path': dataset_path,
            'training_samples': len(X),
            'trained_on_normal_only': train_on_normal_only,
            'num_features': len(feature_names),
            'feature_names': feature_names,
            'hyperparameters': {
                'n_estimators': self.model.n_estimators,
                'contamination': self.model.contamination,
                'max_samples': self.model.max_samples,
                'random_state': self.random_state
            },
            'evaluation_metrics': eval_results,
            'usage_notes': [
                'Trained primarily on normal traffic patterns',
                'Identifies deviations from normal behavior',
                'Does not classify specific threat types',
                'Complements supervised classification',
                'Higher anomaly scores indicate greater deviation from normal',
                'Not all anomalies are attacks - investigate before responding'
            ],
            'warnings': [
                'Trained on synthetic data only',
                'May produce false positives on unusual but benign traffic',
                'Requires threshold tuning for production deployment',
                'Should be used in conjunction with supervised classifiers'
            ]
        }

        # Save
        self.save_model(model_path, scaler_path, metadata_path)

        print("\n" + "=" * 80)
        print("Training Complete!")
        print("=" * 80)


def main():
    """Main training script."""
    # Configuration
    DATASET_PATH = 'datasets/network_flows.csv'
    MODEL_PATH = 'models/isolation_forest.pkl'
    SCALER_PATH = 'models/isolation_forest_scaler.pkl'
    METADATA_PATH = 'models/isolation_forest_metadata.json'

    # Check dataset exists
    if not Path(DATASET_PATH).exists():
        print(f"Error: Dataset not found at {DATASET_PATH}")
        return

    # Create and train detector
    trainer = AnomalyDetectorTrainer(random_state=42)
    trainer.train_and_evaluate(
        DATASET_PATH,
        MODEL_PATH,
        SCALER_PATH,
        METADATA_PATH,
        train_on_normal_only=True  # Train only on normal traffic
    )

    print("\nIMPORTANT NOTES:")
    print("-" * 80)
    print("1. This is an UNSUPERVISED anomaly detector")
    print("2. It identifies deviations from normal behavior")
    print("3. Not all anomalies are attacks - requires investigation")
    print("4. Use with supervised classifier for best results")
    print("5. Threshold tuning recommended for production")
    print("-" * 80)


if __name__ == '__main__':
    main()

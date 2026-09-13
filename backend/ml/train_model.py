"""
Train Random Forest classifier for SentinelOneWay threat detection.

Trains a supervised machine learning model to classify network threats
using the generated synthetic dataset.
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
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)
from typing import Dict, Any


class ThreatClassifier:
    """
    Random Forest classifier for network threat detection.

    Trains on synthetic network flow features to classify threats
    across 6 categories.
    """

    def __init__(self, random_state: int = 42):
        """
        Initialize classifier.

        Args:
            random_state: Random seed for reproducibility
        """
        self.random_state = random_state
        self.model = None
        self.feature_names = None
        self.class_names = None
        self.label_mapping = None
        self.metadata = {}

    def load_data(self, dataset_path: str) -> tuple:
        """
        Load and prepare dataset.

        Args:
            dataset_path: Path to CSV dataset

        Returns:
            Tuple of (X, y, feature_names, class_names)
        """
        print(f"Loading dataset from: {dataset_path}")
        df = pd.read_csv(dataset_path)

        print(f"  Loaded {len(df)} samples with {len(df.columns)} columns")

        # Identify feature columns
        # Exclude: label, label_name, and any identifier columns
        exclude_cols = ['label', 'label_name']

        # Additional exclusions for identifiers that shouldn't be features
        identifier_keywords = ['id', 'timestamp', 'ip', 'address', 'flow_id']
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in identifier_keywords):
                if col not in exclude_cols:
                    exclude_cols.append(col)
                    print(f"  Excluding identifier column: {col}")

        # Get feature columns
        feature_cols = [col for col in df.columns if col not in exclude_cols]

        print(f"  Features: {len(feature_cols)}")
        print(f"  Excluded: {len(exclude_cols)}")

        # Separate features and labels
        X = df[feature_cols]
        y = df['label']

        # Get class names
        class_names = {}
        for label in sorted(df['label'].unique()):
            class_name = df[df['label'] == label]['label_name'].iloc[0]
            class_names[int(label)] = class_name

        print(f"\nClass distribution:")
        for label in sorted(df['label'].unique()):
            count = len(df[df['label'] == label])
            pct = count / len(df) * 100
            print(f"  {class_names[label]:25s}: {count:5d} ({pct:5.1f}%)")

        return X, y, feature_cols, class_names

    def create_train_test_split(self, X: pd.DataFrame, y: pd.Series,
                                test_size: float = 0.2) -> tuple:
        """
        Create stratified train/test split.

        Args:
            X: Features
            y: Labels
            test_size: Fraction for test set

        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        print(f"\nCreating train/test split ({int((1-test_size)*100)}/{int(test_size*100)})...")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=self.random_state,
            stratify=y
        )

        print(f"  Training samples: {len(X_train)}")
        print(f"  Test samples: {len(X_test)}")

        return X_train, X_test, y_train, y_test

    def train(self, X_train: pd.DataFrame, y_train: pd.Series,
             n_estimators: int = 100,
             max_depth: int = 20,
             min_samples_split: int = 5,
             min_samples_leaf: int = 2,
             n_jobs: int = -1) -> None:
        """
        Train Random Forest classifier.

        Args:
            X_train: Training features
            y_train: Training labels
            n_estimators: Number of trees
            max_depth: Maximum tree depth
            min_samples_split: Minimum samples to split node
            min_samples_leaf: Minimum samples in leaf
            n_jobs: Number of parallel jobs (-1 for all cores)
        """
        print(f"\nTraining Random Forest classifier...")
        print(f"  Trees: {n_estimators}")
        print(f"  Max depth: {max_depth}")
        print(f"  Min samples split: {min_samples_split}")
        print(f"  Min samples leaf: {min_samples_leaf}")

        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=self.random_state,
            n_jobs=n_jobs,
            verbose=0
        )

        self.model.fit(X_train, y_train)

        print(f"  Training complete!")

    def cross_validate(self, X: pd.DataFrame, y: pd.Series,
                      cv: int = 5) -> Dict[str, float]:
        """
        Perform cross-validation.

        Args:
            X: Features
            y: Labels
            cv: Number of folds

        Returns:
            Dictionary of CV scores
        """
        print(f"\nPerforming {cv}-fold cross-validation...")

        cv_scores = cross_val_score(
            self.model, X, y,
            cv=cv,
            scoring='accuracy',
            n_jobs=-1
        )

        print(f"  CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

        return {
            'cv_accuracy_mean': float(cv_scores.mean()),
            'cv_accuracy_std': float(cv_scores.std()),
            'cv_scores': cv_scores.tolist()
        }

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        """
        Evaluate model on test set.

        Args:
            X_test: Test features
            y_test: Test labels

        Returns:
            Dictionary of evaluation metrics
        """
        print(f"\nEvaluating model on test set...")

        # Predictions
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)

        # Overall metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision_macro = precision_score(y_test, y_pred, average='macro')
        recall_macro = recall_score(y_test, y_pred, average='macro')
        f1_macro = f1_score(y_test, y_pred, average='macro')

        precision_weighted = precision_score(y_test, y_pred, average='weighted')
        recall_weighted = recall_score(y_test, y_pred, average='weighted')
        f1_weighted = f1_score(y_test, y_pred, average='weighted')

        print(f"\n  Overall Metrics:")
        print(f"    Accuracy:           {accuracy:.4f}")
        print(f"    Precision (macro):  {precision_macro:.4f}")
        print(f"    Recall (macro):     {recall_macro:.4f}")
        print(f"    F1-score (macro):   {f1_macro:.4f}")

        # Per-class metrics
        report = classification_report(
            y_test, y_pred,
            target_names=[self.class_names[i] for i in sorted(self.class_names.keys())],
            output_dict=True
        )

        print(f"\n  Per-Class Metrics:")
        for class_name in [self.class_names[i] for i in sorted(self.class_names.keys())]:
            metrics = report[class_name]
            print(f"    {class_name:25s}: "
                  f"P={metrics['precision']:.4f} "
                  f"R={metrics['recall']:.4f} "
                  f"F1={metrics['f1-score']:.4f} "
                  f"(n={int(metrics['support'])})")

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)

        print(f"\n  Confusion Matrix:")
        print(f"    {'':25s} ", end='')
        for i in sorted(self.class_names.keys()):
            print(f"{self.class_names[i][:8]:>8s} ", end='')
        print()

        for i, row in enumerate(cm):
            print(f"    {self.class_names[i]:25s} ", end='')
            for val in row:
                print(f"{val:8d} ", end='')
            print()

        # Average confidence scores
        avg_confidence = []
        for i in range(len(y_test)):
            max_proba = y_pred_proba[i].max()
            avg_confidence.append(max_proba)

        print(f"\n  Average Confidence: {np.mean(avg_confidence):.4f}")

        return {
            'accuracy': float(accuracy),
            'precision_macro': float(precision_macro),
            'recall_macro': float(recall_macro),
            'f1_macro': float(f1_macro),
            'precision_weighted': float(precision_weighted),
            'recall_weighted': float(recall_weighted),
            'f1_weighted': float(f1_weighted),
            'classification_report': report,
            'confusion_matrix': cm.tolist(),
            'avg_confidence': float(np.mean(avg_confidence))
        }

    def get_feature_importance(self, top_n: int = 10) -> pd.DataFrame:
        """
        Get feature importances.

        Args:
            top_n: Number of top features to return

        Returns:
            DataFrame with feature importances
        """
        importances = self.model.feature_importances_
        feature_importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)

        print(f"\n  Top {top_n} Most Important Features:")
        for idx, row in feature_importance_df.head(top_n).iterrows():
            print(f"    {row['feature']:30s}: {row['importance']:.4f}")

        return feature_importance_df

    def save_model(self, model_path: str, metadata_path: str):
        """
        Save trained model and metadata.

        Args:
            model_path: Path to save model (.pkl)
            metadata_path: Path to save metadata (.json)
        """
        # Create directory if needed
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)

        # Save model
        print(f"\nSaving model to: {model_path}")
        joblib.dump(self.model, model_path)

        # Save metadata
        print(f"Saving metadata to: {metadata_path}")
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)

        print(f"\nModel saved successfully!")
        print(f"  Model size: {Path(model_path).stat().st_size / 1024:.2f} KB")

    def train_and_evaluate(self, dataset_path: str,
                          model_path: str,
                          metadata_path: str):
        """
        Complete training and evaluation pipeline.

        Args:
            dataset_path: Path to training dataset
            model_path: Path to save model
            metadata_path: Path to save metadata
        """
        print("=" * 80)
        print("SentinelOneWay Threat Classification - Training")
        print("=" * 80)

        # Load data
        X, y, feature_names, class_names = self.load_data(dataset_path)
        self.feature_names = feature_names
        self.class_names = class_names
        self.label_mapping = class_names

        # Train/test split
        X_train, X_test, y_train, y_test = self.create_train_test_split(X, y)

        # Train model
        self.train(X_train, y_train)

        # Cross-validation
        cv_results = self.cross_validate(X_train, y_train)

        # Evaluate
        eval_results = self.evaluate(X_test, y_test)

        # Feature importance
        feature_importance_df = self.get_feature_importance()

        # Prepare metadata
        self.metadata = {
            'model_type': 'RandomForestClassifier',
            'training_date': datetime.now().isoformat(),
            'dataset_path': dataset_path,
            'total_samples': len(X),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'num_features': len(feature_names),
            'feature_names': feature_names,
            'class_names': class_names,
            'label_mapping': {int(k): v for k, v in class_names.items()},
            'hyperparameters': {
                'n_estimators': self.model.n_estimators,
                'max_depth': self.model.max_depth,
                'min_samples_split': self.model.min_samples_split,
                'min_samples_leaf': self.model.min_samples_leaf,
                'random_state': self.random_state
            },
            'cross_validation': cv_results,
            'test_metrics': eval_results,
            'feature_importance': feature_importance_df.head(20).to_dict('records'),
            'warnings': [
                'Model trained on synthetic data only',
                'Performance on real network traffic may differ',
                'Requires validation on production data before deployment',
                'False positive rate on real traffic unknown'
            ]
        }

        # Save
        self.save_model(model_path, metadata_path)

        print("\n" + "=" * 80)
        print("Training Complete!")
        print("=" * 80)


def main():
    """Main training script."""
    # Configuration
    DATASET_PATH = 'datasets/network_flows.csv'
    MODEL_PATH = 'models/random_forest.pkl'
    METADATA_PATH = 'models/random_forest_metadata.json'

    # Check dataset exists
    if not Path(DATASET_PATH).exists():
        print(f"Error: Dataset not found at {DATASET_PATH}")
        print(f"Run 'python ml/dataset_generator.py' first to generate dataset.")
        return

    # Create and train classifier
    classifier = ThreatClassifier(random_state=42)
    classifier.train_and_evaluate(DATASET_PATH, MODEL_PATH, METADATA_PATH)

    print("\nIMPORTANT NOTE:")
    print("-" * 80)
    print("This model was trained on SYNTHETIC data only.")
    print("Performance on real network traffic may differ significantly.")
    print("Validation on production data is required before deployment.")
    print("False positive rate on real traffic is unknown.")
    print("-" * 80)


if __name__ == '__main__':
    main()

# ML Training Dataset Documentation

## Overview

The SentinelOneWay ML training dataset contains 2,850 labeled network flow samples across 6 threat classes. Each sample represents an aggregated observation with 32 engineered features extracted from synthetic traffic flows.

## Dataset Summary

### Size and Structure

```
Dataset Shape: 2,850 samples × 34 columns
├── Features: 32 numerical columns
├── Label: 1 numeric class label (0-5)
└── Label Name: 1 string class name

File Size: 0.96 MB
Format: CSV
Location: datasets/network_flows.csv
```

### Class Distribution

| Class | Label | Samples | Percentage | Description |
|-------|-------|---------|------------|-------------|
| NORMAL | 0 | 750 | 26.3% | Benign network traffic |
| SYN_FLOOD | 1 | 500 | 17.5% | SYN flood DDoS attacks |
| PORT_SCAN | 2 | 500 | 17.5% | Port scanning reconnaissance |
| C2_BEACON | 3 | 400 | 14.0% | Command & Control beaconing |
| DNS_TUNNEL | 4 | 400 | 14.0% | DNS tunneling covert channel |
| DATA_EXFILTRATION | 5 | 300 | 10.5% | Data exfiltration |

**Class Balance:** 2.50:1 ratio (reasonably balanced, no resampling needed)

## Features (32)

### Single-Flow Features (20)

**Traffic Features (6):**
- `packets_per_second` - Flow packet rate
- `bytes_per_second` - Flow byte rate
- `average_packet_size` - Mean packet size
- `flow_duration` - Flow duration in seconds
- `packet_count` - Total packets
- `byte_count` - Total bytes

**TCP Features (3):**
- `syn_count` - SYN packet count
- `ack_count` - ACK packet count
- `syn_ack_ratio` - SYN/ACK ratio

**DNS Features (5):**
- `dns_query_length` - DNS query length
- `dns_entropy` - Shannon entropy
- `dns_digit_ratio` - Digit percentage
- `dns_unique_char_ratio` - Character diversity
- `dns_subdomain_count` - Subdomain count

**Exfiltration Features (3):**
- `inbound_bytes` - Bytes received
- `outbound_bytes` - Bytes sent
- `outbound_inbound_ratio` - Data flow direction

**Protocol Features (3):**
- `is_tcp` - TCP indicator
- `is_udp` - UDP indicator
- `is_icmp` - ICMP indicator

### Aggregate Features (12)

**Reconnaissance Features (4):**
- `unique_destination_ports` - Unique ports contacted
- `unique_destination_hosts` - Unique hosts contacted
- `connection_rate` - Connections per second
- `fanout_score` - Destinations per source

**DDoS Features (4):**
- `source_ip_count` - Unique source IPs
- `source_ip_entropy` - Source diversity
- `destination_concentration` - Target concentration
- `aggregate_packet_rate` - Total packet rate

**C2 Beaconing Features (4):**
- `mean_inter_arrival_time` - Mean time between flows
- `inter_arrival_std` - Timing variance
- `periodicity_score` - Regularity measure
- `repeated_destination_count` - Max repeated destination

## Feature Characteristics by Class

### Key Discriminating Features

**SYN_FLOOD vs Others:**
- `syn_ack_ratio`: 68.43 (SYN_FLOOD) vs 0.00-1.00 (others)
- `packets_per_second`: 1024.47 (SYN_FLOOD) vs 9.06-329.49 (others)

**PORT_SCAN vs Others:**
- `unique_destination_ports`: 125.62 (PORT_SCAN) vs 1.00-2.99 (others)
- `connection_rate`: ~100/s (PORT_SCAN) vs much lower (others)

**C2_BEACON vs Others:**
- `periodicity_score`: 0.87 (C2_BEACON) vs 0.51-0.72 (others)
- `mean_inter_arrival_time`: Regular intervals (C2_BEACON)

**DNS_TUNNEL vs Others:**
- `dns_entropy`: 4.72 (DNS_TUNNEL) vs 0.00-0.95 (others)
- `dns_query_length`: High (DNS_TUNNEL) vs 0 or low (others)

**DATA_EXFILTRATION vs Others:**
- `outbound_inbound_ratio`: 2791.37 (DATA_EXFILTRATION) vs 0.10-47.07 (others)
- `byte_count`: Very high (DATA_EXFILTRATION)

## Data Quality

### Completeness
✓ **No missing values** (0 NaN values)  
✓ **No infinite values** (0 Inf values)  
✓ **No duplicate rows** (0 duplicates)  

### Quality Score: **EXCELLENT**

### Feature Correlations

Found 9 highly correlated feature pairs (>0.95):
- `byte_count` ↔ `packet_count`: 1.000 (perfect correlation)
- `syn_ack_ratio` ↔ `syn_count`: 0.993
- `dns_entropy` ↔ `dns_query_length`: 0.972
- `dns_digit_ratio` ↔ `dns_query_length`: 0.991
- `dns_subdomain_count` ↔ `dns_entropy`: 0.987

**Recommendation:** Consider feature selection or PCA to remove redundancy.

## Train/Test Split

### Split Configuration
- **Test Size:** 20% (570 samples)
- **Training Size:** 80% (2,280 samples)
- **Stratification:** Yes (maintains class distribution)
- **Random Seed:** 42 (reproducible)

### Files Generated
- `datasets/train.csv` - Training set (754 KB)
- `datasets/test.csv` - Test set (190 KB)

### Class Distribution Maintained

| Class | Train | Test | Train % | Test % |
|-------|-------|------|---------|--------|
| NORMAL | 600 | 150 | 26.3% | 26.3% |
| SYN_FLOOD | 400 | 100 | 17.5% | 17.5% |
| PORT_SCAN | 400 | 100 | 17.5% | 17.5% |
| C2_BEACON | 320 | 80 | 14.0% | 14.0% |
| DNS_TUNNEL | 320 | 80 | 14.0% | 14.0% |
| DATA_EXFILTRATION | 240 | 60 | 10.5% | 10.5% |

✓ **Perfect stratification** - distributions match exactly

## Generation Process

### Pipeline

```
Traffic Generator → Flow Records → Feature Extraction → Labeled Dataset
                       ↓                  ↓                    ↓
                 (Varied params)   (32 features)      (2850 samples)
```

### Randomization Strategy

To avoid overfitting, each sample is generated with randomized parameters:

1. **Intensity Variation:** 0.3-1.0 range per scenario
2. **Flow Count Variation:** 5-200 flows per sample (scenario-dependent)
3. **Random Sampling:** Random subset of flows when count exceeds target
4. **Seed Control:** Random seed 42 for reproducibility

### Generation Parameters

| Scenario | Samples | Intensity Range | Flows/Sample |
|----------|---------|-----------------|--------------|
| NORMAL | 750 | 0.2-0.8 | 5-20 |
| SYN_FLOOD | 500 | 0.4-1.0 | 20-80 |
| PORT_SCAN | 500 | 0.3-1.0 | 50-200 |
| C2_BEACON | 400 | 0.3-0.9 | 5-20 |
| DNS_TUNNEL | 400 | 0.3-1.0 | 10-50 |
| DATA_EXFILTRATION | 300 | 0.3-1.0 | 2-10 |

## Usage

### Loading Dataset

```python
import pandas as pd

# Load full dataset
df = pd.read_csv('datasets/network_flows.csv')

# Separate features and labels
X = df.drop(['label', 'label_name'], axis=1)
y = df['label']

# Or load pre-split data
train_df = pd.read_csv('datasets/train.csv')
test_df = pd.read_csv('datasets/test.csv')
```

### Regenerating Dataset

```python
from ml.dataset_generator import DatasetGenerator

# Create generator with seed for reproducibility
generator = DatasetGenerator(random_seed=42)

# Generate dataset
dataset = generator.generate_dataset(samples_per_class=500)

# Save
generator.save_dataset(dataset, 'datasets/network_flows.csv')
```

### Custom Generation

```python
# Generate with custom class weights
dataset = generator.generate_dataset(
    samples_per_class=1000,
    class_weights={
        'normal': 2.0,  # 2x normal samples
        'syn_flood': 1.0,
        'port_scan': 1.0,
        'c2_beacon': 0.5,
        'dns_tunnel': 0.5,
        'data_exfiltration': 0.3
    }
)
```

### Analysis

```python
from ml.analyze_dataset import DatasetAnalyzer

# Create analyzer
analyzer = DatasetAnalyzer('datasets/network_flows.csv')

# Run full analysis
analyzer.run_full_analysis()

# Or step-by-step
analyzer.load_dataset()
analyzer.inspect_basic_info()
analyzer.analyze_class_distribution()
analyzer.check_data_quality()
```

## Next Steps for ML Training

### 1. Feature Engineering
- [ ] Consider removing highly correlated features
- [ ] Feature scaling/normalization
- [ ] Feature selection based on importance
- [ ] PCA for dimensionality reduction (optional)

### 2. Model Selection
- [ ] Binary classifier (benign vs malicious)
- [ ] Multi-class classifier (6-class)
- [ ] Ensemble methods (Random Forest, XGBoost)
- [ ] Neural networks (optional)

### 3. Training Strategy
- [ ] Cross-validation (5-fold recommended)
- [ ] Hyperparameter tuning
- [ ] Class weight adjustment (if needed)
- [ ] Early stopping

### 4. Evaluation Metrics
- [ ] Accuracy (overall)
- [ ] Precision, Recall, F1-score (per class)
- [ ] Confusion matrix
- [ ] ROC-AUC (one-vs-rest)
- [ ] False positive rate (critical for security)

### 5. Integration
- [ ] Save trained model
- [ ] Create prediction pipeline
- [ ] Integrate with baseline detectors
- [ ] API endpoints for inference

## Label Encoding

```python
CLASS_MAPPING = {
    0: 'NORMAL',
    1: 'SYN_FLOOD',
    2: 'PORT_SCAN',
    3: 'C2_BEACON',
    4: 'DNS_TUNNEL',
    5: 'DATA_EXFILTRATION'
}
```

## Performance Expectations

Based on feature analysis, expected model performance:

- **Easy Classes** (distinct features):
  - SYN_FLOOD: ~95-99% (unique syn_ack_ratio)
  - PORT_SCAN: ~95-99% (unique port count)
  - DNS_TUNNEL: ~90-95% (unique dns_entropy)
  - DATA_EXFILTRATION: ~85-95% (unique outbound ratio)

- **Moderate Classes** (overlapping features):
  - C2_BEACON: ~80-90% (periodicity overlap with normal)
  - NORMAL: ~85-90% (diverse patterns)

**Overall Expected Accuracy:** 90-95%

## Reproducibility

All dataset generation is reproducible with `random_seed=42`:
- Same traffic patterns
- Same feature values
- Same train/test split

To regenerate exact dataset:
```bash
python ml/dataset_generator.py
```

## References

- Generator: `ml/dataset_generator.py`
- Analyzer: `ml/analyze_dataset.py`
- Feature Extractor: `features/extractor.py`
- Traffic Simulator: `simulator/traffic_generator.py`

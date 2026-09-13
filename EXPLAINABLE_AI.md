# Explainable AI for Threat Classification

## Overview

SentinelOneWay includes **explainable AI** capabilities using SHAP (SHapley Additive exPlanations) to help SOC analysts understand **why** an alert was classified as malicious.

Every threat classification now comes with:
1. **Human-readable explanations** - Clear, actionable insights
2. **Technical AI evidence** - Feature importance scores
3. **Classification confidence** - ML model certainty
4. **Class probabilities** - Alternative threat classifications

## Architecture

```
Alert → Features → Random Forest → Prediction
                         ↓
                   SHAP Explainer
                         ↓
              ┌──────────┴──────────┐
              ↓                     ↓
    Technical Evidence      Human Explanation
    (feature importance)    (SOC analyst view)
```

## Components

### Backend

**1. Explainer Service** (`ml/explainer.py`)

- `ThreatExplainer` class wraps the Random Forest model
- Uses SHAP TreeExplainer for fast feature attribution
- Falls back to model's feature importances if SHAP unavailable
- Generates both technical and human-readable explanations
- Singleton pattern for efficiency

**2. Explanations API** (`api/explanations.py`)

- `GET /api/explanations/alert/{alert_id}` - Explain specific alert
- `POST /api/explanations/explain` - Explain arbitrary features
- `GET /api/explanations/cache/stats` - Cache statistics
- `POST /api/explanations/cache/clear` - Clear cache
- LRU cache (100 most recent) for performance

**3. Alert Service Updates** (`services/alert_service.py`)

- Stores features with alerts for later explanation
- Features saved in `evidence_json` field

### Frontend

**Component:** `components/alert/ExplainableAI.jsx`

Displays on Alert Details page:

**Section 1: Why SentinelOneWay Detected This**
- Human-readable detection reasoning
- Numbered explanations (1, 2, 3...)
- Clear, non-technical language

**Section 2: Classification Probabilities**
- All 6 threat classes with probabilities
- Visual bars showing confidence
- Color-coded (red/yellow/green)

**Section 3: Technical AI Evidence** (expandable)
- Feature importance table
- Feature values
- Impact indicators
- Sorted by importance

## Installation

### SHAP Library (Optional but Recommended)

```bash
cd backend
source venv/Scripts/activate  # Windows Git Bash
pip install shap
```

SHAP provides more accurate feature attributions. Without it, the system falls back to model's built-in feature importances (still useful but less precise).

## Usage

### Backend API

**Explain Alert:**
```python
from ml.explainer import get_explainer

explainer = get_explainer()
explanation = explainer.explain_prediction(features, top_n=10)

# Returns:
{
  "predicted_class": "SYN_FLOOD",
  "confidence": 0.95,
  "technical_explanation": [
    {
      "feature": "syn_ack_ratio",
      "value": 75.0,
      "importance": 0.31,
      "impact": "positive"
    },
    ...
  ],
  "human_explanation": [
    "SYN/ACK ratio is extremely high (75.0), indicating incomplete TCP handshakes typical of SYN floods.",
    "Very high number of SYN packets (1500), characteristic of flood attacks.",
    ...
  ],
  "all_class_probabilities": {
    "NORMAL": 0.02,
    "SYN_FLOOD": 0.95,
    "PORT_SCAN": 0.02,
    ...
  }
}
```

**API Endpoint:**
```bash
# Explain specific alert
curl http://localhost:8000/api/explanations/alert/123

# Explain arbitrary features
curl -X POST http://localhost:8000/api/explanations/explain \
  -H "Content-Type: application/json" \
  -d '{
    "packets_per_second": 1500.0,
    "syn_ack_ratio": 75.0,
    "average_packet_size": 60.0
  }'
```

### Frontend Usage

The ExplainableAI component automatically loads when viewing an alert:

```jsx
import ExplainableAI from '../components/alert/ExplainableAI';

<ExplainableAI alertId={alert.id} />
```

Features:
- Auto-fetches explanation from API
- Shows loading spinner while generating
- Handles errors gracefully
- Expandable technical section
- No SHAP internals exposed to UI

## Feature Explanations

The system provides human-readable explanations for key features:

### Traffic Features

- **packets_per_second** - "Packet rate is very high at 1500 packets/sec"
- **bytes_per_second** - "Data transfer rate is extremely high at 500 KB/sec"
- **average_packet_size** - "Packets are unusually small (60 bytes), typical of scanning"

### TCP Features

- **syn_ack_ratio** - "SYN/ACK ratio is extremely high (75.0), indicating incomplete TCP handshakes"
- **syn_count** - "Very high number of SYN packets (1500), characteristic of flood attacks"

### Reconnaissance Features

- **unique_destination_ports** - "Scanning 150 different ports suggests systematic reconnaissance"
- **connection_rate** - "Very high connection rate (75/sec) typical of automated scanning"

### DDoS Features

- **unique_source_ips** - "Traffic originates from 45 different sources, suggesting distributed attack"
- **source_ip_entropy** - "High source IP diversity (entropy: 5.2) indicates distributed botnet"

### C2 Features

- **periodicity_score** - "Traffic shows highly periodic behavior (score: 0.92), characteristic of automated C2 beaconing"
- **flow_regularity** - "Connection timing is suspiciously regular (score: 0.85)"

### DNS Features

- **dns_entropy** - "DNS query entropy is very high (4.5), suggesting randomized subdomain generation"
- **dns_query_length** - "DNS queries are unusually long (80 characters), typical of data exfiltration"

### Exfiltration Features

- **outbound_inbound_ratio** - "Outbound traffic is 8.5x higher than inbound, suggesting data exfiltration"
- **outbound_bytes** - "Large amount of outbound data (5.2 MB) to external destination"

## Performance Optimization

### Caching Strategy

**LRU Cache (100 entries):**
```python
@lru_cache(maxsize=100)
def _cached_explanation(features_json: str, top_n: int) -> str:
    # Cache key: JSON-serialized features
    # Cache hit: ~1ms
    # Cache miss: ~50-200ms (SHAP computation)
```

**Cache Statistics:**
```bash
curl http://localhost:8000/api/explanations/cache/stats

{
  "cache_size": 45,
  "max_size": 100,
  "hits": 234,
  "misses": 45,
  "hit_rate": 0.838
}
```

### Performance Benchmarks

**With SHAP:**
- First explanation: ~200ms (explainer creation)
- Cached explanation: ~1ms
- Uncached explanation: ~50ms

**Without SHAP (fallback):**
- First explanation: ~50ms (model loading)
- Cached explanation: ~1ms
- Uncached explanation: ~10ms

### Cost Analysis

**Computation cost per alert:**
- Feature extraction: ~5ms
- Classification: ~2ms
- Explanation (cached): ~1ms
- Explanation (uncached): ~50ms
- **Total (typical): ~8ms**

Caching reduces explanation overhead by **98%** for repeated queries.

## Limitations

### Current Limitations

1. **Synthetic Data Training**
   - Model trained on synthetic traffic
   - Explanations reflect synthetic patterns
   - May not perfectly match real-world attacks

2. **Feature Coverage**
   - Not all features have human explanations
   - Falls back to feature name if no template

3. **SHAP Availability**
   - Optional dependency
   - Falls back to feature importances without it
   - Less precise attributions

4. **Context-Limited**
   - Explains single prediction
   - Doesn't compare to historical baseline
   - No cross-alert pattern analysis

### Known Issues

1. **Missing Features**
   - If alert doesn't store features, explanation fails
   - Solution: Ensure features stored with all new alerts

2. **Low Confidence**
   - Partial features yield lower confidence
   - Solution: Provide all 30 features to model

3. **Cache Invalidation**
   - Cache not cleared on model retraining
   - Solution: Manual clear via API after retraining

## Example Explanation

### SYN Flood Detection

**Input Features:**
```json
{
  "packets_per_second": 1500.0,
  "bytes_per_second": 90000.0,
  "average_packet_size": 60.0,
  "syn_ack_ratio": 75.0,
  "syn_count": 1500.0,
  "unique_source_ips": 45.0,
  "source_ip_entropy": 5.2
}
```

**Human Explanation:**
1. This traffic pattern is consistent with a SYN flood DDoS attack.
2. SYN/ACK ratio is extremely high (75.0), indicating incomplete TCP handshakes typical of SYN floods.
3. Very high number of SYN packets (1500), characteristic of flood attacks.
4. Packets are unusually small (60 bytes), typical of scanning.
5. Traffic originates from 45 different sources, suggesting distributed attack.

**Technical Evidence:**
| Feature | Value | Importance |
|---------|-------|------------|
| syn_ack_ratio | 75.00 | 31.2% |
| packets_per_second | 1500.00 | 18.5% |
| syn_count | 1500.00 | 15.3% |
| unique_source_ips | 45.00 | 12.1% |
| source_ip_entropy | 5.20 | 8.7% |

**Classification:**
- SYN_FLOOD: 95%
- PORT_SCAN: 3%
- NORMAL: 1%
- Others: 1%

## Integration with Detection Pipeline

```python
from detection.hybrid_engine import get_hybrid_engine
from services.alert_service import AlertService
from features.extractor import FlowFeatureExtractor

# Extract features
extractor = FlowFeatureExtractor()
features = extractor.extract_single(flow)

# Run detection
engine = get_hybrid_engine()
result = engine.detect(features)

# Create alert with features (for explanation)
if result.threat_class != "NORMAL":
    alert = await AlertService.create_alert_with_broadcast(
        db=db,
        detection_result=result.to_dict(),
        flow_data={...},
        features=features  # ← Store for explanation
    )
```

## Testing

### Backend Test

```bash
cd backend
source venv/Scripts/activate
python ml/explainer.py
```

Expected output:
```
Prediction: SYN_FLOOD
Confidence: 95%

Human Explanation:
1. This traffic pattern is consistent with a SYN flood DDoS attack.
2. SYN/ACK ratio is extremely high (75.0)...

Technical Evidence:
Feature                    Value    Importance
syn_ack_ratio             75.00         31.2%
packets_per_second      1500.00         18.5%
...
```

### API Test

```bash
# Create test alert with features
curl -X POST http://localhost:8000/api/test/simulate-alert

# Get alert ID from response, then explain
curl http://localhost:8000/api/explanations/alert/1
```

### Frontend Test

1. Navigate to http://localhost:5173
2. View any alert details
3. Scroll to "Why SentinelOneWay Detected This"
4. Expand "Technical AI Evidence"

## Future Enhancements

### Short Term

- [ ] Add SHAP waterfall plots
- [ ] Compare current vs. baseline behavior
- [ ] Explain changes in classification over time
- [ ] Add confidence intervals

### Medium Term

- [ ] Multi-alert pattern explanation
- [ ] Cross-feature interaction analysis
- [ ] Counterfactual explanations ("What if...")
- [ ] Anchor explanations (rule-based)

### Long Term

- [ ] Natural language query interface
- [ ] Automated recommendation generation
- [ ] Integration with SIEM platforms
- [ ] Custom explanation templates per organization

## Best Practices

### For SOC Analysts

1. **Read human explanations first** - Technical evidence is secondary
2. **Check confidence score** - Higher confidence = more reliable
3. **Review class probabilities** - Alternative classifications matter
4. **Expand technical evidence** - When human explanation unclear
5. **Consider alert context** - One alert may not tell full story

### For Developers

1. **Always store features** - Required for explanation
2. **Cache explanations** - Expensive to recompute
3. **Handle missing features** - Default to 0.0 gracefully
4. **Test with real data** - Synthetic data limitations
5. **Clear cache after retraining** - Avoid stale explanations

## Troubleshooting

### "Unable to generate explanation"

**Cause:** Alert doesn't contain stored features

**Solution:**
- Ensure `features` parameter passed to `create_alert_with_broadcast()`
- Check alert's `evidence_json` contains `features` field
- Re-create alert with proper feature storage

### Low or incorrect confidence

**Cause:** Missing or incomplete features

**Solution:**
- Provide all 30 features required by model
- Check feature extraction is working correctly
- Verify feature values are realistic

### Explanation doesn't match detection

**Cause:** Different features used for detection vs. explanation

**Solution:**
- Store exact features used for detection
- Verify feature dictionary passed correctly
- Check for feature name mismatches

### Cache showing stale explanations

**Cause:** Cache not cleared after model retraining

**Solution:**
```bash
curl -X POST http://localhost:8000/api/explanations/cache/clear
```

## References

- **SHAP:** https://github.com/slundberg/shap
- **Paper:** "A Unified Approach to Interpreting Model Predictions" (Lundberg & Lee, 2017)
- **TreeExplainer:** Fast exact SHAP values for tree-based models

---

**Status:** Explainable AI implemented with SHAP support, LRU caching, and comprehensive frontend integration. Ready for production use with proper feature storage.

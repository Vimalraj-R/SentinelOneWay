# SentinelOneWay Backend API

FastAPI-based backend for passive network threat detection and monitoring.

## 🏗️ Architecture

The backend follows a clean, modular architecture:

```
backend/
├── api/                    # API route handlers
│   ├── alerts.py          # Alert endpoints
│   ├── metrics.py         # Network metric endpoints
│   ├── assets.py          # Asset endpoints
│   └── dashboard.py       # Dashboard summary endpoint
│
├── database/              # Database layer
│   ├── base.py           # SQLAlchemy configuration
│   └── models.py         # Database models
│
├── schemas/               # Pydantic schemas (request/response)
│   ├── alert.py          # Alert schemas
│   ├── metric.py         # Metric schemas
│   ├── asset.py          # Asset schemas
│   └── dashboard.py      # Dashboard schemas
│
├── services/              # Business logic layer
│   ├── alert_service.py  # Alert operations
│   ├── metric_service.py # Metric operations
│   └── asset_service.py  # Asset operations
│
├── utils/                 # Utility scripts
│   └── seed_data.py      # Database seeding
│
├── main.py                # FastAPI application
└── sentineloneway.db     # SQLite database (generated)
```

---

## 📊 Database Models

### 1. Alert
Stores detected security threats.

**Fields:**
- `id` - Primary key
- `timestamp` - When threat was detected
- `flow_id` - Unique flow identifier
- `threat_class` - Type of threat (SYN Flood, Port Scan, etc.)
- `severity` - Critical, High, Medium, Low
- `confidence` - Detection confidence (0.0 to 1.0)
- `risk_score` - Overall risk (0 to 100)
- `src_ip` - Source IP address
- `dst_ip` - Destination IP address
- `src_port` - Source port
- `dst_port` - Destination port
- `protocol` - Network protocol
- `status` - Active, Investigating, Acknowledged, Resolved, Blocked
- `evidence_json` - JSON string with detection evidence
- `created_at`, `updated_at` - Timestamps

### 2. NetworkMetric
Stores aggregate network traffic statistics.

**Fields:**
- `id` - Primary key
- `timestamp` - Measurement timestamp
- `flows_per_second` - Flow rate
- `packets_per_second` - Packet rate
- `bytes_per_second` - Byte rate
- `tcp_percentage` - TCP traffic percentage
- `udp_percentage` - UDP traffic percentage
- `dns_percentage` - DNS traffic percentage
- `created_at` - Timestamp

### 3. Asset
Network asset inventory.

**Fields:**
- `id` - Primary key
- `ip_address` - IP address (unique)
- `hostname` - Host name
- `asset_type` - server, workstation, network_device
- `criticality` - Critical, High, Medium, Low
- `risk_score` - Current risk (0 to 100)
- `created_at`, `updated_at` - Timestamps

---

## 🚀 API Endpoints

### Alerts

#### `GET /api/alerts`
List alerts with optional filtering and pagination.

**Query Parameters:**
- `skip` (int, default: 0) - Records to skip
- `limit` (int, default: 100, max: 1000) - Max records to return
- `severity` (string, optional) - Filter by severity
- `status` (string, optional) - Filter by status

**Response:**
```json
{
  "total": 8,
  "alerts": [...]
}
```

#### `GET /api/alerts/{alert_id}`
Get a specific alert by ID.

**Response:** Single alert object

#### `POST /api/alerts`
Create a new alert (used by detection engine).

**Request Body:** AlertCreate schema

**Response:** Created alert object

#### `PATCH /api/alerts/{alert_id}/status`
Update alert status (analyst action).

**Request Body:**
```json
{
  "status": "Investigating"
}
```

**Response:** Updated alert object

---

### Metrics

#### `GET /api/metrics/current`
Get the most recent network metrics.

**Response:**
```json
{
  "id": 24,
  "timestamp": "2026-09-13T13:30:21",
  "flows_per_second": 2188.21,
  "packets_per_second": 26258.60,
  "bytes_per_second": 4381432.36,
  "tcp_percentage": 71.23,
  "udp_percentage": 19.45,
  "dns_percentage": 6.82,
  "created_at": "2026-09-13T13:30:21"
}
```

#### `GET /api/metrics/history`
Get historical network metrics.

**Query Parameters:**
- `hours` (int, default: 24, max: 168) - Hours of history
- `limit` (int, default: 100, max: 1000) - Max records

**Response:**
```json
{
  "total": 24,
  "metrics": [...]
}
```

---

### Assets

#### `GET /api/assets`
List all monitored assets.

**Query Parameters:**
- `skip` (int, default: 0) - Records to skip
- `limit` (int, default: 100, max: 1000) - Max records

**Response:**
```json
{
  "total": 8,
  "assets": [...]
}
```

#### `GET /api/assets/{asset_id}`
Get a specific asset by ID.

**Response:** Single asset object

---

### Dashboard

#### `GET /api/dashboard/summary`
Get comprehensive dashboard summary data.

**Response:**
```json
{
  "risk_score": 76,
  "active_alerts": 3,
  "critical_threats": 2,
  "current_flow_rate": 2188.22,
  "alerts_by_severity": {
    "Critical": 3,
    "High": 3,
    "Medium": 2
  },
  "alerts_by_status": {
    "Active": 3,
    "Investigating": 1,
    "Resolved": 2
  },
  "top_threatened_assets": [...],
  "recent_alerts": [...]
}
```

---

## 🔧 Setup & Installation

### 1. Install Dependencies

```bash
cd backend

# Activate virtual environment
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

# Install packages
pip install -r requirements.txt
```

### 2. Seed Database

```bash
python utils/seed_data.py
```

This creates `sentineloneway.db` with:
- 8 assets
- 8 sample alerts
- 24 hours of network metrics

### 3. Start Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Server will be available at:**
- API: `http://localhost:8000`
- Interactive Docs: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

---

## 🧪 Testing Endpoints

### Using curl:

```bash
# Health check
curl http://localhost:8000/health

# Get all alerts
curl http://localhost:8000/api/alerts

# Get specific alert
curl http://localhost:8000/api/alerts/1

# Get dashboard summary
curl http://localhost:8000/api/dashboard/summary

# Update alert status
curl -X PATCH http://localhost:8000/api/alerts/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "Investigating"}'

# Get current metrics
curl http://localhost:8000/api/metrics/current

# Get assets
curl http://localhost:8000/api/assets
```

### Using Browser:

Open `http://localhost:8000/docs` for interactive API documentation with Swagger UI.

---

## 🔌 CORS Configuration

CORS is configured to allow requests from:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:5174`
- `http://localhost:3000` (Create React App)
- `http://127.0.0.1:5173`
- `http://127.0.0.1:5174`
- `http://127.0.0.1:3000`

All HTTP methods and headers are allowed for development.

---

## 📦 Dependencies

See `requirements.txt` for full list. Key packages:

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **sqlalchemy** - ORM
- **pydantic** - Data validation
- **python-multipart** - File uploads

ML packages (not yet implemented):
- **pandas** - Data manipulation
- **numpy** - Numerical operations
- **scikit-learn** - Machine learning
- **joblib** - Model persistence

---

## 🧪 Traffic Simulation

SentinelOneWay includes a built-in traffic simulator for testing detection algorithms.

**IMPORTANT**: This simulator generates **synthetic flow-level metadata only** - no real network packets are sent. It's designed exclusively for defensive cybersecurity development and testing.

### Simulation Scenarios

| Scenario | Description | Key Characteristics |
|----------|-------------|---------------------|
| `normal` | Benign traffic | Balanced ratios, varied destinations |
| `syn_flood` | DDoS attack | High SYN count, few ACKs, single target |
| `port_scan` | Reconnaissance | Single source, many ports, short flows |
| `c2_beacon` | Command & Control | Regular intervals, consistent payloads |
| `dns_tunnel` | Covert channel | High-entropy DNS queries |
| `data_exfiltration` | Data theft | High outbound/inbound ratio |

### Simulation API Endpoints

```bash
# Start simulation
curl -X POST http://localhost:8000/api/simulation/start \
  -H "Content-Type: application/json" \
  -d '{"scenario": "syn_flood", "intensity": 0.8}'

# Check status
curl -X GET http://localhost:8000/api/simulation/status

# Get generated flows
curl -X GET "http://localhost:8000/api/simulation/flows?limit=10"

# Stop simulation
curl -X POST http://localhost:8000/api/simulation/stop

# Clear flows from memory
curl -X DELETE http://localhost:8000/api/simulation/flows
```

**Intensity Values:**
- `0.0` - Minimal traffic generation
- `0.5` - Moderate traffic (default)
- `1.0` - Maximum traffic generation

### Testing the Simulator

Run the test script:

```bash
cd backend
python test_simulation.py
```

### Using Flows for Detection

```python
from simulator.simulation_manager import simulation_manager

# Set callback to process flows in real-time
def process_flow(flow_record):
    # Your detection logic here
    if flow_record.get_syn_ack_ratio() > 10:
        print(f"Potential SYN flood detected: {flow_record.flow_id}")

simulation_manager.set_flow_callback(process_flow)

# Start simulation
simulation_manager.start("syn_flood", intensity=0.8)
```

---

## 🎯 Feature Engineering

SentinelOneWay includes a comprehensive feature extraction system that converts raw network flows into ML-ready numerical features.

### Feature Categories

#### 1. Traffic Features
- `packets_per_second` - Flow packet rate
- `bytes_per_second` - Flow byte rate
- `average_packet_size` - Mean packet size
- `flow_duration` - Flow duration in seconds
- `packet_count` - Total packets
- `byte_count` - Total bytes

#### 2. TCP Features
- `syn_count` - Number of SYN packets
- `ack_count` - Number of ACK packets
- `syn_ack_ratio` - SYN/ACK ratio (high = potential SYN flood)

#### 3. DNS Features
- `dns_query_length` - Length of DNS query
- `dns_entropy` - Shannon entropy (high = potential tunneling)
- `dns_digit_ratio` - Ratio of digits in query
- `dns_unique_char_ratio` - Character diversity
- `dns_subdomain_count` - Number of subdomains

#### 4. Exfiltration Features
- `inbound_bytes` - Bytes received
- `outbound_bytes` - Bytes sent
- `outbound_inbound_ratio` - Data flow direction (high = potential exfiltration)

#### 5. Protocol Features
- `is_tcp`, `is_udp`, `is_icmp` - Protocol indicators

#### 6. Aggregate Features (Multi-Flow)
- **Reconnaissance:** `unique_destination_ports`, `unique_destination_hosts`, `fanout_score`
- **DDoS:** `source_ip_count`, `source_ip_entropy`, `destination_concentration`
- **C2 Beaconing:** `mean_inter_arrival_time`, `periodicity_score`, `repeated_destination_count`

### Using the Feature Extractor

```python
from features.extractor import FlowFeatureExtractor
from simulator.traffic_generator import TrafficGenerator

extractor = FlowFeatureExtractor()
generator = TrafficGenerator()

# Extract features from single flow
flows = generator.generate_traffic('syn_flood', intensity=0.8)
features = extractor.extract_single(flows[0])
print(f"SYN/ACK Ratio: {features['syn_ack_ratio']}")

# Extract features from batch of flows
df = extractor.extract_batch(flows)
print(df.head())

# Extract aggregate features (multi-flow patterns)
aggregate = extractor.extract_aggregate(flows)
print(f"Source IP Entropy: {aggregate['source_ip_entropy']}")
```

### Running the Demo

```bash
cd backend
python demo_features.py
```

The demo shows:
1. Single flow feature extraction
2. Batch processing
3. Aggregate pattern detection
4. Threat-specific indicators
5. ML pipeline preparation

---

## 🛡️ Baseline Threat Detection

SentinelOneWay includes rule-based detectors that provide explainable threat detection before ML models.

### Detectors

| Detector | Primary Indicators | Configurable Thresholds |
|----------|-------------------|------------------------|
| **SYN Flood** | High SYN/ACK ratio, high packet rate, small packets | syn_ack_ratio, packet_rate, source_entropy |
| **Port Scan** | Many unique ports, high fanout, short flows | unique_ports, connection_rate, flow_duration |
| **C2 Beacon** | High periodicity, low timing variance, repeated destination | periodicity_score, timing_variance, intervals |

### Detection Structure

All detectors return structured results:

```python
{
  "threat_class": "SYN Flood",
  "confidence": 0.95,
  "severity": "Critical",
  "evidence": {
    "syn_ack_ratio": 69.8,
    "packet_rate": 1024.4,
    "source_ip_entropy": 6.32
  },
  "human_explanation": [
    "Detected SYN flood attack with 5 indicators...",
    "Extremely high SYN/ACK ratio (69.8) indicates...",
    ...
  ]
}
```

### Using the Detectors

```python
from simulator.traffic_generator import TrafficGenerator
from features.extractor import FlowFeatureExtractor
from detectors import SynFloodDetector, PortScanDetector, C2BeaconDetector

# Generate traffic
generator = TrafficGenerator()
flows = generator.generate_traffic('syn_flood', intensity=0.8)

# Extract features
extractor = FlowFeatureExtractor()
features_df = extractor.extract_batch(flows)
mean_features = features_df.mean().to_dict()
aggregate = extractor.extract_aggregate(flows)

# Run detection
detector = SynFloodDetector()
detection = detector.detect(mean_features, aggregate)

if detection:
    print(f"Threat: {detection.threat_class}")
    print(f"Confidence: {detection.confidence:.0%}")
    print(f"Severity: {detection.severity}")
```

### Custom Configuration

```python
from detectors.config import DetectionConfig

# Create custom thresholds
config = DetectionConfig()
config.syn_flood.syn_ack_ratio_high = 5.0  # More sensitive
config.port_scan.unique_ports_medium = 25   # Detect smaller scans

# Use custom config
detector = SynFloodDetector(config.syn_flood)
```

### Running the Demo

```bash
cd backend
python demo_detection.py
```

The demo shows:
1. SYN flood detection with evidence
2. Port scan detection with reconnaissance indicators
3. C2 beacon detection with periodicity analysis
4. False positive testing on normal traffic
5. Custom threshold configuration
6. Multi-threat analysis across scenarios

---

## 🎯 Design Decisions

### 1. **Layered Architecture**
- **API Layer** - Route handlers, request/response
- **Service Layer** - Business logic, isolated from framework
- **Database Layer** - Data access, SQLAlchemy models
- **Schema Layer** - Pydantic models for validation

### 2. **SQLite for Development**
- Easy setup, no external database needed
- Production can migrate to PostgreSQL/MySQL with minimal changes
- Same SQLAlchemy models work with any SQL database

### 3. **Pydantic Schemas**
- Separate schemas for Create/Update/Response
- Automatic validation and serialization
- OpenAPI documentation generation

### 4. **Service Pattern**
- Business logic separated from API handlers
- Easier to test and maintain
- Can be reused across different endpoints

### 5. **No Authentication (Yet)**
- Phase 4 will add authentication
- Currently focused on core functionality
- CORS configured for local development

---

## 🔮 Next Steps (Not Implemented)

1. **Authentication & Authorization**
   - JWT tokens
   - Role-based access control
   - API key support

2. **ML Integration**
   - Traffic analysis pipeline
   - Model training endpoints
   - Real-time threat detection

3. **WebSocket Support**
   - Real-time alert streaming
   - Live metric updates
   - Dashboard live data

4. **Advanced Features**
   - Threat intelligence integration
   - PCAP analysis
   - Report generation
   - Alert correlation

---

## 📝 Notes

- All timestamps are stored in UTC
- Database uses SQLite (single file)
- Seed data includes realistic threat examples
- Evidence JSON stores detection-specific data
- Risk scores calculated algorithmically

---

## ✅ Status

**Phase Complete:** Backend API with database, seeding, and all CRUD operations.

**Working:**
- ✅ Database models
- ✅ API endpoints
- ✅ Service layer
- ✅ Pydantic schemas
- ✅ Database seeding
- ✅ CORS configuration
- ✅ Interactive API docs
- ✅ Traffic simulator (6 scenarios)
- ✅ Simulation API endpoints
- ✅ Synthetic flow generation
- ✅ Feature engineering (32 features)
- ✅ Single/batch/aggregate extraction
- ✅ Baseline detection (SYN flood, port scan, C2 beacon)
- ✅ Configurable detection thresholds
- ✅ Structured, explainable detections
- ✅ ML training dataset (2,850 samples, 6 classes)
- ✅ Dataset generation pipeline
- ✅ Train/test split (80/20, stratified)
- ✅ Random Forest classifier (100% test accuracy)
- ✅ ML prediction with confidence scores
- ✅ Feature importance analysis
- ✅ Comprehensive unit tests (48 tests passing)

**Note:** ML model trained on synthetic data only. Validation on real traffic required before production deployment.

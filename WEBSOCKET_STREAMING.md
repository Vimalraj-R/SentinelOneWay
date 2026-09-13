# Real-Time Threat Streaming with WebSockets

## Overview

SentinelOneWay now includes real-time threat alert streaming using WebSockets. When the hybrid detection engine generates a new alert, it is:

1. **Stored in the database**
2. **Broadcast to all connected dashboard clients via WebSocket**
3. **Displayed as a live notification**
4. **Updates dashboard statistics in real-time**

## Architecture

```
Detection Engine
      ↓
Alert Service (create_alert_with_broadcast)
      ↓
   Database ← Store
      ↓
WebSocket Manager ← Broadcast
      ↓
Connected Clients (Dashboard)
      ↓
UI Updates:
  - Alert notifications
  - Recent alerts table
  - Risk score
  - Severity counts
```

## Backend Implementation

### WebSocket Connection Manager

**File:** `backend/websocket/manager.py`

- Manages active WebSocket connections
- Broadcasts alerts to all clients
- Handles connection lifecycle
- Sends heartbeats every 30 seconds

```python
from websocket.manager import manager

# Broadcast alert to all connected clients
await manager.broadcast_alert(alert_data)
```

### WebSocket API Endpoint

**Endpoint:** `ws://localhost:8000/ws/alerts`

**File:** `backend/api/websocket.py`

Clients connect to this endpoint to receive real-time updates.

**Message Types:**
- `connection` - Initial connection confirmation
- `alert` - New threat alert
- `stats` - Statistics update
- `heartbeat` - Keep-alive message

### Alert Service with Broadcasting

**File:** `backend/services/alert_service.py`

New method: `create_alert_with_broadcast()`

```python
from services.alert_service import AlertService

# Create alert and broadcast to clients
alert = await AlertService.create_alert_with_broadcast(
    db=db,
    detection_result=detection_result,  # From hybrid engine
    flow_data=flow_data                 # Network flow info
)
```

## Frontend Implementation

### WebSocket Hook

**File:** `frontend/src/hooks/useWebSocket.js`

React hook for WebSocket connection management.

**Features:**
- Automatic connection on mount
- Reconnection logic (up to 10 attempts)
- Connection status tracking
- Message handling
- Cleanup on unmount

**Usage:**
```javascript
import { useWebSocket } from '../hooks/useWebSocket';

const { isConnected, connectionStatus } = useWebSocket((alert) => {
  console.log('New alert:', alert);
  // Handle alert...
});
```

### Dashboard Integration

**File:** `frontend/src/pages/Overview.jsx`

The dashboard automatically:
- Connects to WebSocket on load
- Shows connection status (Live/Connecting/Disconnected)
- Displays alert notifications (top-right corner)
- Refreshes dashboard statistics when alerts arrive
- Auto-dismisses notifications after 5 seconds

## Testing

### 1. Start Backend

```bash
cd backend
source venv/Scripts/activate  # Windows Git Bash
# or: source venv/bin/activate  # Linux/Mac
python main.py
```

Backend runs on `http://localhost:8000`

### 2. Start Frontend

```bash
cd frontend
npm run dev
```

Frontend runs on `http://localhost:5173`

### 3. Open Dashboard

Navigate to http://localhost:5173

You should see:
- **Live** indicator (green) in top-right when connected
- **Connecting...** (yellow) during connection
- **Disconnected** (gray) if connection fails

### 4. Simulate Alerts

Use the test API endpoints to generate alerts:

**Single Alert:**
```bash
curl -X POST http://localhost:8000/api/test/simulate-alert
```

**Multiple Alerts:**
```bash
curl -X POST "http://localhost:8000/api/test/simulate-multiple-alerts?count=5&delay_seconds=2"
```

You should see:
1. Alert notification slide in from right
2. Dashboard stats update
3. Recent alerts table update
4. Risk score may change

### 5. Monitor WebSocket

Open browser DevTools Console to see:
```
WebSocket connected
WebSocket message received: alert
New alert received via WebSocket: {threat_class: "SYN_FLOOD", ...}
Alert broadcast to 1 clients: SYN_FLOOD (risk: 92)
```

## Message Format

### Alert Message (WebSocket → Client)

```json
{
  "type": "alert",
  "data": {
    "id": 123,
    "timestamp": "2024-09-13T12:34:56.789Z",
    "flow_id": "flow_1234567890",
    
    "threat_class": "SYN_FLOOD",
    "severity": "Critical",
    "confidence": 0.95,
    "risk_score": 92,
    
    "src_ip": "203.0.113.45",
    "dst_ip": "192.168.1.10",
    "src_port": "54321",
    "dst_port": "80",
    "protocol": "TCP",
    
    "status": "Active",
    "explanation": "High volume SYN packets detected from single source",
    "detectors_triggered": ["rule_syn_flood", "random_forest", "isolation_forest"],
    "anomaly_score": 98.5,
    
    "created_at": "2024-09-13T12:34:56.789Z"
  },
  "timestamp": "2024-09-13T12:34:56.789Z"
}
```

## Connection Management

### Automatic Reconnection

The WebSocket hook automatically reconnects if connection is lost:
- **Max Attempts:** 10
- **Delay:** 3 seconds between attempts
- **Exponential Backoff:** No (fixed delay)

### Heartbeat

Server sends heartbeat every 30 seconds to keep connection alive:
```json
{
  "type": "heartbeat",
  "timestamp": "2024-09-13T12:34:56.789Z"
}
```

### Fallback to REST API

If WebSocket disconnects, dashboard continues to work using REST API:
- Polls `/api/dashboard/summary` for updates
- Manual refresh button available
- Connection status indicator shows state

## Integration with Detection Engine

To integrate the hybrid detection engine with real-time streaming:

```python
from detection.hybrid_engine import get_hybrid_engine
from services.alert_service import AlertService
from database.base import get_db

# Run detection
engine = get_hybrid_engine()
result = engine.detect(single_flow_features, aggregate_features)

# If threat detected, create and broadcast alert
if result.threat_class != "NORMAL":
    db = next(get_db())
    
    detection_result = result.to_dict()
    flow_data = {
        'flow_id': 'flow_xyz',
        'src_ip': '192.168.1.100',
        'dst_ip': '8.8.8.8',
        'src_port': '54321',
        'dst_port': '443',
        'protocol': 'TCP'
    }
    
    alert = await AlertService.create_alert_with_broadcast(
        db,
        detection_result,
        flow_data
    )
```

## WebSocket Status Endpoint

**GET** `/ws/status`

Returns connection statistics:

```json
{
  "active_connections": 3,
  "total_alerts_sent": 45,
  "clients": [
    {
      "client_id": "client_1",
      "connected_at": "2024-09-13T12:00:00Z",
      "alerts_sent": 15
    }
  ]
}
```

## Configuration

### WebSocket URL

**Frontend:** `frontend/src/hooks/useWebSocket.js`
```javascript
const WS_URL = 'ws://localhost:8000/ws/alerts';
```

Change for production:
```javascript
const WS_URL = process.env.VITE_WS_URL || 'ws://localhost:8000/ws/alerts';
```

### Reconnection Settings

```javascript
const RECONNECT_DELAY = 3000; // 3 seconds
const MAX_RECONNECT_ATTEMPTS = 10;
```

### Heartbeat Interval

**Backend:** `backend/websocket/manager.py`
```python
await asyncio.sleep(30)  # Send heartbeat every 30 seconds
```

## Troubleshooting

### WebSocket Won't Connect

1. **Check backend is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check CORS settings:**
   Backend must allow WebSocket origins in `main.py`

3. **Check browser console:**
   Look for WebSocket connection errors

4. **Test WebSocket endpoint:**
   ```bash
   curl http://localhost:8000/ws/status
   ```

### Notifications Not Appearing

1. **Check WebSocket connection status** (top-right of dashboard)
2. **Open browser DevTools Console** - look for "New alert received"
3. **Test with simulate-alert endpoint**
4. **Check browser doesn't block notifications**

### Connection Keeps Dropping

1. **Check heartbeat is running** (backend logs)
2. **Increase reconnect attempts** in `useWebSocket.js`
3. **Check network stability**
4. **Check firewall/proxy settings**

## Production Considerations

### Security

1. **Use WSS (WebSocket Secure)** in production:
   ```javascript
   const WS_URL = 'wss://yourapi.com/ws/alerts';
   ```

2. **Add authentication:**
   ```javascript
   const ws = new WebSocket(`${WS_URL}?token=${authToken}`);
   ```

3. **Rate limiting:** Limit connection attempts per IP

### Scalability

1. **Load balancing:** Use sticky sessions or Redis pub/sub
2. **Connection limits:** Set max connections per server
3. **Message queuing:** Use Redis for high-throughput scenarios

### Monitoring

1. **Track connection metrics:**
   - Active connections
   - Messages sent/received
   - Connection errors
   - Reconnection attempts

2. **Alert on issues:**
   - All clients disconnected
   - High reconnection rate
   - Message delivery failures

## Files Summary

**Backend:**
- `websocket/manager.py` - Connection management
- `websocket/__init__.py` - Package exports
- `api/websocket.py` - WebSocket endpoint
- `api/test_alerts.py` - Testing endpoints
- `services/alert_service.py` - Alert creation + broadcasting
- `main.py` - WebSocket router + heartbeat startup

**Frontend:**
- `hooks/useWebSocket.js` - WebSocket React hook
- `pages/Overview.jsx` - Dashboard with real-time updates
- `index.css` - Notification animations

**Documentation:**
- `WEBSOCKET_STREAMING.md` - This file

## Next Steps

1. ✅ WebSocket connection management
2. ✅ Real-time alert broadcasting
3. ✅ Dashboard notifications
4. ✅ Connection status indicator
5. ✅ Automatic reconnection
6. ⏳ Authentication/authorization
7. ⏳ Redis pub/sub for multi-server
8. ⏳ Alert filtering/subscriptions
9. ⏳ Performance monitoring
10. ⏳ Production deployment

---

**Status:** Real-time threat streaming implemented and tested. Ready for integration with live detection pipeline.

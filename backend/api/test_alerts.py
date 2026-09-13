"""
Test endpoints for simulating alerts and testing WebSocket streaming.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import asyncio
from datetime import datetime
import random

from database.base import get_db
from services.alert_service import AlertService

router = APIRouter(prefix="/api/test", tags=["Testing"])


@router.post("/simulate-alert")
async def simulate_alert(db: Session = Depends(get_db)):
    """
    Simulate a threat alert for testing WebSocket functionality.

    Creates a random alert and broadcasts it to all connected clients.
    """
    # Random threat scenarios
    scenarios = [
        {
            "threat_class": "SYN_FLOOD",
            "severity": "Critical",
            "confidence": 0.95,
            "risk_score": 92,
            "src_ip": f"203.0.113.{random.randint(1, 254)}",
            "dst_ip": "192.168.1.10",
            "dst_port": "80",
            "protocol": "TCP",
            "explanation": "High volume SYN packets detected from single source",
            "detectors": ["rule_syn_flood", "random_forest", "isolation_forest"]
        },
        {
            "threat_class": "PORT_SCAN",
            "severity": "High",
            "confidence": 0.88,
            "risk_score": 75,
            "src_ip": f"198.51.100.{random.randint(1, 254)}",
            "dst_ip": "192.168.1.50",
            "dst_port": "various",
            "protocol": "TCP",
            "explanation": "Sequential port probing detected across multiple services",
            "detectors": ["rule_port_scan", "random_forest"]
        },
        {
            "threat_class": "C2_BEACON",
            "severity": "High",
            "confidence": 0.82,
            "risk_score": 78,
            "src_ip": "192.168.1.100",
            "dst_ip": f"185.220.{random.randint(100, 200)}.{random.randint(1, 254)}",
            "dst_port": "443",
            "protocol": "TCP",
            "explanation": "Regular periodic beaconing pattern detected",
            "detectors": ["rule_c2_beacon", "isolation_forest"]
        },
        {
            "threat_class": "DNS_TUNNEL",
            "severity": "Medium",
            "confidence": 0.76,
            "risk_score": 65,
            "src_ip": "192.168.1.120",
            "dst_ip": "8.8.8.8",
            "dst_port": "53",
            "protocol": "UDP",
            "explanation": "Unusual DNS query patterns suggesting data exfiltration",
            "detectors": ["random_forest", "isolation_forest"]
        },
        {
            "threat_class": "DATA_EXFILTRATION",
            "severity": "Critical",
            "confidence": 0.91,
            "risk_score": 88,
            "src_ip": "192.168.1.75",
            "dst_ip": f"52.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "dst_port": "443",
            "protocol": "TCP",
            "explanation": "Large data transfer to external destination detected",
            "detectors": ["random_forest", "isolation_forest"]
        }
    ]

    # Pick random scenario
    scenario = random.choice(scenarios)

    # Create detection result
    detection_result = {
        "threat_class": scenario["threat_class"],
        "confidence": scenario["confidence"],
        "anomaly_score": random.uniform(60, 100),
        "risk_score": scenario["risk_score"],
        "severity": scenario["severity"],
        "evidence": {
            "packets_per_second": random.uniform(100, 2000),
            "bytes_per_second": random.uniform(10000, 500000),
        },
        "human_explanation": [scenario["explanation"]],
        "detectors_triggered": scenario["detectors"]
    }

    # Create flow data
    flow_data = {
        "flow_id": f"test_flow_{datetime.utcnow().timestamp()}",
        "src_ip": scenario["src_ip"],
        "dst_ip": scenario["dst_ip"],
        "src_port": str(random.randint(30000, 65000)),
        "dst_port": scenario["dst_port"],
        "protocol": scenario["protocol"]
    }

    # Create and broadcast alert
    alert = await AlertService.create_alert_with_broadcast(
        db,
        detection_result,
        flow_data
    )

    return {
        "status": "success",
        "message": "Alert simulated and broadcast",
        "alert": {
            "id": alert.id,
            "threat_class": alert.threat_class,
            "severity": alert.severity.value,
            "risk_score": alert.risk_score,
            "src_ip": alert.src_ip,
            "dst_ip": alert.dst_ip
        }
    }


@router.post("/simulate-multiple-alerts")
async def simulate_multiple_alerts(
    count: int = 5,
    delay_seconds: float = 2.0,
    db: Session = Depends(get_db)
):
    """
    Simulate multiple alerts with delay between them.

    Useful for testing dashboard updates and WebSocket stream handling.

    Args:
        count: Number of alerts to generate
        delay_seconds: Delay between alerts
    """
    created_alerts = []

    for i in range(count):
        # Simulate alert
        result = await simulate_alert(db)
        created_alerts.append(result["alert"])

        # Wait before next alert (except for last one)
        if i < count - 1:
            await asyncio.sleep(delay_seconds)

    return {
        "status": "success",
        "message": f"Generated {count} alerts",
        "alerts": created_alerts
    }

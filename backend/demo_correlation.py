"""
Demo script for attack correlation and incident generation.

Creates sample multi-stage attacks and correlates them into incidents.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from datetime import datetime, timedelta
from database.base import SessionLocal, engine, Base
from database.models import Alert, AlertSeverity, AlertStatus
from database.incident_models import Incident
from services.incident_service import IncidentService
import json


def create_demo_alerts():
    """Create demo alerts for correlation testing."""
    db = SessionLocal()

    print("=" * 80)
    print("Creating Demo Alerts for Correlation")
    print("=" * 80)

    # Base time
    base_time = datetime.utcnow() - timedelta(minutes=30)
    timestamp_suffix = int(datetime.utcnow().timestamp())

    # Scenario 1: Multi-stage compromise (Port Scan → C2 → Exfiltration)
    print("\nScenario 1: Multi-stage Compromise")
    print("-" * 80)

    alerts_scenario1 = [
        {
            'timestamp': base_time,
            'threat_class': 'PORT_SCAN',
            'src_ip': '203.0.113.45',
            'dst_ip': '192.168.1.100',
            'dst_port': 'various',
            'protocol': 'TCP',
            'severity': AlertSeverity.HIGH,
            'confidence': 0.92,
            'risk_score': 78,
            'flow_id': f'flow_001_{timestamp_suffix}'
        },
        {
            'timestamp': base_time + timedelta(minutes=4),
            'threat_class': 'C2_BEACON',
            'src_ip': '192.168.1.100',
            'dst_ip': '185.220.100.50',
            'dst_port': '443',
            'protocol': 'TCP',
            'severity': AlertSeverity.HIGH,
            'confidence': 0.87,
            'risk_score': 82,
            'flow_id': f'flow_002_{timestamp_suffix}'
        },
        {
            'timestamp': base_time + timedelta(minutes=12),
            'threat_class': 'DATA_EXFILTRATION',
            'src_ip': '192.168.1.100',
            'dst_ip': '52.45.67.89',
            'dst_port': '443',
            'protocol': 'TCP',
            'severity': AlertSeverity.CRITICAL,
            'confidence': 0.94,
            'risk_score': 91,
            'flow_id': f'flow_00\1_{timestamp_suffix}'
        }
    ]

    for alert_data in alerts_scenario1:
        alert = Alert(
            **alert_data,
            status=AlertStatus.ACTIVE,
            evidence_json=json.dumps({
                'evidence': {},
                'human_explanation': [f"Detected {alert_data['threat_class']} activity"],
                'detectors_triggered': ['hybrid_engine'],
                'anomaly_score': 85.0
            })
        )
        db.add(alert)

    print(f"  Created {len(alerts_scenario1)} alerts:")
    print(f"    - Port Scan at {alerts_scenario1[0]['timestamp'].strftime('%H:%M')}")
    print(f"    - C2 Beacon at {alerts_scenario1[1]['timestamp'].strftime('%H:%M')}")
    print(f"    - Data Exfiltration at {alerts_scenario1[2]['timestamp'].strftime('%H:%M')}")

    # Scenario 2: DDoS Campaign (Port Scan → SYN Flood)
    print("\nScenario 2: DDoS Campaign")
    print("-" * 80)

    alerts_scenario2 = [
        {
            'timestamp': base_time + timedelta(minutes=15),
            'threat_class': 'PORT_SCAN',
            'src_ip': '198.51.100.10',
            'dst_ip': '192.168.1.50',
            'dst_port': 'various',
            'protocol': 'TCP',
            'severity': AlertSeverity.MEDIUM,
            'confidence': 0.85,
            'risk_score': 72,
            'flow_id': f'flow_00\1_{timestamp_suffix}'
        },
        {
            'timestamp': base_time + timedelta(minutes=18),
            'threat_class': 'SYN_FLOOD',
            'src_ip': '198.51.100.15',
            'dst_ip': '192.168.1.50',
            'dst_port': '80',
            'protocol': 'TCP',
            'severity': AlertSeverity.CRITICAL,
            'confidence': 0.96,
            'risk_score': 94,
            'flow_id': f'flow_00\1_{timestamp_suffix}'
        }
    ]

    for alert_data in alerts_scenario2:
        alert = Alert(
            **alert_data,
            status=AlertStatus.ACTIVE,
            evidence_json=json.dumps({
                'evidence': {},
                'human_explanation': [f"Detected {alert_data['threat_class']} activity"],
                'detectors_triggered': ['hybrid_engine'],
                'anomaly_score': 80.0
            })
        )
        db.add(alert)

    print(f"  Created {len(alerts_scenario2)} alerts:")
    print(f"    - Port Scan at {alerts_scenario2[0]['timestamp'].strftime('%H:%M')}")
    print(f"    - SYN Flood at {alerts_scenario2[1]['timestamp'].strftime('%H:%M')}")

    # Scenario 3: Persistent C2 Activity (Multiple C2 beacons)
    print("\nScenario 3: Persistent C2 Activity")
    print("-" * 80)

    alerts_scenario3 = [
        {
            'timestamp': base_time + timedelta(minutes=20),
            'threat_class': 'C2_BEACON',
            'src_ip': '192.168.1.75',
            'dst_ip': '45.76.123.45',
            'dst_port': '443',
            'protocol': 'TCP',
            'severity': AlertSeverity.HIGH,
            'confidence': 0.89,
            'risk_score': 81,
            'flow_id': f'flow_00\1_{timestamp_suffix}'
        },
        {
            'timestamp': base_time + timedelta(minutes=23),
            'threat_class': 'C2_BEACON',
            'src_ip': '192.168.1.75',
            'dst_ip': '45.76.123.45',
            'dst_port': '443',
            'protocol': 'TCP',
            'severity': AlertSeverity.HIGH,
            'confidence': 0.91,
            'risk_score': 83,
            'flow_id': f'flow_00\1_{timestamp_suffix}'
        }
    ]

    for alert_data in alerts_scenario3:
        alert = Alert(
            **alert_data,
            status=AlertStatus.ACTIVE,
            evidence_json=json.dumps({
                'evidence': {},
                'human_explanation': [f"Detected {alert_data['threat_class']} activity"],
                'detectors_triggered': ['hybrid_engine'],
                'anomaly_score': 78.0
            })
        )
        db.add(alert)

    print(f"  Created {len(alerts_scenario3)} alerts:")
    print(f"    - C2 Beacon #1 at {alerts_scenario3[0]['timestamp'].strftime('%H:%M')}")
    print(f"    - C2 Beacon #2 at {alerts_scenario3[1]['timestamp'].strftime('%H:%M')}")

    db.commit()
    total_alerts = len(alerts_scenario1) + len(alerts_scenario2) + len(alerts_scenario3)
    print(f"\nTotal alerts created: {total_alerts}")
    db.close()


def correlate_alerts():
    """Run correlation on recent alerts."""
    db = SessionLocal()

    print("\n" + "=" * 80)
    print("Running Alert Correlation")
    print("=" * 80)

    incidents = IncidentService.correlate_recent_alerts(db, hours=1)

    print(f"\nCorrelation complete: {len(incidents)} incidents created")

    for incident in incidents:
        print(f"\n{'-' * 80}")
        print(f"Incident: {incident.incident_id}")
        print(f"Pattern:  {incident.attack_pattern}")
        print(f"Severity: {incident.severity.value}")
        print(f"Risk:     {incident.risk_score}/100")
        print(f"Alerts:   {incident.alert_count}")
        print(f"Summary:  {incident.summary}")

    db.close()
    return incidents


def main():
    """Run demo."""
    print("\n" + "=" * 80)
    print("ATTACK CORRELATION DEMO")
    print("=" * 80)

    # Initialize database
    print("\nInitializing database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database ready!")

    # Create demo alerts
    create_demo_alerts()

    # Run correlation
    incidents = correlate_alerts()

    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print(f"\nGenerated {len(incidents)} correlated incidents")
    print("\nView them at:")
    print("  Frontend: http://localhost:5173/attack-timeline")
    print("  API:      http://localhost:8000/api/incidents/")
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()

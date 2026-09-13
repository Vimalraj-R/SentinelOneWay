"""
Database seeding script for development.

This script populates the database with realistic sample data
for testing and development purposes.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from datetime import datetime, timedelta
import random
import json

from database.base import SessionLocal, engine, Base
from database.models import Alert, NetworkMetric, Asset, AlertStatus, AlertSeverity, AssetCriticality


def seed_database():
    """Seed the database with sample data."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Check if data already exists
        if db.query(Alert).count() > 0:
            print("Database already contains data. Skipping seed.")
            return

        print("Seeding database with sample data...")

        # Seed Assets
        print("Creating assets...")
        assets_data = [
            {
                'ip_address': '10.0.1.15',
                'hostname': 'web-server-01',
                'asset_type': 'server',
                'criticality': AssetCriticality.CRITICAL,
                'risk_score': 78
            },
            {
                'ip_address': '10.0.2.50',
                'hostname': 'db-primary',
                'asset_type': 'server',
                'criticality': AssetCriticality.CRITICAL,
                'risk_score': 85
            },
            {
                'ip_address': '10.0.3.142',
                'hostname': 'workstation-42',
                'asset_type': 'workstation',
                'criticality': AssetCriticality.HIGH,
                'risk_score': 72
            },
            {
                'ip_address': '10.0.4.88',
                'hostname': 'dns-resolver',
                'asset_type': 'server',
                'criticality': AssetCriticality.HIGH,
                'risk_score': 65
            },
            {
                'ip_address': '10.0.5.201',
                'hostname': 'file-server',
                'asset_type': 'server',
                'criticality': AssetCriticality.HIGH,
                'risk_score': 68
            },
            {
                'ip_address': '10.0.6.30',
                'hostname': 'workstation-30',
                'asset_type': 'workstation',
                'criticality': AssetCriticality.MEDIUM,
                'risk_score': 45
            },
            {
                'ip_address': '10.0.7.100',
                'hostname': 'firewall-01',
                'asset_type': 'network_device',
                'criticality': AssetCriticality.CRITICAL,
                'risk_score': 40
            },
            {
                'ip_address': '10.0.8.250',
                'hostname': 'backup-server',
                'asset_type': 'server',
                'criticality': AssetCriticality.MEDIUM,
                'risk_score': 35
            }
        ]

        for asset_data in assets_data:
            asset = Asset(**asset_data)
            db.add(asset)

        db.commit()
        print(f"Created {len(assets_data)} assets")

        # Seed Alerts
        print("Creating alerts...")
        base_time = datetime.utcnow()

        alerts_data = [
            {
                'timestamp': base_time - timedelta(minutes=13),
                'flow_id': 'FLW-2026091323471201',
                'threat_class': 'SYN Flood',
                'severity': AlertSeverity.CRITICAL,
                'confidence': 0.94,
                'risk_score': 92,
                'src_ip': '203.0.113.45',
                'dst_ip': '10.0.1.15',
                'src_port': 'Multiple',
                'dst_port': '443',
                'protocol': 'TCP',
                'status': AlertStatus.ACTIVE,
                'evidence_json': json.dumps({
                    'syn_rate': 182400,
                    'baseline_rate': 12500,
                    'unique_sources': 23421,
                    'syn_ack_ratio': 18.4
                })
            },
            {
                'timestamp': base_time - timedelta(minutes=15),
                'flow_id': 'FLW-2026091323453301',
                'threat_class': 'Port Scan',
                'severity': AlertSeverity.HIGH,
                'confidence': 0.89,
                'risk_score': 78,
                'src_ip': '198.51.100.88',
                'dst_ip': '10.0.2.50',
                'src_port': 'Multiple',
                'dst_port': '1-65535',
                'protocol': 'TCP',
                'status': AlertStatus.ACTIVE,
                'evidence_json': json.dumps({
                    'hosts_scanned': 42,
                    'ports_probed': 65535,
                    'scan_rate': 289
                })
            },
            {
                'timestamp': base_time - timedelta(minutes=18),
                'flow_id': 'FLW-2026091323421801',
                'threat_class': 'C2 Beacon',
                'severity': AlertSeverity.CRITICAL,
                'confidence': 0.97,
                'risk_score': 95,
                'src_ip': '10.0.3.142',
                'dst_ip': '185.220.101.5',
                'src_port': '49847',
                'dst_port': '8080',
                'protocol': 'TCP/HTTPS',
                'status': AlertStatus.INVESTIGATING,
                'evidence_json': json.dumps({
                    'beacon_interval': 120,
                    'regularity': 0.987,
                    'beacon_count': 67,
                    'payload_size': 154
                })
            },
            {
                'timestamp': base_time - timedelta(minutes=22),
                'flow_id': 'FLW-2026091323380501',
                'threat_class': 'DNS Tunnel',
                'severity': AlertSeverity.HIGH,
                'confidence': 0.82,
                'risk_score': 75,
                'src_ip': '10.0.4.88',
                'dst_ip': '8.8.8.8',
                'src_port': '53241',
                'dst_port': '53',
                'protocol': 'UDP/DNS',
                'status': AlertStatus.ACTIVE,
                'evidence_json': json.dumps({
                    'query_length_avg': 67,
                    'entropy': 0.91,
                    'subdomain_count': 47
                })
            },
            {
                'timestamp': base_time - timedelta(minutes=25),
                'flow_id': 'FLW-2026091323354401',
                'threat_class': 'Data Exfiltration',
                'severity': AlertSeverity.CRITICAL,
                'confidence': 0.91,
                'risk_score': 88,
                'src_ip': '10.0.5.201',
                'dst_ip': '198.51.100.200',
                'src_port': '54123',
                'dst_port': '443',
                'protocol': 'TCP/HTTPS',
                'status': AlertStatus.BLOCKED,
                'evidence_json': json.dumps({
                    'bytes_transferred': 824000000,
                    'duration_seconds': 1240,
                    'encryption': 'TLS 1.3'
                })
            },
            {
                'timestamp': base_time - timedelta(minutes=32),
                'flow_id': 'FLW-2026091323282201',
                'threat_class': 'Port Scan',
                'severity': AlertSeverity.MEDIUM,
                'confidence': 0.76,
                'risk_score': 62,
                'src_ip': '203.0.113.120',
                'dst_ip': '10.0.6.30',
                'src_port': 'Multiple',
                'dst_port': 'Multiple',
                'protocol': 'TCP',
                'status': AlertStatus.RESOLVED,
                'evidence_json': json.dumps({
                    'hosts_scanned': 1,
                    'ports_probed': 1024,
                    'scan_rate': 145
                })
            },
            {
                'timestamp': base_time - timedelta(hours=2),
                'flow_id': 'FLW-2026091321154401',
                'threat_class': 'Brute Force',
                'severity': AlertSeverity.HIGH,
                'confidence': 0.88,
                'risk_score': 74,
                'src_ip': '192.0.2.50',
                'dst_ip': '10.0.1.15',
                'src_port': '58422',
                'dst_port': '22',
                'protocol': 'TCP/SSH',
                'status': AlertStatus.RESOLVED,
                'evidence_json': json.dumps({
                    'failed_attempts': 487,
                    'duration_seconds': 320,
                    'unique_usernames': 42
                })
            },
            {
                'timestamp': base_time - timedelta(hours=4),
                'flow_id': 'FLW-2026091319234501',
                'threat_class': 'Unusual Outbound',
                'severity': AlertSeverity.MEDIUM,
                'confidence': 0.71,
                'risk_score': 58,
                'src_ip': '10.0.6.30',
                'dst_ip': '192.0.2.100',
                'src_port': '49233',
                'dst_port': '443',
                'protocol': 'TCP/HTTPS',
                'status': AlertStatus.ACKNOWLEDGED,
                'evidence_json': json.dumps({
                    'destination_country': 'Unknown',
                    'bytes_sent': 125000000,
                    'first_seen': True
                })
            }
        ]

        for alert_data in alerts_data:
            alert = Alert(**alert_data)
            db.add(alert)

        db.commit()
        print(f"Created {len(alerts_data)} alerts")

        # Seed Network Metrics
        print("Creating network metrics...")
        base_time = datetime.utcnow()

        # Create metrics for the last 24 hours (one per hour)
        for hour in range(24):
            timestamp = base_time - timedelta(hours=23-hour)

            # Simulate traffic patterns (higher during business hours)
            hour_of_day = timestamp.hour
            if 8 <= hour_of_day <= 18:  # Business hours
                base_flow = random.uniform(2000, 3200)
            elif 20 <= hour_of_day or hour_of_day <= 6:  # Night
                base_flow = random.uniform(800, 1500)
            else:  # Off-peak
                base_flow = random.uniform(1500, 2200)

            metric = NetworkMetric(
                timestamp=timestamp,
                flows_per_second=base_flow,
                packets_per_second=base_flow * random.uniform(8, 15),
                bytes_per_second=base_flow * random.uniform(1200, 2500),
                tcp_percentage=random.uniform(65, 75),
                udp_percentage=random.uniform(15, 25),
                dns_percentage=random.uniform(5, 10)
            )
            db.add(metric)

        db.commit()
        print("Created 24 network metric records")

        print("\n[SUCCESS] Database seeded successfully!")
        print(f"   - {len(assets_data)} assets")
        print(f"   - {len(alerts_data)} alerts")
        print(f"   - 24 network metrics")

    except Exception as e:
        print(f"\n[ERROR] Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

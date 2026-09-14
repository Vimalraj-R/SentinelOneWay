"""
Continuous Traffic Service - Generates live traffic for MVP demonstration.

This service runs a background simulation that continuously generates
network flows, feeds them into the detection pipeline, and creates
real-time alerts and metrics across the entire system.
"""
import threading
import time
import random
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from database.base import SessionLocal
from database.models import Alert, AlertSeverity, AlertStatus, NetworkMetric
from database.incident_models import Incident
from simulator.simulation_manager import simulation_manager
from websocket.manager import manager as websocket_manager
from services.incident_service import IncidentService


class ContinuousTrafficService:
    """
    Manages continuous background traffic generation for live MVP demo.

    Features:
    - Generates realistic traffic patterns 24/7
    - Creates alerts from detected threats
    - Updates metrics in real-time
    - Cycles through different attack scenarios
    - Provides live data to all frontend pages
    """

    def __init__(self):
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.stop_flag = threading.Event()
        self.current_scenario = "normal"
        self.scenario_start_time = None
        self.flows_processed = 0
        self.alerts_generated = 0
        self.event_loop = None  # Will be set to FastAPI's event loop

        # Scenario rotation for realistic demo
        self.scenarios = [
            ("normal", 120, 0.3),         # 2 min normal traffic (low intensity)
            ("port_scan", 30, 0.6),       # 30 sec port scan (medium)
            ("normal", 60, 0.3),          # 1 min normal
            ("c2_beacon", 45, 0.7),       # 45 sec C2 beaconing (high)
            ("normal", 90, 0.3),          # 1.5 min normal
            ("syn_flood", 20, 0.8),       # 20 sec SYN flood (very high)
            ("normal", 120, 0.3),         # 2 min normal
            ("dns_tunnel", 40, 0.6),      # 40 sec DNS tunneling
            ("normal", 90, 0.3),          # 1.5 min normal
            ("data_exfiltration", 35, 0.7) # 35 sec data exfil
        ]
        self.scenario_index = 0

    def start(self):
        """Start continuous traffic generation in background."""
        if self.is_running:
            print("[WARN] Continuous traffic service already running")
            return

        self.is_running = True
        self.stop_flag.clear()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

        print("[OK] Continuous traffic service started")
        print("     Generating live flows -> alerts -> metrics -> incidents")
        print("     All pages will show real-time updates!")

    def stop(self):
        """Stop continuous traffic generation."""
        if not self.is_running:
            return

        print("[STOP] Stopping continuous traffic service...")
        self.is_running = False
        self.stop_flag.set()

        # Stop current simulation
        try:
            simulation_manager.stop()
        except:
            pass

        if self.thread:
            self.thread.join(timeout=5)

        print(f"[OK] Stopped. Generated {self.flows_processed} flows, {self.alerts_generated} alerts")

    def _run_loop(self):
        """Main loop - rotates through scenarios and generates data."""
        print("[LOOP] Traffic generation loop started")

        while self.is_running and not self.stop_flag.is_set():
            try:
                # Get current scenario
                scenario, duration, intensity = self.scenarios[self.scenario_index]

                print(f"\n[SCENARIO] Starting: {scenario} (intensity={intensity}, duration={duration}s)")

                # Start simulation for this scenario
                simulation_manager.start(scenario=scenario, intensity=intensity)

                # Run for specified duration
                start_time = time.time()
                while (time.time() - start_time) < duration and self.is_running:
                    # Every 5 seconds, generate alerts and update metrics
                    if int(time.time() - start_time) % 5 == 0:
                        self._generate_alert_from_scenario(scenario, intensity)
                        self._update_metrics(scenario, intensity)

                    time.sleep(1)

                # Stop this scenario
                stats = simulation_manager.stop()
                self.flows_processed += stats.get('flows_generated', 0)

                # Move to next scenario
                self.scenario_index = (self.scenario_index + 1) % len(self.scenarios)

                # Small pause between scenarios
                time.sleep(2)

            except Exception as e:
                print(f"[ERROR] Error in traffic loop: {e}")
                time.sleep(5)  # Wait before retrying

    def _generate_alert_from_scenario(self, scenario: str, intensity: float):
        """Generate realistic alerts based on current scenario."""
        # Only generate alerts for attack scenarios (not normal)
        if scenario == "normal":
            return

        # Probability of generating an alert this cycle
        alert_probability = intensity * 0.3  # 0-30% chance per 5-second cycle

        if random.random() > alert_probability:
            return

        db = SessionLocal()
        try:
            # Map scenarios to threat classes
            threat_map = {
                "syn_flood": ("SYN_FLOOD", AlertSeverity.CRITICAL, "SYN flood DDoS attack detected"),
                "port_scan": ("PORT_SCAN", AlertSeverity.HIGH, "Systematic port scanning activity"),
                "c2_beacon": ("C2_BEACON", AlertSeverity.CRITICAL, "Command & Control beaconing detected"),
                "dns_tunnel": ("DNS_TUNNEL", AlertSeverity.HIGH, "DNS tunneling covert channel"),
                "data_exfiltration": ("DATA_EXFILTRATION", AlertSeverity.CRITICAL, "Large-scale data exfiltration")
            }

            threat_class, severity, description = threat_map.get(
                scenario,
                ("UNKNOWN", AlertSeverity.MEDIUM, "Anomalous network activity")
            )

            # Generate realistic IPs
            src_ips = ["192.168.1.50", "192.168.1.105", "10.0.0.23", "172.16.0.8"]
            dst_ips = ["45.76.123.45", "52.45.67.89", "8.8.8.8", "1.1.1.1"]

            # Create alert with flow_id (required field)
            flow_id = f"flow_{int(datetime.now().timestamp() * 1000)}_{random.randint(1000, 9999)}"

            alert = Alert(
                timestamp=datetime.now(),
                flow_id=flow_id,
                src_ip=random.choice(src_ips),
                dst_ip=random.choice(dst_ips),
                src_port=random.randint(1024, 65535),
                dst_port=random.choice([80, 443, 8080, 53, 22, 3389]),
                protocol="TCP",
                threat_class=threat_class,
                severity=severity,
                confidence=0.85 + (intensity * 0.15),  # 85-100% confidence
                risk_score=int(70 + (intensity * 30)),  # 70-100 risk
                status=AlertStatus.ACTIVE,
                detection_method="Hybrid",
                rule_triggered=f"{threat_class}_DETECTOR",
                description=description
            )

            db.add(alert)
            db.commit()
            db.refresh(alert)  # Get the ID and updated fields

            # Rebuild recent incidents so the Attack Timeline reflects live alerts.
            IncidentService.correlate_recent_alerts(db, hours=24)

            self.alerts_generated += 1
            print(f"   [ALERT] #{self.alerts_generated}: {threat_class} ({severity.value})")

            # Broadcast alert to WebSocket clients for live notifications
            self._broadcast_alert_to_websocket(alert)

        except Exception as e:
            print(f"   [WARN] Error generating alert: {e}")
            db.rollback()
        finally:
            db.close()

    def _update_metrics(self, scenario: str, intensity: float):
        """Update network metrics in database."""
        db = SessionLocal()
        try:
            # Get simulation status for flow count
            status = simulation_manager.get_status()
            flows_generated = status.get('flows_generated', 0)

            # Generate realistic metric based on intensity
            base_flows = 1500 + (intensity * 1500)  # 1500-3000 flows/sec
            base_packets = base_flows * 10  # ~10 packets per flow
            base_bytes = base_packets * 800  # ~800 bytes per packet

            # Add some randomness
            flows_ps = base_flows + random.uniform(-200, 200)
            packets_ps = base_packets + random.uniform(-1000, 1000)
            bytes_ps = base_bytes + random.uniform(-50000, 50000)

            # Protocol distribution (varies by scenario)
            if scenario == "syn_flood":
                tcp_pct = 95.0
                udp_pct = 4.0
                dns_pct = 1.0
            elif scenario == "dns_tunnel":
                tcp_pct = 30.0
                udp_pct = 60.0
                dns_pct = 10.0
            else:
                tcp_pct = 70.0 + random.uniform(-5, 5)
                udp_pct = 25.0 + random.uniform(-3, 3)
                dns_pct = 5.0 + random.uniform(-2, 2)

            # Create metric record
            metric = NetworkMetric(
                timestamp=datetime.now(),
                flows_per_second=flows_ps,
                packets_per_second=packets_ps,
                bytes_per_second=bytes_ps,
                tcp_percentage=tcp_pct,
                udp_percentage=udp_pct,
                dns_percentage=dns_pct
            )

            db.add(metric)
            db.commit()

            print(f"   [METRICS] {flows_ps:.0f} flows/s, {bytes_ps/1024/1024:.1f} MB/s")

        except Exception as e:
            print(f"   [WARN] Error updating metrics: {e}")
            db.rollback()
        finally:
            db.close()

    def _broadcast_alert_to_websocket(self, alert: Alert):
        """
        Broadcast alert to WebSocket clients for real-time notifications.

        Args:
            alert: Alert model instance to broadcast
        """
        try:
            # Convert alert to dictionary for WebSocket transmission
            alert_dict = {
                'id': alert.id,
                'timestamp': alert.timestamp.isoformat(),
                'src_ip': alert.src_ip,
                'dst_ip': alert.dst_ip,
                'dst_port': alert.dst_port,
                'protocol': alert.protocol,
                'threat_class': alert.threat_class,
                'severity': alert.severity.value,
                'confidence': alert.confidence,
                'risk_score': alert.risk_score,
                'status': alert.status.value,
                'description': alert.description
            }

            # Broadcast to WebSocket clients using the main event loop
            if self.event_loop and websocket_manager.active_connections:
                asyncio.run_coroutine_threadsafe(
                    websocket_manager.broadcast_alert(alert_dict),
                    self.event_loop
                )
                print(f"   [WS] Broadcasted alert #{alert.id} to {len(websocket_manager.active_connections)} clients")
            else:
                if not self.event_loop:
                    print(f"   [WS] No event loop available for broadcast")
                else:
                    print(f"   [WS] No active WebSocket connections")

        except Exception as e:
            print(f"   [WARN] Error broadcasting to WebSocket: {e}")

    def get_status(self) -> dict:
        """Get current service status."""
        return {
            "is_running": self.is_running,
            "current_scenario": self.current_scenario,
            "flows_processed": self.flows_processed,
            "alerts_generated": self.alerts_generated,
            "scenario_index": self.scenario_index,
            "total_scenarios": len(self.scenarios)
        }


# Global instance
continuous_traffic_service = ContinuousTrafficService()


# Auto-start function to be called from main.py
def start_continuous_traffic():
    """Start continuous traffic generation (called on backend startup)."""
    continuous_traffic_service.start()


def stop_continuous_traffic():
    """Stop continuous traffic generation (called on backend shutdown)."""
    continuous_traffic_service.stop()

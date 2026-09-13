"""
Network traffic simulator for SentinelOneWay.

IMPORTANT: This generates SYNTHETIC flow-level metadata for defensive
cybersecurity testing and development. It does NOT send real network
packets or perform actual attacks. All data is simulated for testing
detection algorithms in a safe, controlled environment.
"""
import random
import string
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any
import ipaddress

from .flow_record import FlowRecord


class TrafficGenerator:
    """
    Generates synthetic network flow records for testing.

    Creates realistic but fake network flow metadata to test
    threat detection algorithms without real network activity.
    """

    def __init__(self):
        # Internal networks (RFC 1918 private addresses)
        self.internal_networks = [
            ipaddress.IPv4Network('10.0.0.0/8'),
            ipaddress.IPv4Network('172.16.0.0/12'),
            ipaddress.IPv4Network('192.168.0.0/16')
        ]

        # Common internal IPs for simulation
        self.internal_ips = [
            '10.0.1.15',   # web-server-01
            '10.0.2.50',   # db-primary
            '10.0.3.142',  # workstation-42
            '10.0.4.88',   # dns-resolver
            '10.0.5.201',  # file-server
            '10.0.6.30',   # workstation-30
            '10.0.7.100',  # firewall-01
            '10.0.8.250',  # backup-server
        ]

        # External IPs for simulation
        self.external_ips = [
            '203.0.113.45',    # Test-Net-3
            '198.51.100.88',   # Test-Net-2
            '192.0.2.100',     # Test-Net-1
            '185.220.101.5',   # Simulated C2
            '8.8.8.8',         # Public DNS
            '1.1.1.1',         # Public DNS
        ]

        self.flow_counter = 0

    def _generate_flow_id(self) -> str:
        """Generate unique flow ID."""
        self.flow_counter += 1
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"FLW-{timestamp}{self.flow_counter:04d}"

    def _random_internal_ip(self) -> str:
        """Get random internal IP."""
        return random.choice(self.internal_ips)

    def _random_external_ip(self) -> str:
        """Get random external IP."""
        return random.choice(self.external_ips)

    def _random_ephemeral_port(self) -> int:
        """Generate random ephemeral port (49152-65535)."""
        return random.randint(49152, 65535)

    def _random_dns_query(self, length: int = 20, entropy_high: bool = False) -> str:
        """
        Generate synthetic DNS query.

        Args:
            length: Query string length
            entropy_high: If True, generate high-entropy (random) domain
        """
        if entropy_high:
            # High entropy - looks like DGA or tunneling
            subdomain = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        else:
            # Normal looking domain
            words = ['api', 'www', 'mail', 'cdn', 'app', 'web', 'secure', 'portal']
            subdomain = random.choice(words)

        domains = ['example.com', 'test.org', 'demo.net']
        return f"{subdomain}.{random.choice(domains)}"

    def _random_tls_fingerprint(self) -> str:
        """Generate synthetic TLS fingerprint."""
        random_bytes = ''.join(random.choices(string.hexdigits.lower(), k=32))
        return hashlib.sha256(random_bytes.encode()).hexdigest()[:16]

    def generate_normal_traffic(self, intensity: float = 0.5) -> List[FlowRecord]:
        """
        Generate normal benign traffic flows.

        Characteristics:
        - Moderate packet rates
        - Normal SYN/ACK ratios (~1:1)
        - Varied destinations
        - Typical protocol distribution
        """
        flows = []
        now = datetime.now()

        count = int(10 * intensity) if intensity else 10

        for i in range(count):
            timestamp = now - timedelta(seconds=random.randint(0, 300))
            protocol = random.choices(['TCP', 'UDP', 'ICMP'], weights=[70, 25, 5])[0]

            # Normal traffic characteristics
            packet_count = random.randint(10, 500)
            byte_count = packet_count * random.randint(500, 1500)
            duration = random.uniform(0.1, 60.0)

            if protocol == 'TCP':
                syn_count = random.randint(1, 5)
                ack_count = syn_count + random.randint(-1, 1)  # Roughly equal
            else:
                syn_count = 0
                ack_count = 0

            # Balanced bidirectional traffic
            outbound_bytes = int(byte_count * random.uniform(0.4, 0.6))
            inbound_bytes = byte_count - outbound_bytes

            flow = FlowRecord(
                timestamp=timestamp,
                flow_id=self._generate_flow_id(),
                src_ip=self._random_internal_ip(),
                dst_ip=self._random_external_ip(),
                src_port=self._random_ephemeral_port(),
                dst_port=random.choice([80, 443, 53, 22, 25]),
                protocol=protocol,
                packet_count=packet_count,
                byte_count=byte_count,
                duration=duration,
                syn_count=syn_count,
                ack_count=ack_count,
                inbound_bytes=inbound_bytes,
                outbound_bytes=outbound_bytes,
                dns_query=self._random_dns_query() if random.random() < 0.3 else None,
                tls_fingerprint=self._random_tls_fingerprint() if protocol == 'TCP' else None
            )
            flows.append(flow)

        return flows

    def generate_syn_flood(self, intensity: float = 0.5) -> List[FlowRecord]:
        """
        Generate SYN flood attack simulation.

        Characteristics:
        - Very high SYN count
        - Few or no ACK responses
        - High source IP diversity
        - High packet rate to single target
        - Short duration per flow
        """
        flows = []
        now = datetime.now()
        target_ip = self._random_internal_ip()
        target_port = 443

        # Number of flows based on intensity
        flow_count = int(100 * intensity)

        for i in range(flow_count):
            timestamp = now - timedelta(milliseconds=random.randint(0, 1000))

            # Generate random source IPs (spoofed in real attack)
            src_network = random.randint(1, 254)
            src_host = random.randint(1, 254)
            src_ip = f"203.0.{src_network}.{src_host}"

            # SYN flood characteristics
            syn_count = random.randint(50, 200)
            ack_count = random.randint(0, 5)  # Very few ACKs
            packet_count = syn_count + ack_count
            byte_count = packet_count * 60  # Small packets (just headers)
            duration = random.uniform(0.01, 0.5)  # Very short

            flow = FlowRecord(
                timestamp=timestamp,
                flow_id=self._generate_flow_id(),
                src_ip=src_ip,
                dst_ip=target_ip,
                src_port=self._random_ephemeral_port(),
                dst_port=target_port,
                protocol='TCP',
                packet_count=packet_count,
                byte_count=byte_count,
                duration=duration,
                syn_count=syn_count,
                ack_count=ack_count,
                inbound_bytes=ack_count * 60,
                outbound_bytes=syn_count * 60,
                dns_query=None,
                tls_fingerprint=None
            )
            flows.append(flow)

        return flows

    def generate_port_scan(self, intensity: float = 0.5) -> List[FlowRecord]:
        """
        Generate port scan simulation.

        Characteristics:
        - Single source IP
        - Many destination ports
        - Many short-duration flows
        - Low packet count per flow
        - Sequential or random port patterns
        """
        flows = []
        now = datetime.now()
        scanner_ip = self._random_external_ip()
        target_ip = self._random_internal_ip()

        # Number of ports to scan
        port_count = int(1000 * intensity)
        start_port = random.randint(1, 30000)

        for i in range(port_count):
            timestamp = now - timedelta(milliseconds=i * 10)  # Sequential timing
            dst_port = (start_port + i) % 65535 + 1

            # Port scan characteristics
            packet_count = random.randint(1, 3)  # Very few packets
            byte_count = packet_count * 60
            duration = random.uniform(0.001, 0.1)  # Very short
            syn_count = 1
            ack_count = 1 if random.random() < 0.1 else 0  # Rarely successful

            flow = FlowRecord(
                timestamp=timestamp,
                flow_id=self._generate_flow_id(),
                src_ip=scanner_ip,
                dst_ip=target_ip,
                src_port=self._random_ephemeral_port(),
                dst_port=dst_port,
                protocol='TCP',
                packet_count=packet_count,
                byte_count=byte_count,
                duration=duration,
                syn_count=syn_count,
                ack_count=ack_count,
                inbound_bytes=ack_count * 60,
                outbound_bytes=syn_count * 60,
                dns_query=None,
                tls_fingerprint=None
            )
            flows.append(flow)

        return flows

    def generate_c2_beacon(self, intensity: float = 0.5) -> List[FlowRecord]:
        """
        Generate C2 beacon simulation.

        Characteristics:
        - Same source/destination pair
        - Regular interval timing (120 seconds ±jitter)
        - Consistent small payload size
        - Long-duration pattern
        """
        flows = []
        now = datetime.now()
        infected_host = self._random_internal_ip()
        c2_server = '185.220.101.5'
        beacon_interval = 120  # seconds
        jitter = 2  # seconds

        # Number of beacons based on intensity
        beacon_count = int(20 * intensity)

        for i in range(beacon_count):
            # Regular interval with small jitter
            time_offset = i * beacon_interval + random.uniform(-jitter, jitter)
            timestamp = now - timedelta(seconds=time_offset)

            # C2 beacon characteristics
            packet_count = random.randint(5, 15)  # Small, consistent
            byte_count = random.randint(500, 2000)  # Small payload
            duration = random.uniform(0.5, 2.0)
            syn_count = 1
            ack_count = 1

            # Slightly more outbound (sending data)
            outbound_bytes = int(byte_count * random.uniform(0.55, 0.65))
            inbound_bytes = byte_count - outbound_bytes

            flow = FlowRecord(
                timestamp=timestamp,
                flow_id=self._generate_flow_id(),
                src_ip=infected_host,
                dst_ip=c2_server,
                src_port=self._random_ephemeral_port(),
                dst_port=8080,
                protocol='TCP',
                packet_count=packet_count,
                byte_count=byte_count,
                duration=duration,
                syn_count=syn_count,
                ack_count=ack_count,
                inbound_bytes=inbound_bytes,
                outbound_bytes=outbound_bytes,
                dns_query=None,
                tls_fingerprint=self._random_tls_fingerprint()
            )
            flows.append(flow)

        return flows

    def generate_dns_tunnel(self, intensity: float = 0.5) -> List[FlowRecord]:
        """
        Generate DNS tunneling simulation.

        Characteristics:
        - Unusually long DNS query names
        - High entropy in subdomain names
        - High query frequency
        - Consistent source
        """
        flows = []
        now = datetime.now()
        source_ip = self._random_internal_ip()
        dns_server = '8.8.8.8'

        # Number of queries based on intensity
        query_count = int(50 * intensity)

        for i in range(query_count):
            timestamp = now - timedelta(seconds=random.randint(0, 300))

            # DNS tunnel characteristics
            query_length = random.randint(40, 63)  # Long, near max
            dns_query = self._random_dns_query(length=query_length, entropy_high=True)

            packet_count = random.randint(1, 3)
            byte_count = len(dns_query) + random.randint(100, 200)
            duration = random.uniform(0.05, 0.5)

            flow = FlowRecord(
                timestamp=timestamp,
                flow_id=self._generate_flow_id(),
                src_ip=source_ip,
                dst_ip=dns_server,
                src_port=self._random_ephemeral_port(),
                dst_port=53,
                protocol='UDP',
                packet_count=packet_count,
                byte_count=byte_count,
                duration=duration,
                syn_count=0,
                ack_count=0,
                inbound_bytes=int(byte_count * 0.3),
                outbound_bytes=int(byte_count * 0.7),
                dns_query=dns_query,
                tls_fingerprint=None
            )
            flows.append(flow)

        return flows

    def generate_data_exfiltration(self, intensity: float = 0.5) -> List[FlowRecord]:
        """
        Generate data exfiltration simulation.

        Characteristics:
        - Unusually high outbound/inbound byte ratio
        - Large data transfer
        - Often to unusual destinations
        - Encrypted (HTTPS)
        """
        flows = []
        now = datetime.now()
        source_ip = self._random_internal_ip()
        destination_ip = self._random_external_ip()

        # Number of flows based on intensity
        flow_count = int(5 * intensity)

        for i in range(flow_count):
            timestamp = now - timedelta(seconds=random.randint(0, 600))

            # Data exfiltration characteristics
            outbound_bytes = random.randint(10_000_000, 100_000_000)  # 10-100 MB
            inbound_bytes = random.randint(5000, 50000)  # Very small inbound
            byte_count = outbound_bytes + inbound_bytes

            packet_count = int(byte_count / 1400)  # Estimate packets
            duration = random.uniform(30.0, 300.0)  # Long duration

            syn_count = 1
            ack_count = 1

            flow = FlowRecord(
                timestamp=timestamp,
                flow_id=self._generate_flow_id(),
                src_ip=source_ip,
                dst_ip=destination_ip,
                src_port=self._random_ephemeral_port(),
                dst_port=443,
                protocol='TCP',
                packet_count=packet_count,
                byte_count=byte_count,
                duration=duration,
                syn_count=syn_count,
                ack_count=ack_count,
                inbound_bytes=inbound_bytes,
                outbound_bytes=outbound_bytes,
                dns_query=None,
                tls_fingerprint=self._random_tls_fingerprint()
            )
            flows.append(flow)

        return flows

    def generate_traffic(self, scenario: str, intensity: float = 0.5) -> List[FlowRecord]:
        """
        Generate traffic flows for specified scenario.

        Args:
            scenario: Type of traffic (normal, syn_flood, port_scan, etc.)
            intensity: 0.0 to 1.0, controls volume/severity

        Returns:
            List of synthetic flow records
        """
        scenario = scenario.lower()
        intensity = max(0.0, min(1.0, intensity))  # Clamp to [0, 1]

        generators = {
            'normal': lambda i: self.generate_normal_traffic(i),
            'syn_flood': self.generate_syn_flood,
            'port_scan': self.generate_port_scan,
            'c2_beacon': self.generate_c2_beacon,
            'dns_tunnel': self.generate_dns_tunnel,
            'data_exfiltration': self.generate_data_exfiltration,
        }

        generator = generators.get(scenario)
        if not generator:
            raise ValueError(f"Unknown scenario: {scenario}. Valid: {list(generators.keys())}")

        return generator(intensity)
